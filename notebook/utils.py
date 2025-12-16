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
    # Flask 애플리케이션 컨텍스트를 푸시하여 `current_app`, `db` 등과 같은 애플리케이션 의존적인 객체들을
    # 요청 컨텍스트 외부(예: Jupyter 노트북)에서 사용할 수 있도록 합니다.
    ctx.push()

    print("데이터베이스 연결 및 앱 컨텍스트 푸시 완료.")
    return app, db
