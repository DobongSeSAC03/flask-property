from flask import jsonify, request
import pandas as pd
from . import parking_bp
from sqlalchemy import select
from myapp.models import PublicParking
from myapp import db

@parking_bp.route('', methods=['POST'])
def parking():
    data = request.get_json()
    input_district_name = data.get('district')
    input_dong_name = data.get('dong')
    # DataFrame으로 변환
    stmt = select(PublicParking)
    df_pp = pd.read_sql(stmt, db.session.connection())

    print(f"총 레코드 수: {len(df_pp)}")

    selected_cols = ['parking_name', 'address', 'parking_type_name','total_spaces','current_parking','basic_rate'] #필요한 컬럼을 가지고 데이터 프레임 생성
    parking_df = df_pp[selected_cols]

    parking_nw = parking_df[parking_df['parking_type_name'].str.contains('노외 주차장')] 
    parking_nw.sort_values(by='total_spaces', ascending=False).reset_index(drop=True)        # 주차장(노외) 통합 데이터 총 주차면수 순서대로       

    parking_nss = parking_df[parking_df['parking_type_name'].str.contains('노상 주차장')] # 노상주차장은 코드 카운팅 해서 총 주차면수 정해야함

    parking_nss['address_count'] = parking_nss.groupby('address')['address'].transform('count') # 중복되는 address를 count하여 새로운 컬럼을 생성 

    parking_nss['total_spaces'] = parking_nss['address_count'] #위 새롭게 생성된 컬럼을 total_spaces로 바꿔줌
    parking_nss.drop(columns='address_count',inplace=True)
    parking_ns = parking_nss.copy()

    parking_ns.drop_duplicates(subset=['address'], inplace=True)

    parking_ns = parking_ns.sort_values(by='total_spaces', ascending=False).reset_index(drop=True)  # 주차장(노상) 통합 데이터 총 주차면수 순서대로

    parking = pd.concat([parking_nw, parking_ns], ignore_index=True)
    parking = parking.sort_values(by='total_spaces', ascending=False).reset_index(drop=True)    # 주차장(노외, 노상) 통합 데이터 총 주차면수 순서대로

    parking['Area_Gu'] = parking['address'].str.split().str[0]
    parking['Area_Dong'] = parking['address'].str.split().str[1]        # address 주소를 split해서 Gu, Dong별로 컬럼을 생성해줌

    parking['available_spaces'] = (parking['total_spaces'] - parking['current_parking'])    # 총 주차면수 - 주차차량수 = 주차가능한 공간을 컬럼으로 생성 
    parking['available_spaces'] = parking['available_spaces'].astype(int)                   # 실수형 컬럼을 정수형으로 변환함

    def filter_by_district(df, input_district_name):
        return df[df['Area_Gu']==input_district_name].copy()

    result = filter_by_district(parking, input_district_name)
    if input_dong_name is not None:
        result = result[result['Area_Dong'] == input_dong_name]
    
    result=result.to_dict(orient='records')

    return jsonify(result)

