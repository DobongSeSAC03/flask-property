from flask import render_template, jsonify, request
import pandas as pd
from . import query_bp
from sqlalchemy import select, and_
from myapp.models import RealEstateTransaction
from myapp import db

@query_bp.route('/', methods=['GET'])
def query():
    return render_template('query/query.html')

@query_bp.route('/search', methods=['POST'])
def search():
    """
    리팩토링 목적: 
    - 조회 페이지에서 데이터 요청시
    - 원본 데이터 로드를 최대한 지양하고, 필요한 컬러만 로드해서 응답 시간을 개선 하는 것이 목표
    
    Before: total waiting for server response: 6.28s
    After: total waiting for server response: 0.08s
            (6.28 − 0.08) / 6.28 × 100 ≈ 98.7% 성능 개선
    """
    data = request.get_json(silent=True) or {}

    #input 데이터 처리
    input_district_name = data.get('district')
    input_legal_dong_name = data.get('dong')
    input_building_use = data.get('building_type')
    input_amount = data.get('amount')

    # amount 방어적 변환 (문자/숫자 모두 대응)
    if input_amount is not None:
        try:
            input_amount = int(input_amount)
        except (TypeError, ValueError):
            input_amount = None

    # Task 1: 필요 컬럼만 DB에서 select
    def build_select_stmt():
        return select(
            RealEstateTransaction.district_name,
            RealEstateTransaction.legal_dong_name,
            RealEstateTransaction.building_name,
            RealEstateTransaction.building_area,
            RealEstateTransaction.amount,
            RealEstateTransaction.construction_year,
            RealEstateTransaction.building_use,
        )

    # Task 2: Where 필터
    def apply_filters(stmt, district_name=None, legal_dong_name=None, building_use=None, amount=None):
        conditions = []

        if district_name:
            conditions.append(RealEstateTransaction.district_name == district_name)

        if legal_dong_name:
            conditions.append(RealEstateTransaction.legal_dong_name == legal_dong_name)

        if building_use:
            conditions.append(RealEstateTransaction.building_use == building_use)

        if amount is not None:
            conditions.append(RealEstateTransaction.amount <= amount)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        return stmt

    # Task 3: ORDER BY 입력값 기반 정렬
    # 지역구(district_name)를 받음에 상관없이, 결과를 "구 -> 동" 순서로 정렬
    # 구만 넣었을 때는 "구 내에서 동 정렬 "
    def apply_ordering(stmt):
        return stmt.order_by(
            RealEstateTransaction.district_name.asc(),
            RealEstateTransaction.legal_dong_name.asc(),
        )

    # Task 4: DB limit
    def fetch_rows(stmt, limit_size=1000):
        stmt = stmt.limit(limit_size)
        return db.session.execute(stmt).mappings().all()

    def to_response(rows):
        result = []
        for r in rows:
            item = dict(r)
            for k, v in item.items():
                if v is None:
                    item[k] = '-'
            result.append(item)
        return result
    
    stmt = build_select_stmt()

    stmt = apply_filters(
        stmt,
        district_name=input_district_name,
        legal_dong_name=input_legal_dong_name,
        building_use=input_building_use,
        amount=input_amount,
    )

    stmt = apply_ordering(stmt)
    rows = fetch_rows(stmt, limit_size=1000)
    result = to_response(rows)

    return jsonify(result)