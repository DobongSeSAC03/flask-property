from myapp import db

# 부동산 실거래가 테이블
class RealEstateTransaction(db.Model):
    __tablename__ = 'real_estate_transaction'
    
    ret_id = db.Column(db.Integer, primary_key=True)
    reception_year = db.Column(db.Integer)  # 접수연도
    district_code = db.Column(db.String(10))  # 자치구코드
    district_name = db.Column(db.String(50))  # 자치구명
    legal_dong_code = db.Column(db.String(10))  # 법정동코드
    legal_dong_name = db.Column(db.String(50))  # 법정동명
    jibun_type = db.Column(db.String(10))  # 지번구분
    jibun_type_name = db.Column(db.String(50))  # 지번구분명
    main_number = db.Column(db.String(10))  # 본번
    sub_number = db.Column(db.String(10))  # 부번
    building_name = db.Column(db.String(100))  # 건물명
    contract_date = db.Column(db.String(8))  # 계약일
    amount = db.Column(db.BigInteger)  # 물건금액(만원)
    building_area = db.Column(db.Float)  # 건물면적(㎡)
    land_area = db.Column(db.Float)  # 토지면적(㎡)
    floor = db.Column(db.Integer)  # 층
    right_type = db.Column(db.String(50))  # 권리구분
    cancel_date = db.Column(db.String(8), nullable=True)  # 취소일
    construction_year = db.Column(db.Integer)  # 건축년도
    building_use = db.Column(db.String(50))  # 건물용도
    declaration_type = db.Column(db.String(50))  # 신고구분
    broker_district_name = db.Column(db.String(100))  # 신고한 개업공인중개사 시군구명

    def __repr__(self):
        return f'<RealEstateTransaction {self.id} {self.building_name}>'

class PublicParking(db.Model):
    __tablename__ = 'public_parking'

    pp_id = db.Column(db.Integer, primary_key=True)
    parking_code = db.Column(db.String(20))  # 주차장코드
    parking_name = db.Column(db.String(100))  # 주차장명
    address = db.Column(db.String(200))  # 주소
    parking_type = db.Column(db.String(20))  # 주차장 종류
    parking_type_name = db.Column(db.String(50))  # 주차장 종류명
    operation_type = db.Column(db.String(20))  # 운영구분
    operation_type_name = db.Column(db.String(50))  # 운영구분명
    phone_number = db.Column(db.String(20))  # 전화번호
    parking_status_available = db.Column(db.String(1))  # 주차현황 정보 제공여부
    parking_status_available_name = db.Column(db.String(10))  # 주차현황 정보 제공여부명
    total_spaces = db.Column(db.Integer)  # 총 주차면
    current_parking = db.Column(db.Integer)  # 현재 주차 차량수
    current_parking_update_time = db.Column(db.String(50))  # 현재 주차 차량수 업데이트시간
    pay_type = db.Column(db.String(10))  # 유무료구분
    pay_type_name = db.Column(db.String(20))  # 유무료구분명
    night_free_open = db.Column(db.String(1))  # 야간무료개방여부
    night_free_open_name = db.Column(db.String(10))  # 야간무료개방여부명
    weekday_start_time = db.Column(db.String(4))  # 평일 운영 시작시각(HHMM)
    weekday_end_time = db.Column(db.String(4))  # 평일 운영 종료시각(HHMM)
    weekend_start_time = db.Column(db.String(4))  # 주말 운영 시작시각(HHMM)
    weekend_end_time = db.Column(db.String(4))  # 주말 운영 종료시각(HHMM)
    holiday_start_time = db.Column(db.String(4))  # 공휴일 운영 시작시각(HHMM)
    holiday_end_time = db.Column(db.String(4))  # 공휴일 운영 종료시각(HHMM)
    saturday_pay_type = db.Column(db.String(10))  # 토요일 유,무료 구분
    saturday_pay_type_name = db.Column(db.String(20))  # 토요일 유,무료 구분명
    holiday_pay_type = db.Column(db.String(10))  # 공휴일 유,무료 구분
    holiday_pay_type_name = db.Column(db.String(20))  # 공휴일 유,무료 구분명
    monthly_rate = db.Column(db.Integer)  # 월 정기권 금액
    street_parking_group_no = db.Column(db.String(20))  # 노상 주차장 관리그룹번호
    basic_rate = db.Column(db.Integer)  # 기본 주차 요금
    basic_time_min = db.Column(db.Integer)  # 기본 주차 시간(분 단위)
    add_rate = db.Column(db.Integer)  # 추가 단위 요금
    add_time_min = db.Column(db.Integer)  # 추가 단위 시간(분 단위)
    bus_basic_rate = db.Column(db.Integer)  # 버스 기본 주차 요금
    bus_basic_time_min = db.Column(db.Integer)  # 버스 기본 주차 시간(분 단위)
    bus_add_rate = db.Column(db.Integer)  # 버스 추가 단위 요금
    bus_add_time_min = db.Column(db.Integer)  # 버스 추가 단위 시간(분 단위)
    day_max_rate = db.Column(db.Integer)  # 일 최대 요금
    lat = db.Column(db.Float)  # 주차장 위치 좌표 위도
    lng = db.Column(db.Float)  # 주차장 위치 좌표 경도
    share_parking_company_name = db.Column(db.String(50))  # 공유 주차장 관리업체명
    share_parking = db.Column(db.String(1))  # 공유 주차장 여부
    share_parking_company_link = db.Column(db.String(200))  # 공유 주차장 관리업체 링크
    share_parking_etc = db.Column(db.String(200))  # 공유 주차장 기타사항

    def __repr__(self):
        return f'<PublicParking {self.parking_code} {self.parking_name}>'
