from flask import render_template, jsonify, request
import pandas as pd
from . import main_bp
from sqlalchemy import select
from myapp.models import RealEstateTransaction
from myapp import db

@main_bp.route('/', methods=['GET'])
def index():
    return render_template('main/index.html')

@main_bp.route('/', methods=['POST'])
def district():
    # DataFrame으로 변환
    stmt = select(RealEstateTransaction)
    df_ret = pd.read_sql(stmt, db.session.connection())
    district_df = df_ret

    # 각 거래 평단가 계산
    def calc_price_per_sqm(df):
        df = df.copy()
        df['price_per_sqm'] = (df['amount'] * 10000) / df['building_area']
        return df

    # 지역구 별 년도의 평단가 평균
    def calc_yearly_avg_price_by_district(df):
        return (
            df
            .groupby(['district_name', 'reception_year'])
            .agg(avg_price_per_sqm=('price_per_sqm', 'mean'))
            .reset_index()
            .sort_values(['district_name', 'reception_year'])
        )

    # 전체 상승률 계산
    def calc_total_change_rate_by_district(df):
        total_rate = (
            df
            .groupby('district_name')['avg_price_per_sqm']
            .agg(first='first', last='last')
            .reset_index()
        )

        total_rate['total_change_rate'] = (
            (total_rate['last'] - total_rate['first'])
            / total_rate['first'] * 100
        ).round(2)

        return total_rate

    # 순위 출력
    def apply_total_change_rank(df):
        df = df.copy()
        df['rank'] = (
            df['total_change_rate']
            .rank(method='dense', ascending=False)
            .astype(int)
        )
        return df.sort_values(['rank', 'district_name'])

    # 포맷팅 round(0)으로 소수점 첫 째 자리에서 반올림 | price_per_sqm_format 컬럼 생성
    def format_price_column(df):
        df = df.copy()
        df['price_per_sqm_format'] = (
            df['last']
            .round(0)
            .map(lambda x: f"{int(x):,}")
        )
        return df

    avg_df = calc_price_per_sqm(district_df)

    yoy_avg_df = calc_yearly_avg_price_by_district(avg_df)

    district_rate_df = calc_total_change_rate_by_district(yoy_avg_df)

    rank_df = apply_total_change_rank(district_rate_df)

    result = format_price_column(rank_df)

    result = result.to_dict(orient="records")

    return jsonify(result)
