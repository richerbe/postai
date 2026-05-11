import streamlit as st
import json
import os
from datetime import datetime
import hashlib

st.set_page_config(
    page_title="PostAI - SNS 자동화",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }

    body {
        background: linear-gradient(135deg, #0c0c18 0%, #13132a 100%);
        font-family: 'Noto Sans KR', sans-serif;
    }

    .main {
        padding: 40px 20px;
    }

    .header-section {
        text-align: center;
        margin-bottom: 60px;
        animation: fadeIn 0.8s ease-in;
    }

    .header-section h1 {
        font-size: 3.5em;
        background: linear-gradient(135deg, #f39c12, #e056fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        font-weight: 900;
    }

    .header-section p {
        font-size: 1.2em;
        color: #a0a0b8;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 0.95em;
        color: #606080;
    }

    .category-title {
        font-size: 1.8em;
        font-weight: 700;
        color: #f0f0f0;
        margin-top: 50px;
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 2px solid rgba(243, 156, 18, 0.3);
    }

    .card-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 25px;
        margin-bottom: 40px;
    }

    .card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1px solid rgba(243, 156, 18, 0.2);
        border-radius: 20px;
        padding: 30px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.34, 0.1, 0.64, 1);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }

    .card:hover {
        transform: translateY(-8px);
        border-color: rgba(243, 156, 18, 0.5);
        box-shadow: 0 20px 50px rgba(243, 156, 18, 0.15);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.04) 100%);
    }

    .card-icon {
        font-size: 3em;
        margin-bottom: 15px;
        display: inline-block;
    }

    .card-title {
        font-size: 1.4em;
        font-weight: 700;
        color: #f0f0f0;
        margin-bottom: 10px;
    }

    .card-description {
        font-size: 0.95em;
        color: #a0a0b8;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    .card-button {
        display: inline-block;
        background: linear-gradient(135deg, #f39c12, #e056fd);
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9em;
        transition: all 0.3s;
    }

    .card-button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 25px rgba(243, 156, 18, 0.3);
    }

    .login-section {
        max-width: 400px;
        margin: 100px auto;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(243, 156, 18, 0.3);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# 설정 파일 경로
CONFIG_FILE = "config.yaml"

def load_config():
    if os.path.exists(CONFIG_FILE):
        import yaml
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def save_config(data):
    import yaml
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True)

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

cfg = load_config()

# 카테고리별 메뉴 정의
CATEGORIES = {
    "📝 콘텐츠 생성": [
        {"title": "글쓰기", "icon": "✍️", "description": "AI 기반 고품질 글 작성"},
        {"title": "카드뉴스", "icon": "🎨", "description": "시각적 카드뉴스 제작"},
        {"title": "해시태그", "icon": "#️⃣", "description": "트렌드 해시태그 생성"},
    ],
    "📅 발행 관리": [
        {"title": "발행 일정", "icon": "📆", "description": "SNS 발행 캘린더"},
        {"title": "예약 발행", "icon": "⏰", "description": "자동 발행 스케줄"},
        {"title": "일괄 발행", "icon": "📤", "description": "여러 채널 동시 발행"},
    ],
    "📊 성과 분석": [
        {"title": "실시간 분석", "icon": "📈", "description": "조회수, 좋아요 분석"},
        {"title": "팔로워 추이", "icon": "📊", "description": "팔로워 증가 현황"},
        {"title": "최고 성과", "icon": "🏆", "description": "가장 잘된 콘텐츠"},
    ],
    "🔧 채널 연동": [
        {"title": "Instagram", "icon": "📸", "description": "인스타그램 연동"},
        {"title": "YouTube", "icon": "▶️", "description": "유튜브 채널 연동"},
        {"title": "TikTok", "icon": "🎵", "description": "틱톡 계정 연동"},
    ],
    "👥 팀 관리": [
        {"title": "멤버 관리", "icon": "👤", "description": "팀 멤버 초대 및 권한"},
        {"title": "역할 설정", "icon": "🎯", "description": "멤버 역할 지정"},
        {"title": "활동 로그", "icon": "📋", "description": "팀 활동 기록 조회"},
    ],
}

# 로그인 페이지
if not st.session_state.logged_in:
    st.markdown("""
    <div class="login-section">
        <h1 style="font-size: 2.5em; margin-bottom: 10px;">🚀 PostAI</h1>
        <p style="color: #a0a0b8; font-size: 1.1em; margin-bottom: 30px;">SNS 자동화 플랫폼</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 로그인")

        login_username = st.text_input("사용자명", placeholder="admin")
        login_password = st.text_input("비밀번호", type="password", placeholder="admin123")

        if st.button("🔓 로그인", use_container_width=True, key="login_btn"):
            pwd_hash = hash_password(login_password)
            if login_username in cfg.get("users", {}):
                user_data = cfg["users"][login_username]
                if user_data["password"] == pwd_hash and user_data.get("enabled", False):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.success("✅ 로그인 성공!")
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 잘못되었거나 승인 대기 중입니다.")
            else:
                st.error("❌ 사용자를 찾을 수 없습니다.")

        st.markdown("---")
        st.markdown("#### 📝 회원가입")

        reg_username = st.text_input("새 사용자명", placeholder="username", key="reg_user")
        reg_email = st.text_input("이메일", placeholder="user@example.com", key="reg_email")
        reg_password = st.text_input("비밀번호", type="password", placeholder="비밀번호", key="reg_pwd")

        if st.button("✍️ 가입 신청", use_container_width=True):
            if reg_username and reg_email and reg_password:
                if "users" not in cfg:
                    cfg["users"] = {}

                if reg_username in cfg["users"]:
                    st.error("❌ 이미 존재하는 사용자명입니다.")
                else:
                    cfg["users"][reg_username] = {
                        "email": reg_email,
                        "password": hash_password(reg_password),
                        "enabled": False,
                        "role": "editor",
                        "created_at": datetime.now().isoformat()
                    }
                    save_config(cfg)
                    st.success("✅ 가입 신청 완료! 관리자 승인 대기 중입니다.")

        st.markdown("---")
        st.info("📝 **데모 계정**: admin / admin123")

else:
    # 헤더
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown(f"### 👋 {st.session_state.username}님 환영합니다!")
    with col3:
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

    st.markdown("---")

    # 메인 홈페이지
    st.markdown("""
    <div class="header-section">
        <h1>🚀 PostAI</h1>
        <p>SNS 자동화 플랫폼</p>
        <p class="subtitle">모든 SNS 채널을 한 곳에서 관리하세요</p>
    </div>
    """, unsafe_allow_html=True)

    # 카테고리별 카드 UI
    for category, items in CATEGORIES.items():
        st.markdown(f"<h2 class='category-title'>{category}</h2>", unsafe_allow_html=True)

        cols = st.columns(3)
        for idx, item in enumerate(items):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="card">
                    <div class="card-icon">{item['icon']}</div>
                    <div class="card-title">{item['title']}</div>
                    <div class="card-description">{item['description']}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"시작하기 →", use_container_width=True, key=f"btn_{item['title']}"):
                    st.session_state.current_page = item['title']
                    st.rerun()

    # 추가 섹션
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 💡 팁
        - 매일 정오에 최고 성과 콘텐츠 추천
        - AI가 최적의 발행 시간 제안
        - 자동 해시태그 생성으로 도달률 증가
        """)

    with col2:
        st.markdown("""
        ### 📊 현황
        - **팔로워**: 12,500명
        - **이번달 조회**: 45,000회
        - **상호작용률**: 8.5%
        """)
