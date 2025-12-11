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

## API 엔드포인트

- `/`: 메인 인덱스 라우트.
- `/auth`: 인증 라우트.
- `/api`: API 라우트.

## Git 전략 및 협업 규칙

이 프로젝트의 규모와 특성에 맞춰 가볍고 효율적인 **Feature Branch Workflow**를 권장합니다.
`main` 브랜치는 항상 안정적인 상태를 유지하며, 모든 개발은 별도의 기능 브랜치에서 진행 후 병합(Merge/Squash)합니다.

### 1. 브랜치 전략 (Feature Branch Workflow)

- **`main`**: 
  - 제품으로 배포 가능한 상태의 코드를 관리합니다. (Production-ready)
  - 직접 커밋을 지양하고 PR(Pull Request)을 통해서만 병합합니다.

- **`feature/*`**:
  - 새로운 기능 개발이나 버그 수정을 위한 브랜치입니다.
  - `main` 브랜치에서 생성하며, 작업 완료 후 `main`으로 병합됩니다.
  - 명명 규칙: `feature/기능요약` (예: `feature/login-api`, `feature/user-model`)

### 2. 커밋 메시지 규칙 (Conventional Commits)

명확한 변경 이력 관리를 위해 **Angular Commit Convention**을 따릅니다.

**형식:**
```plaintext
<type>: <subject>

<body>
```

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

JWT를 이용한 로그인 인증 로직 추가
```
