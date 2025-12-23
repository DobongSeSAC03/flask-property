from flask import render_template, jsonify, request
import pandas as pd
from . import predict_bp
from sqlalchemy import select, func, and_
from myapp.models import RealEstateTransaction
from myapp import db
@predict_bp.route('/', methods=['GET'])
def predict():
    return render_template('predict/predict.html')

@predict_bp.route('/location', methods=['POST'])
def predict_by_loaction():

    """
    리팩토링 목적: 
    - 메인 페이지, 예측 페이지에서 데이터 요청시
    - 원본 데이터 로드를 최대한 지양하고, 필요한 컬러만 로드해서 응답 시간을 개선 하는 것이 목표
    
    Before: total waiting for server response: 1.70s
    After: total waiting for server response: 0.24s
            (1.70 − 0.24) / 1.70 × 100 ≈ 85.9% 성능 개선
    """
    
    # silent=True 가 없으면 body 값이 비어있거나 JSON이 아니면 에러가 날 수 있어서 명시
    data = request.get_json(silent=True) or {}


    # input data 예시 "지역구" = 도봉구, "법정동" = 방학동 | "법정동" 데이터는 프론트로 부터 받지 않을 수도 있음.
    input_district_name = data.get('district')
    input_legal_dong_name = data.get('dong')
    input_building_use = data.get('building_type')
    input_amount = data.get('amount')
    
    # Task 1: 요청 값에 따라 필요한 컬럼만 선별해서 DataFame 로드
    # 함수 정의할 떄 None으로 초기화해도, 값은 덮어 씌워 지지 않음. 호출할 때 값을 넘기면 넘긴 값 그대로 초기화 됨.
    # But, 함수를 호출할때, fetch_yearly_avg_price_by_dong(district_name=None) 처럼 넘기면 값은 무조건 None으로 넘어옴
    def fetch_yearly_avg_price_by_dong(
        district_name=None,
        legal_dong_name=None,
        building_use=None,
        amount=None,
    ):
        conditions = [
            RealEstateTransaction.building_area.isnot(None),
            RealEstateTransaction.building_area > 0,
            RealEstateTransaction.amount.isnot(None),
        ]

        if amount is not None and str(amount).strip() != "":
            conditions.append(RealEstateTransaction.amount < int(amount))

        if building_use:
            conditions.append(RealEstateTransaction.building_use == building_use)

        if district_name:
            conditions.append(RealEstateTransaction.district_name == district_name)

        if legal_dong_name:
            conditions.append(RealEstateTransaction.legal_dong_name == legal_dong_name)

        # DB에서 컬럼들 선택적으로 가져오기 + 평단가 컬럼 "avg_price_per_sqm" 계산 및 생성
        stmt = (
            select(
                RealEstateTransaction.district_name,
                RealEstateTransaction.legal_dong_name,
                RealEstateTransaction.reception_year,
                func.avg(
                    (RealEstateTransaction.amount * 10000) / RealEstateTransaction.building_area
                ).label("avg_price_per_sqm"),
                func.count().label("transaction_count"),
            )
            .where(and_(*conditions))
            # 지역구 | 법정동 | 연도 별 그룹핑
            .group_by(
                RealEstateTransaction.district_name,
                RealEstateTransaction.legal_dong_name,
                RealEstateTransaction.reception_year,
            )
            # 지역구 | 법정동 | 연도 별 정렬
            .order_by(
                RealEstateTransaction.legal_dong_name,
                RealEstateTransaction.district_name,
                RealEstateTransaction.reception_year,
            )
        )

        # 데이터 꺼내옴
        rows = db.session.execute(stmt).fetchall()

        # DataFrame으로 변환 후 반환
        return pd.DataFrame(
            rows,
            columns=[
                "district_name",
                "legal_dong_name",
                "reception_year",
                "avg_price_per_sqm",
                "transaction_count",
            ],
        )
    
    # Task 2: 받은 데이터 프레임에서 연도별 상승률 계산
    def calc_yoy_change_rate(df: pd.DataFrame):
        df = df.copy()
        df["yoy_change_rate"] = (
            df.groupby(["district_name", "legal_dong_name"])["avg_price_per_sqm"]
            .pct_change()
            .mul(100)
            .round(2)
        )
        return df
    
    # Task 3: 받은 데이터 프레임에서 전체 상승률 계산
    def calc_total_change_rate(df: pd.DataFrame):
        df = df.copy()
        # 평균 평단가를 이용해서 first는 2022년도 평단가 평균(시작 데이터가 거기라면) last는 2025년도 평단가 평균(끝 데이터가 거기라면)
        total_rate = (
            df.sort_values(["district_name", "legal_dong_name", "reception_year"])
            .groupby(["district_name", "legal_dong_name"])["avg_price_per_sqm"]
            .agg(["first", "last"])
            .reset_index()
        )
        # 위의 first, last를 이용해서 2022년 대비 2025년의 전체 상승률을 계산
        total_rate["total_change_rate"] = (
            (total_rate["last"] - total_rate["first"]) / total_rate["first"] * 100
        ).round(2)

        # merge 하는 이유: 프론트에서는 연도별 row를 그대로 받아야하니까, 전체 상승률을 다 붙여줌, total_rank를 연도별로 다 붙이는 이유와 동일, last도 merge하는 이유는 프론트에서 최근 평단가 데이터 필요해서 format 함수 쓰려면 필요함
        return df.merge(
            total_rate[["district_name", "legal_dong_name", "total_change_rate", "last"]],
            on=["district_name", "legal_dong_name"],
            how="left",
        )
    
    # Task 4: 전체 랭킹 붙이기 및 랭킹으로 정렬
    def apply_change_rank(df: pd.DataFrame):
        df = df.copy()
        df["change_rank"] = (
            df["total_change_rate"]
            .rank(method="dense", ascending=False)
            .astype(int)
        )
        return df
    # Task 5: last 값 이용, 10000 단위에 대한 포맷팅
    def format_price_column(df: pd.DataFrame):
        df = df.copy()
        # merge에서 가져온 last(최신 avg_price_per_sqm) 기준으로 포맷 생성
        df["price_per_sqm_format"] = (
            df["last"]
            .round(0)
            .map(lambda x: f"{int(x):,}" if pd.notna(x) else "-")
        )
        return df

    df_yearly = fetch_yearly_avg_price_by_dong(
        district_name=input_district_name,
        legal_dong_name=input_legal_dong_name,
        building_use=input_building_use,
        amount=input_amount,
    )

    if df_yearly.empty:
        return jsonify([])

    df_yearly = calc_yoy_change_rate(df_yearly)
    df_yearly = calc_total_change_rate(df_yearly)
    df_yearly = apply_change_rank(df_yearly)

    # 기존과 동일하게 rank + year 정렬(프론트 가정 유지) | merge하면 행순서 보장 안됨
    df_yearly = df_yearly.sort_values(["change_rank", "reception_year"])

    df_yearly = format_price_column(df_yearly)

    # Presentation
    df_yearly["yoy_change_rate"] = df_yearly["yoy_change_rate"].fillna("-")
    df_yearly["total_change_rate"] = df_yearly["total_change_rate"].fillna("-")

    # last 컬럼은 내부 계산용이니 내려주기 싫으면 drop 가능(프론트 사용 안 함)
    df_yearly = df_yearly.drop(columns=["last"], errors="ignore")

    result = df_yearly.fillna("-").to_dict(orient="records")
    return jsonify(result)