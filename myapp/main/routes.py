from flask import render_template, jsonify, request
import pandas as pd
from . import main_bp
from sqlalchemy import select, func
from myapp.models import RealEstateTransaction
from myapp import db

@main_bp.route('/', methods=['GET'])
def index():
    return render_template('main/index.html')


@main_bp.route('/district', methods=['POST'])
def district():
    """
    리팩토링 목적:
    - DB에서 원본데이터를 로드하지 않고, 이미 정제된 컬럼만 가져오기
    - 프론트 지역구 막대 그래프 데이터 제공
    - 위의 리팩토링이 완료 되면, Spring의 Service, Repository 처럼 관심사 분리 리팩토링 예정
    """
    # Task 1: DB에서 연도별 지역구 평균 평단가 + 거래수 계산
    def fetch_yearly_avg_price_by_district():
        """
        DB에서 연도별 지역구 평균 평단가 + 거래 수 조회
        (원본 데이터 로드 없음)
        """
        stmt = (
            select(
                RealEstateTransaction.district_name,
                RealEstateTransaction.reception_year,
                func.avg(
                    (RealEstateTransaction.amount * 10000)
                    / RealEstateTransaction.building_area
                ).label("avg_price_per_sqm"),
                func.count().label("transaction_count")
            )
            .group_by(
                RealEstateTransaction.district_name,
                RealEstateTransaction.reception_year
            )
        )

        # execute:SQL문을 DB에 직접 실행해라.
        # fetchall: 실행된 SQL의 결과 행들을 한 번에 가져옴
        rows = db.session.execute(stmt).fetchall()
        return pd.DataFrame(
            rows,
            columns=[
                "district_name",
                "reception_year",
                "avg_price_per_sqm",
                "transaction_count",
            ],
        )

    # Task2: 지역구별 전체 상승률 계산 
    # 정렬 및 라벨링
    def calculate_total_change_rate_by_district(df_yearly: pd.DataFrame):
        """
        지역구별 최초 연도 대비 최종 연도 상승률 계산
        """
        total_rate_df = (
            df_yearly
            .sort_values(["district_name", "reception_year"])
            .groupby("district_name")
            .agg(
                first=("avg_price_per_sqm", "first"),
                last=("avg_price_per_sqm", "last"),
                transaction_count=("transaction_count", "sum"),
            )
            .reset_index()
        )

        total_rate_df["total_change_rate"] = (
            (total_rate_df["last"] - total_rate_df["first"])
            / total_rate_df["first"] * 100
        ).round(2)

        return total_rate_df

    # Task3: 랭킹 계산
    def apply_total_change_rank(df: pd.DataFrame):
        """
        상승률 기준 dense rank 적용
        """
        df = df.copy()
        df["rank"] = (
            df["total_change_rate"]
            .rank(method="dense", ascending=False)
            .astype(int)
        )
        # 랭킹으로 정렬
        return df.sort_values(["rank", "district_name"])

    # Task4: 포맷 컬럼
    # 포맷팅 round(0)으로 소수점 첫 째 자리에서 반올림 | price_per_sqm_format 컬럼 생성
    def format_price_columns(df: pd.DataFrame):
        """
        프론트 출력용 평단가 포맷 컬럼 생성
        """
        df = df.copy()
        df["price_per_sqm_format"] = (
            df["last"]
            .round(0)
            .map(lambda x: f"{int(x):,}")
        )
        return df

    # 1️⃣ Repository
    df_yearly = fetch_yearly_avg_price_by_district()

    # 2️⃣ Service
    total_rate_df = calculate_total_change_rate_by_district(df_yearly)
    total_rate_df = apply_total_change_rank(total_rate_df)

    # 3️⃣ Presentation
    total_rate_df = format_price_columns(total_rate_df)

    result = (
        total_rate_df
        .fillna("-")
        .to_dict(orient="records")
    )

    return jsonify(result)

# 건물유형 연도별 매매가 상승률 추이
@main_bp.route('/building', methods=['POST'])
def building():
    # DataFrame으로 변환
    stmt = select(RealEstateTransaction)
    df_ret = pd.read_sql(stmt, db.session.connection())
    
    # 전체 구 | 평단가 계산 | 건물 가격 단위(만원) | 건물 면적 단위 (m^2) | 모든 건물의 평균 단가 개발 계산 | price_per_sqm 컬럼 생성
    def calc_price_per_sqm(df):
        df = df.copy()
        df['price_per_sqm'] = (
            df['amount'] * 10000
        ) / df['building_area']
        return df

    def calc_yearly_avg_price_by_building(df):
        return (
            df
            .groupby(['building_use', 'reception_year'])
            .agg(
                avg_price_per_sqm=('price_per_sqm', 'mean'),
                transactions_counts=('price_per_sqm', 'count')
            )
            .reset_index()
            .sort_values(['building_use', 'reception_year'])
        )

    def calc_yoy_change_rate_by_building(df):
        df = df.copy()

        df['yoy_change_rate'] = (
            df
            .groupby('building_use')['avg_price_per_sqm']
            .pct_change()
            .mul(100)
            .round(2)
        )

        return df

    avg_df = calc_price_per_sqm(df_ret)
    building_df = calc_yearly_avg_price_by_building(avg_df)
    result = calc_yoy_change_rate_by_building(building_df)

    result.fillna('-', inplace=True)
    result = result.to_dict(orient="records")

    return jsonify(result)