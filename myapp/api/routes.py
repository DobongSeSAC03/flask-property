from flask import jsonify, render_template
from . import api_bp
from myapp.models import RealEstateTransaction, PublicParking, Api

@api_bp.route('/', methods=['GET','POST'])
def apis():
    apis = Api.query.all()
    return render_template('api/apis.html', apis=apis)

@api_bp.route('/real_estate_transactions', methods=['GET','POST'])
def get_real_estate_transactions():
    transactions = RealEstateTransaction.query.limit(100).all()
    return jsonify([{
        'ret_id': transaction.ret_id,
        'reception_year': transaction.reception_year,
        'district_code': transaction.district_code,
        'district_name': transaction.district_name,
        'legal_dong_code': transaction.legal_dong_code,
        'legal_dong_name': transaction.legal_dong_name,
        'jibun_type': transaction.jibun_type,
        'jibun_type_name': transaction.jibun_type_name,
        'main_number': transaction.main_number,
        'sub_number': transaction.sub_number,
        'building_name': transaction.building_name,
        'contract_date': transaction.contract_date,
        'amount': transaction.amount,
        'building_area': transaction.building_area,
        'land_area': transaction.land_area,
        'floor': transaction.floor,
        'right_type': transaction.right_type,
        'cancel_date': transaction.cancel_date,
        'construction_year': transaction.construction_year,
        'building_use': transaction.building_use,
        'declaration_type': transaction.declaration_type,
        'broker_district_name': transaction.broker_district_name
    } for transaction in transactions])

@api_bp.route('/public_parkings', methods=['GET','POST'])
def get_public_parkings():
    parkings = PublicParking.query.limit(100).all()
    return jsonify([{
        'pp_id': parking.pp_id,
        'parking_code': parking.parking_code,
        'parking_name': parking.parking_name,
        'address': parking.address,
        'parking_type': parking.parking_type,
        'parking_type_name': parking.parking_type_name,
        'operation_type': parking.operation_type,
        'operation_type_name': parking.operation_type_name,
        'phone_number': parking.phone_number,
        'parking_status_available': parking.parking_status_available,
        'parking_status_available_name': parking.parking_status_available_name,
        'total_spaces': parking.total_spaces,
        'current_parking': parking.current_parking,
        'current_parking_update_time': parking.current_parking_update_time,
        'pay_type': parking.pay_type,
        'pay_type_name': parking.pay_type_name,
        'night_free_open': parking.night_free_open,
        'night_free_open_name': parking.night_free_open_name,
        'weekday_start_time': parking.weekday_start_time,
        'weekday_end_time': parking.weekday_end_time,
        'weekend_start_time': parking.weekend_start_time,
        'weekend_end_time': parking.weekend_end_time,
        'holiday_start_time': parking.holiday_start_time,
        'holiday_end_time': parking.holiday_end_time,
        'saturday_pay_type': parking.saturday_pay_type,
        'saturday_pay_type_name': parking.saturday_pay_type_name,
        'holiday_pay_type': parking.holiday_pay_type,
        'holiday_pay_type_name': parking.holiday_pay_type_name,
        'monthly_rate': parking.monthly_rate,
        'street_parking_group_no': parking.street_parking_group_no,
        'basic_rate': parking.basic_rate,
        'basic_time_min': parking.basic_time_min,
        'add_rate': parking.add_rate,
        'add_time_min': parking.add_time_min,
        'bus_basic_rate': parking.bus_basic_rate,
        'bus_basic_time_min': parking.bus_basic_time_min,
        'bus_add_rate': parking.bus_add_rate,
        'bus_add_time_min': parking.bus_add_time_min,
        'day_max_rate': parking.day_max_rate,
        'lat': parking.lat,
        'lng': parking.lng,
        'share_parking_company_name': parking.share_parking_company_name,
        'share_parking': parking.share_parking,
        'share_parking_company_link': parking.share_parking_company_link,
        'share_parking_etc': parking.share_parking_etc
    } for parking in parkings])
