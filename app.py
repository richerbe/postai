import streamlit as st

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

    .badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: 600;
        margin-bottom: 15px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .premium-badge {
        display: inline-block;
        background: rgba(168, 85, 247, 0.2);
        color: #a855f7;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: 600;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }

    .cta-button {
        background: linear-gradient(135deg, #f39c12, #e056fd);
        color: white;
        padding: 15px 40px;
        border: none;
        border-radius: 12px;
        font-size: 1.1em;
        font-weight: 700;
        cursor: pointer;
        width: 100%;
        transition: all 0.3s;
        margin-top: 30px;
    }

    .cta-button:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 40px rgba(243, 156, 18, 0.3);
    }

    .stats-section {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 50px 0;
    }

    .stat-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(243, 156, 18, 0.3);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
    }

    .stat-number {
        font-size: 2.5em;
        font-weight: 900;
        background: linear-gradient(135deg, #f39c12, #e056fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stat-label {
        color: #a0a0b8;
        margin-top: 10px;
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

# 자동 로그인 (세션 상태)
if "auto_logged_in" not in st.session_state:
    st.session_state.auto_logged_in = True
    st.session_state.username = "무료사용자"
    st.session_state.is_premium = False
    st.session_state.current_page = "home"

# 카테고리별 메뉴 정의
CATEGORIES = {
    "📝 콘텐츠 생성": [
        {"title": "글쓰기", "icon": "✍️", "description": "AI 기반 고품질 글 작성", "premium": False, "page": "writing"},
        {"title": "카드뉴스", "icon": "🎨", "description": "시각적 카드뉴스 제작", "premium": False, "page": "cardnews"},
        {"title": "해시태그", "icon": "#️⃣", "description": "트렌드 해시태그 생성", "premium": False, "page": "hashtag"},
    ],
    "📅 발행 관리": [
        {"title": "발행 일정", "icon": "📆", "description": "SNS 발행 캘린더", "premium": False, "page": "schedule"},
        {"title": "예약 발행", "icon": "⏰", "description": "자동 발행 스케줄", "premium": True, "page": "reserved"},
        {"title": "일괄 발행", "icon": "📤", "description": "여러 채널 동시 발행", "premium": True, "page": "batch"},
    ],
    "📊 성과 분석": [
        {"title": "실시간 분석", "icon": "📈", "description": "조회수, 좋아요 분석", "premium": False, "page": "analytics"},
        {"title": "팔로워 추이", "icon": "📊", "description": "팔로워 증가 현황", "premium": True, "page": "followers"},
        {"title": "최고 성과", "icon": "🏆", "description": "가장 잘된 콘텐츠", "premium": True, "page": "best"},
    ],
    "🔧 채널 연동": [
        {"title": "Instagram", "icon": "📸", "description": "인스타그램 연동", "premium": False, "page": "instagram"},
        {"title": "YouTube", "icon": "▶️", "description": "유튜브 채널 연동", "premium": False, "page": "youtube"},
        {"title": "TikTok", "icon": "🎵", "description": "틱톡 계정 연동", "premium": True, "page": "tiktok"},
    ],
}

# ============ 페이지: 글쓰기 ============
def page_writing():
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        if st.button("← 뒤로", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()

    st.markdown("## ✍️ AI 글쓰기")
    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 주제 입력")
        topic = st.text_input("어떤 주제로 글을 작성하시겠어요?", placeholder="예: 여름 패션 트렌드")
        tone = st.selectbox("톤앤매너", ["친근한", "전문적인", "유머있는", "감성적인"])
        length = st.slider("글의 길이", 100, 1000, 300)

    with col2:
        st.markdown("### 채널 선택")
        channels = st.multiselect("어느 채널에 발행하시겠어요?", ["Instagram", "YouTube", "Naver Blog"])
        hashtags = st.toggle("해시태그 자동 생성")

    st.markdown("---")

    if st.button("🚀 글 생성하기", use_container_width=True):
        if topic:
            with st.spinner("AI가 멋진 글을 작성 중입니다..."):
                import time
                time.sleep(2)

            st.success(f"✅ 완료! '{topic}'에 대한 {length}자 글이 생성되었습니다.")
            st.markdown("""
            ### 📝 생성된 글

            **{topic}**

            오늘은 {topic}에 대해 이야기해볼게요. 이것은 정말 흥미로운 주제입니다.

            {tone} 톤으로 작성된 이 글은 여러분의 {', '.join(channels)} 채널에 완벽합니다.

            #트렌드 #최신정보 #공유
            """.format(topic=topic, tone=tone, channels=channels))

            col1, col2, col3 = st.columns(3)
            with col1:
                st.button("📋 복사", use_container_width=True)
            with col2:
                st.button("📤 발행하기", use_container_width=True)
            with col3:
                st.button("🔄 다시 생성", use_container_width=True)
        else:
            st.warning("주제를 입력해주세요!")

# ============ 페이지: 해시태그 ============
def page_hashtag():
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        if st.button("← 뒤로", use_container_width=True, key="back_hashtag"):
            st.session_state.current_page = "home"
            st.rerun()

    st.markdown("## #️⃣ 해시태그 생성")
    st.markdown("---")

    keyword = st.text_input("키워드를 입력하세요", placeholder="예: 커피, 여행, 패션")

    col1, col2 = st.columns(2)
    with col1:
        count = st.slider("생성할 해시태그 개수", 5, 30, 15)
    with col2:
        trend = st.toggle("트렌드 중심으로", value=True)

    if st.button("✨ 해시태그 생성", use_container_width=True):
        if keyword:
            with st.spinner("트렌드 해시태그를 분석 중입니다..."):
                import time
                time.sleep(1)

            st.success(f"✅ '{keyword}' 관련 {count}개의 해시태그가 생성되었습니다!")
            st.markdown(f"""
            ### 생성된 해시태그

            #초보자 #{keyword} #{keyword}추천 #{keyword}정보 #{keyword}팁
            #일상 #공유 #감성 #트렌드 #최신정보
            """)
            st.button("📋 전체 복사", use_container_width=True)
        else:
            st.warning("키워드를 입력해주세요!")

# ============ 페이지: 실시간 분석 ============
def page_analytics():
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        if st.button("← 뒤로", use_container_width=True, key="back_analytics"):
            st.session_state.current_page = "home"
            st.rerun()

    st.markdown("## 📈 실시간 분석")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("조회수", "2,543", "+12%")
    with col2:
        st.metric("좋아요", "342", "+5%")
    with col3:
        st.metric("댓글", "89", "+3%")

    st.markdown("### 최근 게시물 성과")
    st.info("📱 스크롤하여 더 많은 데이터를 확인하세요")

# ============ 메인 페이지 ============
def page_home():
    # 헤더
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"### 👋 {st.session_state.username}님, 환영합니다!")

    st.markdown("---")

    # 메인 홈페이지
    st.markdown("""
    <div class="header-section">
        <h1>🚀 PostAI</h1>
        <p>SNS 자동화 플랫폼</p>
        <p class="subtitle">모든 SNS 채널을 한 곳에서 관리하세요</p>
    </div>
    """, unsafe_allow_html=True)

    # 통계
    st.markdown("""
    <div class="stats-section">
        <div class="stat-card">
            <div class="stat-number">50K+</div>
            <div class="stat-label">활성 사용자</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">1M+</div>
            <div class="stat-label">발행된 콘텐츠</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">자동 관리</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 카테고리별 카드 UI
    for category, items in CATEGORIES.items():
        st.markdown(f"<h2 class='category-title'>{category}</h2>", unsafe_allow_html=True)

        cols = st.columns(3)
        for idx, item in enumerate(items):
            with cols[idx % 3]:
                badge = '🆓 무료' if not item['premium'] else '💎 프리미엄'
                badge_color = 'rgba(16, 185, 129, 0.2)' if not item['premium'] else 'rgba(168, 85, 247, 0.2)'
                badge_text = '#10b981' if not item['premium'] else '#a855f7'

                st.markdown(f"""
                <div class="card">
                    <div class="card-icon">{item['icon']}</div>
                    <div class="badge" style="background: {badge_color}; color: {badge_text};">{badge}</div>
                    <div class="card-title">{item['title']}</div>
                    <div class="card-description">{item['description']}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"시작하기 →", use_container_width=True, key=f"btn_{item['title']}"):
                    if item['premium'] and not st.session_state.is_premium:
                        st.warning("💎 이 기능은 프리미엄 플랜에서 사용 가능합니다!")
                    else:
                        st.session_state.current_page = item['page']
                        st.rerun()

    st.markdown("---")

    # 가격 계획
    st.markdown("### 💰 간단한 가격 계획")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 🆓 무료
        - 기본 콘텐츠 생성
        - 1개 채널 연동
        - 기본 분석

        **$0/월**
        """)
        if st.button("지금 시작", key="free_plan", use_container_width=True):
            st.success("✅ 무료 플랜으로 시작되었습니다!")

    with col2:
        st.markdown("""
        #### 💎 프로
        - 모든 생성 기능
        - 5개 채널 연동
        - 고급 분석
        - 우선 지원

        **$9.99/월**
        """)
        if st.button("업그레이드", key="pro_plan", use_container_width=True):
            st.info("📍 프로 플랜으로 업그레이드하세요!")

    with col3:
        st.markdown("""
        #### 🚀 엔터프라이즈
        - 무제한 기능
        - 무제한 채널
        - API 접근
        - 전담 담당자

        **문의**
        """)
        if st.button("문의하기", key="enterprise_plan", use_container_width=True):
            st.info("📧 enterprise@postai.com으로 문의하세요!")

    st.markdown("---")

    # FAQ
    st.markdown("### ❓ 자주 묻는 질문")

    with st.expander("🆓 무료 플랜으로 무엇을 할 수 있나요?"):
        st.write("""
        - 월 30개의 콘텐츠 생성
        - Instagram, YouTube 연동
        - 기본 성과 분석
        - 무제한 텍스트 생성
        """)

    with st.expander("💳 결제 방법은?"):
        st.write("""
        - 신용카드 (Visa, Mastercard)
        - Google Pay
        - Apple Pay
        - 월간/연간 결제 선택 가능
        """)

    with st.expander("🔄 언제든 취소 가능한가요?"):
        st.write("""
        - 언제든지 취소 가능합니다
        - 환불은 정책에 따릅니다
        - 취소 후에도 월말까지 사용 가능합니다
        """)

    st.markdown("---")

    # 푸터
    st.markdown("""
    <div style="text-align: center; color: #606080; margin-top: 50px;">
        <p>© 2026 PostAI. All rights reserved.</p>
        <p>
            <a href="#" style="color: #a0a0b8; text-decoration: none;">이용약관</a> |
            <a href="#" style="color: #a0a0b8; text-decoration: none;">개인정보</a> |
            <a href="#" style="color: #a0a0b8; text-decoration: none;">지원</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============ 페이지 라우팅 ============
if st.session_state.current_page == "home":
    page_home()
elif st.session_state.current_page == "writing":
    page_writing()
elif st.session_state.current_page == "hashtag":
    page_hashtag()
elif st.session_state.current_page == "analytics":
    page_analytics()
else:
    # 구현되지 않은 페이지
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        if st.button("← 뒤로", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()

    st.markdown(f"## {st.session_state.current_page}")
    st.info("🚧 이 기능은 준비 중입니다. 조금만 기다려주세요!")
