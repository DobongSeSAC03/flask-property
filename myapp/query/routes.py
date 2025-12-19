from flask import render_template, jsonify, request
import pandas as pd
from . import query_bp
from sqlalchemy import select
from myapp.models import RealEstateTransaction
from myapp import db

@query_bp.route('/', methods=['GET'])
def query():
    return render_template('query/query.html')

@query_bp.route('search', methods=['POST'])
def search():
    data = request.get_json()

    #input 데이터 처리
    input_district_name = data.get('district')
    input_legal_dong_name = data.get('dong')
    input_building_use = data.get('building_type')
    input_amount = data.get('amount')
    
    #DataFrame으로 변환
    stmt = select(RealEstateTransaction)
    df_ret = pd.read_sql(stmt, db.session.connection())

    df_ret_filtered = df_ret.copy()
    if input_district_name:
        df_ret_filtered = df_ret_filtered[df_ret_filtered['district_name'] == input_district_name]
    if input_legal_dong_name:
        df_ret_filtered = df_ret_filtered[df_ret_filtered['legal_dong_name'] == input_legal_dong_name]
    if input_amount is not None:
        df_ret_filtered = df_ret_filtered[df_ret_filtered['amount'] <= input_amount]
    if input_building_use:
        df_ret_filtered = df_ret_filtered[df_ret_filtered['building_use'] == input_building_use]

    df_ret_filtered.fillna('-', inplace=True)

    result = df_ret_filtered.to_dict(orient="records")
    return jsonify(result)

