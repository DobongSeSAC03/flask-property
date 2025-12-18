from flask import jsonify, request, render_template
import pandas as pd
from sqlalchemy import select, and_
from . import query_bp
from myapp.models import RealEstateTransaction
from myapp import db


@query_bp.route("/", methods=["GET"])
def query():
    return render_template("query.html")


@query_bp.route("/select", methods=["POST"])
def query_select():
    data = request.get_json()
    input_district_name = data.get('district')
    input_legal_dong_name = data.get('dong')
    input_max_budget = data.get('max_budget')


    stmt = select(RealEstateTransaction)
    df_ret = pd.read_sql(stmt, db.session.connection())

    """
    통합 API
    POST /predict/location

    JSON 예시:
    {
      "district": "도봉구",     # 필수(구)
      "dong": "방학동",         # 선택(법정동) - 없으면 분석은 구 단위로, 예산필터는 dongs 목록만 반환
      "budget": 10000          # 선택(만원) 기본 10000
    }

    반환:
    {
      "analysis_result": {...},        # 평단가/상승률/랭킹 계산 결과
      "budget_filter_result": {...}    # 예산/구/동 필터링 결과
    }
    """

    # -----------------------------
    # 0) 입력(JSON) = 콘솔 input() 대체
    # -----------------------------

    input_district_name = (data.get("district") or "").strip()
    input_legal_dong_name = data.get("dong")
    input_legal_dong_name = str(input_legal_dong_name).strip() if input_legal_dong_name is not None else None

    budget_raw = data.get("budget", 10000)
    try:
        target_budget = int(budget_raw)
    except (TypeError, ValueError):
        target_budget = 10000

    # 콘솔 변수명에 매핑
    target_gu = input_district_name
    target_dong = input_legal_dong_name

    if not target_gu:
        return jsonify({"error": "district(구) 값이 필요합니다."}), 400

    # -----------------------------
    # 1) DB -> DataFrame
    # -----------------------------
    stmt = select(RealEstateTransaction)
    df_ret = pd.read_sql(stmt, db.session.connection())

    # 필수 컬럼 체크(최소)
    base_required = {"district_name", "legal_dong_name", "amount"}
    if not base_required.issubset(df_ret.columns):
        missing = sorted(list(base_required - set(df_ret.columns)))
        return jsonify({"error": f"필수 컬럼 누락: {missing}"}), 500

    # 공백/타입 정리
    df_ret = df_ret.copy()
    df_ret["district_name"] = df_ret["district_name"].astype(str).str.strip()
    df_ret["legal_dong_name"] = df_ret["legal_dong_name"].astype(str).str.strip()
    df_ret["building_name"] = df_ret["building_name"].astype(str).str.strip()
    df_ret["building_use"] = df_ret["building_use"].astype(str).str.strip()

    df_ret["amount"] = pd.to_numeric(df_ret["amount"], errors="coerce")
    df_ret["building_area"] = pd.to_numeric(df_ret["building_area"], errors="coerce")
    df_ret["construction_year"] = pd.to_numeric(df_ret["construction_year"], errors="coerce")

    # =========================================================
    # A) 분석 파트: 평단가/연도별 평균/상승률/전체상승률/랭킹
    # =========================================================

    def filter_by_district(df, district_name):
        return df[df["district_name"] == district_name].copy()

    def calc_price_per_sqm(df):
        df = df.copy()
        # 필요한 컬럼 체크
        if "building_area" not in df.columns:
            raise KeyError("building_area")
        df["building_area"] = pd.to_numeric(df["building_area"], errors="coerce")

        # 0/결측 방어
        df = df[df["building_area"].notna() & (df["building_area"] > 0)]
        df = df[df["amount"].notna()]

        df["price_per_sqm"] = (df["amount"] * 10000) / df["building_area"]
        return df

    def calc_yearly_avg_price(df):
        df = df.copy()
        if "reception_year" not in df.columns:
            raise KeyError("reception_year")

        return (
            df.groupby(["reception_year", "district_name", "legal_dong_name"])
              .agg(
                  avg_price_per_sqm=("price_per_sqm", "mean"),
                  transaction_count=("price_per_sqm", "count"),
              )
              .reset_index()
              .sort_values(["legal_dong_name", "district_name", "reception_year"])
        )

    def format_price_column(df):
        df = df.copy()
        df["price_per_sqm_format"] = (
            df["avg_price_per_sqm"]
            .round(0)
            .map(lambda x: f"{int(x):,}" if pd.notnull(x) else None)
        )
        return df

    def calc_yoy_change_rate(df):
        df = df.copy()
        df["yoy_change_rate"] = (
            df.groupby(["district_name", "legal_dong_name"])["avg_price_per_sqm"]
              .pct_change() * 100
        ).round(2)
        return df

    def calc_total_change_rate(df):
        df = df.copy()
        total_rate = (
            df.groupby(["district_name", "legal_dong_name"])["avg_price_per_sqm"]
              .agg(["first", "last"])
              .reset_index()
        )

        total_rate["total_change_rate"] = (
            (total_rate["last"] - total_rate["first"]) / total_rate["first"] * 100
        ).round(2)

        return df.merge(
            total_rate[["district_name", "legal_dong_name", "total_change_rate"]],
            on=["district_name", "legal_dong_name"],
            how="left",
        )

    def apply_change_rank(df):
        df = df.copy()
        # total_change_rate 결측 가능성 -> Int64로
        df["change_rank"] = (
            df.groupby("district_name")["total_change_rate"]
              .rank(method="dense", ascending=False)
              .astype("Int64")
        )
        return df

    try:
        district_df = filter_by_district(df_ret, input_district_name)
        if district_df.empty:
            return jsonify({"error": f"'{input_district_name}' 데이터 없음"}), 404

        district_df = calc_price_per_sqm(district_df)
        if district_df.empty:
            # building_area/amount 문제 등
            analysis_result = {
                "filters": {"district": input_district_name, "dong": input_legal_dong_name},
                "count": 0,
                "items": [],
                "message": "평단가 계산 가능한 데이터가 없습니다(building_area/amount 확인)."
            }
        else:
            yearly_avg_price = calc_yearly_avg_price(district_df)
            yearly_avg_price = format_price_column(yearly_avg_price)
            yearly_avg_price = calc_yoy_change_rate(yearly_avg_price)
            yearly_avg_price = calc_total_change_rate(yearly_avg_price)
            yearly_avg_price = apply_change_rank(yearly_avg_price)

            # 랭킹 정렬
            yearly_avg_price = yearly_avg_price.sort_values(by="change_rank", ascending=True)

            # dong 필터(선택)
            if input_legal_dong_name is not None:
                yearly_avg_price = yearly_avg_price[
                    yearly_avg_price["legal_dong_name"] == input_legal_dong_name
                ]

            yearly_avg_price["yoy_change_rate"] = yearly_avg_price["yoy_change_rate"].fillna("-")

            analysis_result = {
                "filters": {"district": input_district_name, "dong": input_legal_dong_name},
                "count": int(len(yearly_avg_price)),
                "items": yearly_avg_price.where(pd.notnull(yearly_avg_price), None).to_dict(orient="records"),
            }

    except KeyError as e:
        # reception_year/building_area 없을 때
        analysis_result = {
            "filters": {"district": input_district_name, "dong": input_legal_dong_name},
            "count": 0,
            "items": [],
            "error": f"분석에 필요한 컬럼이 없습니다: {str(e)}"
        }

    # =========================================================
    # B) 예산 필터 파트: (네 콘솔 코드 로직을 API로 변환)
    # =========================================================

    # 2. 해당 구의 데이터 1차 필터링 및 동 리스트 추출
    df_gu = df_ret[df_ret["district_name"] == target_gu].copy()

    if df_gu.empty:
        # 콘솔 while 재입력 대신 에러 반환
        budget_filter_result = {
            "error": f"'{target_gu}'에 해당하는 데이터가 없습니다. 구 이름을 확인해 주세요.",
            "gu": target_gu,
            "budget": target_budget
        }
        df_fields = pd.DataFrame(columns=[
            "district_name",
            "legal_dong_name",
            "building_name",
            "amount",
            "building_area",
            "construction_year",
            "building_use"
        ])
    else:
        dong_list = sorted(df_gu["legal_dong_name"].dropna().unique().tolist())

        # 콘솔에서는 동 목록 출력 후 input 받음 -> API에서는 dong이 없으면 목록만 줌
        if not target_dong:
            budget_filter_result = {
                "gu": target_gu,
                "budget": target_budget,
                "dongs": dong_list,
                "message": "dong을 선택해서 다시 요청하세요."
            }
            df_fields = pd.DataFrame(columns=[
                "district_name",
                "legal_dong_name",
                "building_name",
                "amount",
                "building_area",
                "construction_year",
                "building_use"
            ])
        else:
            # dong 검사
            if target_dong not in dong_list:
                budget_filter_result = {
                    "error": f"'{target_dong}' 동 없음",
                    "gu": target_gu,
                    "budget": target_budget,
                    "dongs": dong_list
                }
                df_fields = pd.DataFrame(columns=[
                    "district_name",
                    "legal_dong_name",
                    "building_name",
                    "amount",
                    "building_area",
                    "construction_year",
                    "building_use"
                ])
            else:
                # 3. 최종 필터링: 구 + 동 + 예산(amount) 조건 적용
                condition = (
                    (df_ret["district_name"] == target_gu) &
                    (df_ret["legal_dong_name"] == target_dong) &
                    (df_ret["amount"].notna()) &
                    (df_ret["amount"] <= target_budget)
                )

                df_fields = df_ret.loc[condition, [
                    "district_name",
                    "legal_dong_name",
                    "building_name",
                    "amount",
                    "building_area",
                    "construction_year",
                    "building_use"
                ]].copy()

    items = df_fields.where(pd.notnull(df_fields), None).to_dict(orient="records")

    return jsonify({
        "filters": {"gu": target_gu, "dong": target_dong, "budget": target_budget},
        "count": len(items),
        "items": items
    }), 200
