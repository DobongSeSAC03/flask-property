import sys
import os

def setup_db_context():
    """
    Jupyter Notebook을 위한 Flask 앱 컨텍스트 및 데이터베이스 연결을 설정합니다.
    Returns:
        app: Flask 애플리케이션 인스턴스.
        db: SQLAlchemy 데이터베이스 인스턴스.
    """
    # 프로젝트 루트를 sys.path에 추가
    project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
    if project_root not in sys.path:
        sys.path.append(project_root)

    from myapp import create_app, db

    # 기본 설정(Development)으로 앱 생성
    app = create_app('default')
    ctx = app.app_context()
    ctx.push()

    print("데이터베이스 연결 및 앱 컨텍스트 푸시 완료.")
    return app, db
