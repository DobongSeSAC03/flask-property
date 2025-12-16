# Flask Property 프로젝트

이 프로젝트는 확장성과 유지 보수성을 위해 블루프린트(Blueprints)를 사용하여 구조화된 Flask 기반 웹 애플리케이션입니다.

## 디자인 패턴 : 마이크로서비스 아키텍처 (Microservices Architecture)

이 프로젝트는 확장성과 유지 보수성을 극대화하기 위해 **마이크로서비스 아키텍처**를 지향하여 구조화되었습니다. Flask의 **Blueprints**를 활용하여 각 기능(서비스)을 독립적인 모듈로 분리하였으며, 향후 별도의 서비스로 쉽게 분리 배포할 수 있도록 설계되었습니다.

### 프로젝트 디렉토리 구조

```plaintext
project_root/
├── .flaskenv               # 환경 변수 (FLASK_APP, FLASK_DEBUG 등 자동 로드)
├── .gitignore              # Git 제외 파일 목록
├── config.py               # [중요] 환경별 설정 (Development, Production, Testing) 분리
├── requirements.txt
├── run.py                  # [중요] 앱 실행 스크립트 (진입점)
├── myapp/                  # 메인 애플리케이션 패키지 (폴더명은 프로젝트명으로 변경 가능)
│   ├── __init__.py         # [중요] Application Factory (create_app) 정의 및 초기화
│   ├── models.py           # 데이터베이스 모델 정의 (SQLAlchemy)
│   ├── templates/          # 전역 공통 템플릿 파일
│   ├── static/             # 전역 공통 정적 파일
│   ├── api/                # [Blueprint] API 관련 기능 모듈
│   │   ├── __init__.py     # Blueprint 객체 생성
│   │   ├── routes.py       # API 엔드포인트 라우팅
│   │   └── schemas.py      # 데이터 검증 및 직렬화 스키마
│   └── auth/               # [Blueprint] 인증 관련 기능 모듈
│       ├── __init__.py
│       ├── routes.py       # 로그인/회원가입 라우팅
│       └── services.py     # 인증 관련 비즈니스 로직
└── tests/                  # 테스트 코드 패키지
    ├── conftest.py         # Pytest 설정 및 공통 Fixture (app, client, db 등)
    ├── test_auth.py
    └── test_api.py
```

### 서비스 모듈 구성 (`myapp/`)

각 폴더는 독립적인 역할을 수행하는 서비스 모듈로 구성되어 있습니다:

- **Auth 서비스 (`auth/`)**:
  - 사용자 인증 및 인가(로그인, 회원가입 등)를 전담합니다.
  - JWT 또는 세션 관리 로직이 포함됩니다.
  
- **API 서비스 (`api/`)**:
  - 핵심 비즈니스 로직을 처리하는 RESTful API 서버 역할을 합니다.
  - 외부 클라이언트 또는 프론트엔드와의 데이터 통신을 담당합니다.

- **Main 서비스 (`main/`)**:
  - 사용자에게 보여지는 UI 렌더링 또는 메인 라우팅을 담당합니다.
  - 웹 페이지 뷰(View) 로직이 포함됩니다.

- **공통 모듈**:
  - `models.py`: 데이터베이스 모델 (User 등) 공유.
  - `__init__.py`: 애플리케이션 팩토리 패턴을 통한 앱 생성 및 각 블루프린트(서비스) 등록.
- `config.py`: 개발 및 프로덕션 환경을 위한 설정.
- `run.py`: 애플리케이션 실행을 위한 진입점.
- `.flaskenv`: Flask 환경 변수.

## 사전 요구 사항

- Python 3.8 이상
- pip (Python 패키지 설치 관리자)

## 설치

1. 저장소를 복제하거나(해당되는 경우) 프로젝트 디렉토리로 이동합니다.

2. 가상 환경을 생성하고 활성화합니다:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows의 경우 `venv\Scripts\activate` 사용
   ```

3. 필요한 의존성을 설치합니다:

   ```bash
   pip install -r requirements.txt
   ```

4. 가상 환경을 해제하려면:

   ```bash
   deactivate
   ```



### 5. 데이터베이스별 필수 의존성 설치 (SQLAlchemy)

프로젝트에서 사용하는 데이터베이스에 따라 추가 드라이버 설치가 필요할 수 있습니다.

| 데이터베이스 | 라이브러리 | 설치 명령어 | 연결 URI 예시 | 비고 |
|---|---|---|---|---|
| **PostgreSQL** | `psycopg2` | `pip install psycopg2-binary` | `postgresql://user:password@host:5432/dbname` | 개발환경 권장 (프로덕션: `psycopg2`) |
| **MySQL / MariaDB** | `pymysql` | `pip install pymysql` | `mysql+pymysql://user:password@host:3306/dbname` | - |
| **MySQL / MariaDB** | `mysqlclient` | `pip install mysqlclient` | `mysql://user:password@host:3306/dbname` | C 확장 모듈 (설치 시 시스템 의존성 필요) |
| **SQLite** | - | - | `sqlite:///path/to/database.db` | Python 내장 라이브러리 (설치 불필요) |
| **Oracle** | `cx_Oracle` | `pip install cx_Oracle` | `oracle://user:password@host:1521/sid` | - |
| **MS SQL Server** | `pyodbc` | `pip install pyodbc` | `mssql+pyodbc://user:password@host:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server` | ODBC 드라이버 필요 |

> **참고**: `requirements.txt`에 포함되지 않은 경우 위 명령어로 직접 설치해 주십시오.

## 환경 설정 및 실행 (Configuration & Running)

애플리케이션 실행 전 환경 변수 설정이 필요합니다. `.flaskenv`와 `.env` 파일을 통해 설정을 관리할 수 있습니다.

### 1. 환경 변수 파일 생성

프로젝트 루트 디렉토리에 다음 파일들을 생성합니다.

**`.flaskenv`** (Flask 실행 옵션 - Git에 포함 가능):
```ini
FLASK_APP=run.py
FLASK_DEBUG=1
```

**`.env`** (비밀 설정 - **Git 제외 필수**):
```ini
FLASK_CONFIG=development
SECRET_KEY=secure-random-secret-key
DEV_DATABASE_URL=sqlite:///dev.db
DATABASE_URL=postgresql://user:password@localhost/dbname
```

> **참고**: `Flask-DebugToolbar`가 `run.py`에 설정되어 있어, 개발 모드 실행 시 브라우저에서 디버그 툴바를 사용할 수 있습니다. `config.py`의 `SECRET_KEY`가 반드시 설정되어 있어야 합니다. `DebugToolbarExtension(app)`를 통해 활성화됩니다.


### 2. 애플리케이션 실행

환경 변수가 설정되어 있다면 다음 명령어로 바로 실행할 수 있습니다.

```bash
flask run
```

또는 특정 설정을 명시하여 실행할 수도 있습니다:

```bash
export FLASK_CONFIG=development
flask run
```

애플리케이션은 `http://127.0.0.1:5000/`에서 확인할 수 있습니다.

### 3. VS Code 디버깅 설정 (Optional)

Visual Studio Code에서 디버깅 기능을 사용하려면 `.vscode/launch.json` 파일을 생성하여 다음과 같이 설정합니다.

**.vscode/launch.json**:
```json
{
    "version": "0.2.0",
    "configurations": [
        // =============================================================
        // [1] Flask 설정
        // =============================================================
        {
            "name": "부동산 데이터 App", // VS Code 디버그 드롭다운에 표시될 이름
            "type": "python", // 디버그 유형: 파이썬
            "request": "launch", // 실행(launch) 요청
            "module": "flask", // 'flask' 모듈을 실행
            "env": {
                // FLASK_APP 환경 변수 설정: cwd(app_microservice) 폴더 내의 run.py 파일을 시작 파일로 지정
                "FLASK_APP": "run.py",
                "FLASK_DEBUG": "1" // 디버그 모드 활성화 (오류 발생 시 상세 정보 표시)
            },
            "args": [
                "run",
                "--no-debugger", // VS Code 자체 디버거를 사용하므로 Flask의 내장 디버거는 비활성화
                // "--no-reload" // VS Code 자체 디버거를 사용하므로 Flask의 리로더도 비활성화
            ],
            "jinja": true, // Flask 템플릿(Jinja2) 디버깅 지원 활성화
            // ⭐ 현재 작업 디렉토리(루트 경로) 설정
            // 이 경로부터 상대 경로(예: FLASK_APP: "run.py")가 시작됩니다.
            "cwd": "${workspaceFolder}",
            "justMyCode": true // 사용자 코드만 디버그하고 외부 라이브러리 코드는 건너뜁니다.
        },
        // =============================================================
        // [2] Python: Current File 설정 (일반적인 파이썬 스크립트 실행)
        // 현재 열려있는 Python 파일을 일반 스크립트로 디버그합니다.
        // =============================================================
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}", // 현재 VS Code에서 활성화된 파일(.py)을 실행
            "console": "integratedTerminal", // 출력을 VS Code 내장 터미널로 보냄
            "justMyCode": true
        }
    ]
}
```

## API 엔드포인트

- `/`: 메인 인덱스 라우트.
- `/auth`: 인증 라우트.
- `/api`: API 라우트.

## Git 전략 및 협업 규칙

프로젝트의 체계적인 관리를 위해 **Git-Flow** 방식을 도입하여 `main`, `develop`, `feature` 브랜치를 운영합니다.
또한, **GitHub Issues**와 연동하여 이슈 단위로 작업을 관리합니다.

### 1. 브랜치 전략

- **`main`**: 
  - 언제든지 제품으로 배포 가능한 **안정적인 상태(Production)**를 유지합니다.
  - `develop` 브랜치에서 충분히 검증된 코드만 병합됩니다.

- **`develop`**: 
  - 다음 배포를 위해 개발 중인 기능을 통합하는 **개발 중심 브랜치**입니다.
  - 모든 Feature 브랜치는 이곳으로 병합되어 테스트됩니다.

- **`feature/*`**:
  - 새로운 기능 개발, 버그 수정 등을 위한 브랜치입니다.
  - `develop` 브랜치에서 생성하며, 작업 완료 후 다시 `develop`으로 병합(PR)합니다.

### 2. Feature 브랜치 명명 규칙 (GitHub Issue 연동)

모든 작업은 **GitHub Issue** 생성 후 시작하며, 이슈 보드에서 생성된 브랜치 이름을 사용합니다.

- **규칙**: GitHub Issue 페이지의 `Create a branch` 기능을 통해 자동 생성된 이름을 그대로 사용합니다.
- **예시**: `1-login-function` (이슈번호-제목)

### 3. 커밋 메시지 규칙 (Conventional Commits)

명확한 변경 이력 관리를 위해 **Angular Commit Convention**을 따릅니다.

**형식:**
```plaintext
<type>: <subject>

 - <body1>
 - <body2>
```
> **참고**: 내용이 짧으면 body 없이 작성할 수 있습니다.

**Type 종류:**
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정 (README 등)
- `style`: 코드 포맷팅 (로직 변경 없음)
- `refactor`: 코드 리팩토링 (기능 변경 없음)
- `test`: 테스트 코드 추가/수정
- `chore`: 빌드 업무, 패키지 매니저 설정 등

**예시:**
```plaintext
feat: 사용자 로그인 API 구현

- JWT를 이용한 로그인 인증 로직 추가
- 사용자 정보 관리 모델 구현
```
