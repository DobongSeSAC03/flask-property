from flask import render_template, jsonify, request
import pandas as pd
from . import predict_bp
from sqlalchemy import select
from myapp.models import RealEstateTransaction
from myapp import db


@predict_bp.route('/', methods=['GET'])
def predict():
    return render_template('predict/predict.html')

@predict_bp.route('location', methods=['POST'])
def predict_by_loaction():
    # input data 예시 "지역구" = 도봉구, "법정동" = 방학동 | "법정동" 데이터는 프론트로 부터 받지 않을 수도 있음.
    data = request.get_json()
    input_district_name = data.get('district')
    input_legal_dong_name = data.get('dong')
    input_building_use = data.get('building_type')

    # SQLAlchemy를 사용하여 데이터 가져오기
    # transactions = RealEstateTransaction.query.limit(5).all()
    # print(f"가져온 거래 수: {len(transactions)}")

    # DataFrame으로 변환
    stmt = select(RealEstateTransaction)
    df_ret = pd.read_sql(stmt, db.session.connection())


    # 지역구 필터링
    def filter_by_district(df, district_name):
        return df[df['district_name'] == district_name].copy()


    # 전체 구 | 평단가 계산 | 건물 가격 단위(만원) | 건물 면적 단위 (m^2) | 모든 건물의 평균 단가 개발 계산 | price_per_sqm 컬럼 생성
    def calc_price_per_sqm(df):
        df = df.copy()
        df['price_per_sqm'] = (
            df['amount'] * 10000
        ) / df['building_area']
        return df


    # 법정동 연도별 평단가 평균 계산 | yearly_avg_price DataFrame 생성 | transaction_count, avg_price_per_sqm 컬럼 생성
    def calc_yearly_avg_price(df):
        df = df.copy()
        return (
            df
            .groupby(['reception_year', 'district_name', 'legal_dong_name'])
            .agg(
                avg_price_per_sqm=('price_per_sqm', 'mean'),
                transaction_count=('price_per_sqm', 'count')
            )
            .reset_index()
            .sort_values(['legal_dong_name', 'district_name', 'reception_year'])
        )


    # 포맷팅 round(0)으로 소수점 첫 째 자리에서 반올림 | price_per_sqm_format 컬럼 생성
    def format_price_column(df):
        df = df.copy()
        df['price_per_sqm_format'] = (
            df['avg_price_per_sqm']
            .round(0)
            .map(lambda x: f"{int(x):,}")
        )
        return df

    # 연도별 상승률 | yoy_change_rate 컬럼생성 | 앞 행(전년도)과의 평단가의 차이 %로 계산
    def calc_yoy_change_rate(df):
        df = df.copy()
        df['yoy_change_rate'] = (
            df
            .groupby(['district_name', 'legal_dong_name'])['avg_price_per_sqm']
            .pct_change() * 100
        ).round(2)
        return df

    # 전체 상승률 | 2025(데이터 마지막 년도)평단가 - 2022 년도(데이터 시작년도) 평단가의 차이 %로 계산
    def calc_total_change_rate(df):
        df = df.copy()

        total_rate = (
            df
            .groupby(['district_name', 'legal_dong_name'])['avg_price_per_sqm']
            .agg(['first', 'last'])
            .reset_index()
        )

        total_rate['total_change_rate'] = (
            (total_rate['last'] - total_rate['first'])
            / total_rate['first'] * 100
        ).round(2)

        return df.merge(
            total_rate[['district_name', 'legal_dong_name', 'total_change_rate']],
            on=['district_name', 'legal_dong_name'],
            how='left'
        )

    # 랭킹 계산
    def apply_change_rank(df):
        df = df.copy()
        df['change_rank'] = (
            df
            .groupby('district_name')['total_change_rate']
            .rank(method='dense'     #1, 2, 3 (중복 순위 허용, 다음 순위 건너뛰지 않음)
                , ascending=False) # 상승률 높은 게 1위
            .astype(int)
        )
        return df


    district_df = filter_by_district(df_ret, input_district_name)
    district_df = calc_price_per_sqm(district_df)

    yearly_avg_price = calc_yearly_avg_price(district_df)
    yearly_avg_price = format_price_column(yearly_avg_price)
    yearly_avg_price = calc_yoy_change_rate(yearly_avg_price)
    yearly_avg_price = calc_total_change_rate(yearly_avg_price)
    yearly_avg_price = apply_change_rank(yearly_avg_price)

    # 랭킹으로 정렬
    yearly_avg_price = yearly_avg_price.sort_values(
        by='change_rank',
        ascending=True   # 1위부터
    )

    if input_legal_dong_name is not None:
        yearly_avg_price = yearly_avg_price[
            yearly_avg_price['legal_dong_name'] == input_legal_dong_name
        ]

    yearly_avg_price['yoy_change_rate'].fillna('-', inplace=True)
    result = yearly_avg_price.to_dict()
    print(yearly_avg_price)

    return jsonify(result)
