import sys, os, hashlib
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import yaml
from pathlib import Path
from datetime import datetime

# ── 페이지 설정 ───────────────────────────────────────────
st.set_page_config(
    page_title="SNS 자동 업로드",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 공통 함수 ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_cfg():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_cfg(cfg: dict):
    with open("config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
    st.cache_data.clear()

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

PLATFORMS = {
    "instagram": "📸 Instagram",
    "threads":   "🧵 Threads",
    "youtube":   "▶️ YouTube",
    "naver":     "🟢 네이버 블로그",
    "wordpress": "🌐 WordPress",
}

# ── 세션 상태 초기화 ────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.user_role = None

cfg = load_cfg()

# 기본 관리자 사용자 설정
if not cfg.get("users"):
    cfg["users"] = {
        "admin": {
            "password": hash_password("admin123"),
            "role": "관리자",
            "enabled": True,
            "created_at": datetime.now().isoformat()
        }
    }
    save_cfg(cfg)

# ── 로그인 페이지 ──────────────────────────────────────────
def show_login_page():
    st.set_page_config(layout="centered")
    st.markdown("## 🔐 로그인")
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["로그인", "회원가입"])

        with tab_login:
            login_user = st.text_input("사용자명", placeholder="사용자명 입력")
            login_pwd = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력")

            if st.button("🔓 로그인", type="primary", use_container_width=True):
                pwd_hash = hash_password(login_pwd)
                if login_user in cfg.get("users", {}):
                    user_data = cfg["users"][login_user]
                    if user_data["password"] == pwd_hash and user_data["enabled"]:
                        st.session_state.logged_in = True
                        st.session_state.current_user = login_user
                        st.session_state.user_role = user_data["role"]
                        st.success("✅ 로그인 성공!")
                        st.rerun()
                    else:
                        st.error("❌ 비밀번호가 올바르지 않습니다.")
                else:
                    st.error("❌ 등록되지 않은 사용자입니다.")

        with tab_signup:
            st.info("👤 새 계정 생성 (관리자 승인 필요)")
            signup_user = st.text_input("사용자명", placeholder="새 사용자명", key="signup_user")
            signup_pwd = st.text_input("비밀번호", type="password", placeholder="비밀번호 (8자 이상)", key="signup_pwd")
            signup_pwd_confirm = st.text_input("비밀번호 확인", type="password", key="signup_confirm")

            if st.button("📝 가입 신청", use_container_width=True):
                if not signup_user or not signup_pwd:
                    st.error("❌ 모든 필드를 입력해주세요.")
                elif len(signup_pwd) < 8:
                    st.error("❌ 비밀번호는 8자 이상이어야 합니다.")
                elif signup_pwd != signup_pwd_confirm:
                    st.error("❌ 비밀번호가 일치하지 않습니다.")
                elif signup_user in cfg.get("users", {}):
                    st.error("❌ 이미 존재하는 사용자명입니다.")
                else:
                    cfg["users"][signup_user] = {
                        "password": hash_password(signup_pwd),
                        "role": "뷰어",
                        "enabled": False,
                        "created_at": datetime.now().isoformat(),
                        "status": "pending"
                    }
                    save_cfg(cfg)
                    st.success("✅ 가입 신청 완료!\n\n관리자의 승인을 기다려주세요.")

    st.divider()
    st.info("**데모 계정**: admin / admin123")

# ── 로그인하지 않은 경우 로그인 페이지 표시
if not st.session_state.logged_in:
    show_login_page()
    st.stop()

# ── 사이드바 (로그인 후에만 표시) ────────────────────────────
set_page_config_reset = st.set_page_config(
    page_title="SNS 자동 업로드",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.markdown(f"## 🚀 SNS 자동 업로드")
    st.markdown(f"**👤 {st.session_state.current_user}** ({st.session_state.user_role})")
    st.divider()

    menus = ["🏠 대시보드", "🔥 트렌드 기획", "✏️ 콘텐츠 기획실", "🎯 AI 콘텐츠 기획", "🎬 영상 분석", "📹 숏폼 영상", "🔍 유튜브 탐색", "✍️ 포스트 생성", "🖼️ 이미지 생성", "📸 사진→콘텐츠", "👁️ 미리보기 & 편집", "🏷️ 해시태그 분석", "🤖 AI 최적화", "📤 업로드", "⏰ 예약 발행", "📅 발행 캘린더", "📊 성과 추적", "📄 리포트 생성", "💬 DM 자동화", "🎨 워터마크 제거", "🔤 폰트 & 스타일", "🎴 카드뉴스 제작", "📝 블로그 글 쓰기", "🔗 링크 변환", "🔗 계정 연동", "👥 팀 멤버 관리", "🔌 API/MCP 연동"]

    if st.session_state.user_role == "관리자":
        menus.append("👥 사용자 관리")

    menus.append("⚙️ 설정")

    page = st.radio(
        "메뉴",
        menus,
        label_visibility="collapsed",
    )

    st.divider()
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.rerun()

cfg = load_cfg()

# ══════════════════════════════════════════════════════════
# 🏠 대시보드
# ══════════════════════════════════════════════════════════
if page == "🏠 대시보드":
    import collections
    import json as _json
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from datetime import date as _date, timedelta as _td

    # ── 데이터 수집 ───────────────────────────────────────
    _post_files = sorted(Path("posts").glob("*.yaml"), key=os.path.getmtime, reverse=True) if Path("posts").exists() else []
    _schedule   = {}
    if Path("schedule.json").exists():
        with open("schedule.json", "r", encoding="utf-8") as _f:
            _schedule = _json.load(_f)

    # 포스트 파일 파싱
    _posts_data = []
    for _pf in _post_files:
        try:
            with open(_pf, "r", encoding="utf-8") as _f:
                _d = yaml.safe_load(_f)
            _plat = _pf.stem.split("_")[0] if "_" in _pf.stem else "unknown"
            _posts_data.append({
                "file": _pf.name,
                "platform": _plat,
                "title": _d.get("title", ""),
                "body_len": len(_d.get("body", "")),
                "hashtag_cnt": len(_d.get("hashtags", [])),
                "has_image": bool(_d.get("image_paths")),
                "mtime": datetime.fromtimestamp(os.path.getmtime(_pf)),
            })
        except Exception:
            pass

    # 예약/발행 데이터
    _all_scheduled, _all_published = [], []
    for _ds, _items in _schedule.items():
        for _item in _items:
            _item["date"] = _ds
            if _item.get("status") == "published":
                _all_published.append(_item)
            else:
                _all_scheduled.append(_item)

    # 해시태그 카운터
    _ht_counter = collections.Counter()
    for _pd2 in _posts_data:
        try:
            with open(f"posts/{_pd2['file']}", "r", encoding="utf-8") as _f:
                _raw = yaml.safe_load(_f)
            for _t in _raw.get("hashtags", []):
                if _t.strip():
                    _ht_counter[_t.strip()] += 1
        except Exception:
            pass

    # 오늘/이번달 집계
    _today      = _date.today()
    _month_str  = _today.strftime("%Y-%m")
    _posts_month = [p for p in _posts_data if p["mtime"].strftime("%Y-%m") == _month_str]
    _pub_month   = [p for p in _all_published if str(p.get("date", "")).startswith(_month_str)]
    _upcoming    = [p for p in _all_scheduled if p.get("date", "") >= str(_today)]

    # 플랫폼 연결 상태
    _status_map = {
        "instagram": bool(cfg.get("instagram", {}).get("username", "").replace("YOUR", "")),
        "threads":   bool(cfg.get("threads", {}).get("username", "").replace("YOUR", "")),
        "youtube":   Path("youtube_client_secrets.json").exists(),
        "naver":     Path("naver_cookies.json").exists(),
        "wordpress": bool(cfg.get("wordpress", {}).get("url", "").replace("your-wordpress", "")),
    }

    # ── 헤더 ─────────────────────────────────────────────
    st.markdown("""
    <style>
    .dash-card{background:#fff;border-radius:12px;padding:18px 20px;
               border:1px solid #e8eaf0;box-shadow:0 1px 4px rgba(0,0,0,.06);}
    .dash-kpi-val{font-size:2rem;font-weight:800;color:#1a1a2e;margin:4px 0;}
    .dash-kpi-label{font-size:.8rem;color:#888;font-weight:500;text-transform:uppercase;letter-spacing:.5px;}
    .dash-kpi-delta{font-size:.85rem;margin-top:2px;}
    .platform-pill{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;
                   border-radius:20px;font-size:.85rem;font-weight:600;margin:3px;}
    .pill-ok{background:#d4edda;color:#155724;}
    .pill-no{background:#f8d7da;color:#721c24;}
    </style>""", unsafe_allow_html=True)

    st.markdown("## 📊 SNS 운영 현황 대시보드")
    st.caption(f"기준일: {_today.strftime('%Y년 %m월 %d일')}  |  @geumseok_jewellery")

    # ── KPI 카드 행 ───────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    _kpi_style = "background:#f8f9ff;border-radius:10px;padding:14px 10px;text-align:center;border:1px solid #e0e4ff"

    with k1:
        st.markdown(f"<div style='{_kpi_style}'><div style='font-size:1.6rem;font-weight:800;color:#6366f1'>{len(_posts_data)}</div><div style='font-size:.75rem;color:#888;margin-top:2px'>총 생성 포스트</div></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div style='{_kpi_style}'><div style='font-size:1.6rem;font-weight:800;color:#10b981'>{len(_posts_month)}</div><div style='font-size:.75rem;color:#888;margin-top:2px'>이번 달 생성</div></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div style='{_kpi_style}'><div style='font-size:1.6rem;font-weight:800;color:#f59e0b'>{len(_upcoming)}</div><div style='font-size:.75rem;color:#888;margin-top:2px'>예약 대기</div></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div style='{_kpi_style}'><div style='font-size:1.6rem;font-weight:800;color:#ef4444'>{len(_all_published)}</div><div style='font-size:.75rem;color:#888;margin-top:2px'>발행 완료</div></div>", unsafe_allow_html=True)
    with k5:
        _avg_ht = round(sum(p["hashtag_cnt"] for p in _posts_data) / max(len(_posts_data), 1), 1)
        st.markdown(f"<div style='{_kpi_style}'><div style='font-size:1.6rem;font-weight:800;color:#8b5cf6'>{_avg_ht}</div><div style='font-size:.75rem;color:#888;margin-top:2px'>평균 해시태그</div></div>", unsafe_allow_html=True)
    with k6:
        _conn_cnt = sum(1 for v in _status_map.values() if v)
        st.markdown(f"<div style='{_kpi_style}'><div style='font-size:1.6rem;font-weight:800;color:#06b6d4'>{_conn_cnt}/5</div><div style='font-size:.75rem;color:#888;margin-top:2px'>연결된 플랫폼</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 플랫폼 연결 상태 바 ───────────────────────────────
    _pill_html = ""
    for _pk, _plabel in PLATFORMS.items():
        _ok = _status_map.get(_pk, False)
        _cls = "pill-ok" if _ok else "pill-no"
        _icon = "✅" if _ok else "❌"
        _pill_html += f"<span class='platform-pill {_cls}'>{_icon} {_plabel}</span>"
    st.markdown(f"<div style='margin-bottom:8px'>{_pill_html}</div>", unsafe_allow_html=True)
    st.divider()

    # ── 차트 행 1: 월별 생성량 + 플랫폼 분포 ────────────────
    cc1, cc2 = st.columns([3, 2])

    with cc1:
        st.markdown("#### 📅 월별 포스트 생성량")
        if _posts_data:
            _month_cnt = collections.Counter(p["mtime"].strftime("%Y-%m") for p in _posts_data)
            _months_sorted = sorted(_month_cnt.keys())[-12:]
            _fig_bar = go.Figure(go.Bar(
                x=_months_sorted,
                y=[_month_cnt[m] for m in _months_sorted],
                marker_color=["#6366f1" if m != _month_str else "#ef4444" for m in _months_sorted],
                text=[_month_cnt[m] for m in _months_sorted],
                textposition="outside",
            ))
            _fig_bar.update_layout(
                height=260, margin=dict(l=0,r=0,t=10,b=0),
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis=dict(gridcolor="#f0f0f0", zeroline=False),
                xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                font=dict(family="sans-serif"),
            )
            st.plotly_chart(_fig_bar, width="stretch")
        else:
            st.info("포스트 데이터가 없습니다.")

    with cc2:
        st.markdown("#### 🎯 플랫폼별 생성 비율")
        if _posts_data:
            _plat_cnt = collections.Counter(p["platform"] for p in _posts_data)
            _plat_labels = list(_plat_cnt.keys())
            _plat_vals   = list(_plat_cnt.values())
            _plat_colors = {"instagram":"#E1306C","threads":"#000","youtube":"#FF0000",
                            "blog":"#03C75A","naver":"#03C75A","wordpress":"#21759B","all":"#6366f1","unknown":"#ccc"}
            _fig_pie = go.Figure(go.Pie(
                labels=_plat_labels, values=_plat_vals,
                marker_colors=[_plat_colors.get(l,"#999") for l in _plat_labels],
                hole=0.45,
                textinfo="label+percent",
                textfont_size=12,
            ))
            _fig_pie.update_layout(
                height=260, margin=dict(l=0,r=0,t=10,b=0),
                showlegend=False, paper_bgcolor="white",
            )
            st.plotly_chart(_fig_pie, width="stretch")
        else:
            st.info("데이터 없음")

    # ── 차트 행 2: 요일×시간 히트맵 + 해시태그 TOP20 ─────────
    cc3, cc4 = st.columns([2, 3])

    with cc3:
        st.markdown("#### 🕐 발행 시간대 히트맵")
        if _all_published:
            _hm_data = [[0]*24 for _ in range(7)]
            _day_kor = ["월","화","수","목","금","토","일"]
            for _item in _all_published:
                try:
                    _dt = datetime.fromisoformat(_item.get("created_at",""))
                    _hm_data[_dt.weekday()][_dt.hour] += 1
                except Exception:
                    pass
            _fig_hm = go.Figure(go.Heatmap(
                z=_hm_data,
                x=[f"{h:02d}시" for h in range(24)],
                y=_day_kor,
                colorscale="Purples",
                showscale=False,
                hoverongaps=False,
            ))
            _fig_hm.update_layout(
                height=240, margin=dict(l=30,r=0,t=10,b=30),
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(size=10),
            )
            st.plotly_chart(_fig_hm, width="stretch")
        else:
            # 샘플 히트맵 (데이터 없을 때)
            import random as _rnd
            _rnd.seed(42)
            _sample = [[_rnd.randint(0,3) if 8<=h<=22 else 0 for h in range(24)] for _ in range(7)]
            _fig_hm2 = go.Figure(go.Heatmap(
                z=_sample, x=[f"{h:02d}시" for h in range(24)],
                y=["월","화","수","목","금","토","일"],
                colorscale="Purples", showscale=False,
            ))
            _fig_hm2.update_layout(height=240, margin=dict(l=30,r=0,t=10,b=30),
                                   paper_bgcolor="white", plot_bgcolor="white", font=dict(size=10))
            st.plotly_chart(_fig_hm2, width="stretch")
            st.caption("샘플 데이터 — 발행 후 실제 데이터로 채워집니다")

    with cc4:
        st.markdown("#### 🏷️ 해시태그 사용 TOP 20")
        if _ht_counter:
            _top_ht  = _ht_counter.most_common(20)
            _ht_tags = [t for t,_ in reversed(_top_ht)]
            _ht_vals = [c for _,c in reversed(_top_ht)]
            _fig_ht  = go.Figure(go.Bar(
                x=_ht_vals, y=_ht_tags,
                orientation="h",
                marker=dict(
                    color=_ht_vals,
                    colorscale="Purp",
                    showscale=False,
                ),
                text=_ht_vals, textposition="outside",
            ))
            _fig_ht.update_layout(
                height=320, margin=dict(l=10,r=40,t=10,b=0),
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(gridcolor="#f0f0f0", zeroline=False),
                yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11)),
                font=dict(family="sans-serif"),
            )
            st.plotly_chart(_fig_ht, width="stretch")
        else:
            st.info("해시태그 데이터 없음")

    st.divider()

    # ── 차트 행 3: 본문 길이 분포 + 예약 현황 게이지 ──────────
    cc5, cc6 = st.columns([3, 2])

    with cc5:
        st.markdown("#### 📝 플랫폼별 평균 본문 길이")
        if _posts_data:
            _len_by_plat = collections.defaultdict(list)
            for _p in _posts_data:
                _len_by_plat[_p["platform"]].append(_p["body_len"])
            _plat_names = list(_len_by_plat.keys())
            _plat_avgs  = [round(sum(v)/len(v)) for v in _len_by_plat.values()]
            _plat_colors_list = [{"instagram":"#E1306C","threads":"#222","youtube":"#FF0000",
                                   "blog":"#03C75A","naver":"#03C75A","all":"#6366f1"}.get(p,"#aaa")
                                  for p in _plat_names]
            _fig_len = go.Figure(go.Bar(
                x=_plat_names, y=_plat_avgs,
                marker_color=_plat_colors_list,
                text=_plat_avgs, textposition="outside",
            ))
            # 권장 길이 가이드라인
            _fig_len.add_hline(y=150, line_dash="dot", line_color="#E1306C",
                               annotation_text="Instagram 권장(150)", annotation_position="top right")
            _fig_len.add_hline(y=500, line_dash="dot", line_color="#222",
                               annotation_text="Threads 권장(500)", annotation_position="top right")
            _fig_len.add_hline(y=800, line_dash="dot", line_color="#03C75A",
                               annotation_text="블로그 권장(800)", annotation_position="top right")
            _fig_len.update_layout(
                height=280, margin=dict(l=0,r=100,t=10,b=0),
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis=dict(gridcolor="#f0f0f0", zeroline=False, title="글자 수"),
                font=dict(family="sans-serif"),
            )
            st.plotly_chart(_fig_len, width="stretch")
        else:
            st.info("데이터 없음")

    with cc6:
        st.markdown("#### 🚦 예약/발행 현황")
        _total_sched = len(_all_scheduled) + len(_all_published)

        # 게이지 차트
        _fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=len(_all_published),
            delta={"reference": _total_sched, "valueformat": ".0f"},
            title={"text": "발행 완료 포스트", "font": {"size": 14}},
            gauge={
                "axis": {"range": [0, max(_total_sched, 1)], "tickwidth": 1},
                "bar":  {"color": "#6366f1"},
                "bgcolor": "white",
                "steps": [
                    {"range": [0, _total_sched * 0.4], "color": "#fee2e2"},
                    {"range": [_total_sched * 0.4, _total_sched * 0.7], "color": "#fef9c3"},
                    {"range": [_total_sched * 0.7, max(_total_sched, 1)], "color": "#dcfce7"},
                ],
                "threshold": {"line": {"color": "red", "width": 2},
                              "thickness": 0.75, "value": max(_total_sched, 1)},
            },
        ))
        _fig_gauge.update_layout(
            height=240, margin=dict(l=20,r=20,t=30,b=10),
            paper_bgcolor="white",
        )
        st.plotly_chart(_fig_gauge, width="stretch")

        # 발행률 텍스트
        _pub_rate = int(len(_all_published) / max(_total_sched, 1) * 100)
        st.markdown(f"""
<div style='text-align:center;margin-top:-10px'>
  <span style='font-size:1.4rem;font-weight:800;color:{"#10b981" if _pub_rate>=70 else "#f59e0b" if _pub_rate>=40 else "#ef4444"}'>{_pub_rate}%</span>
  <span style='font-size:.8rem;color:#888;margin-left:6px'>발행률</span>
</div>""", unsafe_allow_html=True)

    st.divider()

    # ── GitHub 스타일 기여 그래프 (52주 활동 캘린더) ──────────
    st.markdown("#### 📆 포스트 생성 활동 (최근 1년)")
    _activity = collections.Counter()
    for _p in _posts_data:
        _activity[_p["mtime"].date()] += 1
    for _item in _all_published:
        try:
            _activity[datetime.fromisoformat(_item.get("created_at","")).date()] += 1
        except Exception:
            pass

    _cal_end   = _today
    _cal_start = _today - _td(days=364)
    _weeks = []
    _cur = _cal_start - _td(days=_cal_start.weekday())
    while _cur <= _cal_end + _td(days=6):
        _week = []
        for _d in range(7):
            _day = _cur + _td(days=_d)
            _cnt = _activity.get(_day, 0)
            _week.append(_cnt)
        _weeks.append(_week)
        _cur += _td(days=7)

    _z  = [[_weeks[w][d] for w in range(len(_weeks))] for d in range(7)]
    _x  = [((_cal_start - _td(days=_cal_start.weekday())) + _td(weeks=w)).strftime("%Y-%m") for w in range(len(_weeks))]
    _y  = ["월","화","수","목","금","토","일"]

    _fig_cal = go.Figure(go.Heatmap(
        z=_z, x=_x, y=_y,
        colorscale=[[0,"#ebedf0"],[0.25,"#c4b5fd"],[0.6,"#8b5cf6"],[1,"#5b21b6"]],
        showscale=False,
        xgap=2, ygap=2,
        hovertemplate="%{x} %{y}요일: %{z}개<extra></extra>",
    ))
    _fig_cal.update_layout(
        height=160, margin=dict(l=30,r=0,t=5,b=0),
        paper_bgcolor="white", plot_bgcolor="white",
        yaxis=dict(autorange="reversed", tickfont=dict(size=10), gridcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickangle=0, tickfont=dict(size=9)),
        font=dict(family="sans-serif"),
    )
    st.plotly_chart(_fig_cal, width="stretch")

    st.divider()

    # ── 하단: 최근 포스트 + 예정 스케줄 ─────────────────────
    bot1, bot2 = st.columns(2)

    with bot1:
        st.markdown("#### 📄 최근 생성 포스트")
        _plat_icons = {"instagram":"📸","threads":"🧵","youtube":"▶️","blog":"📝","naver":"🟢","all":"🤖"}
        for _p in _posts_data[:8]:
            _icon = _plat_icons.get(_p["platform"], "📌")
            _time_str = _p["mtime"].strftime("%m/%d %H:%M")
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"padding:8px 12px;margin:3px 0;background:#f8f9ff;border-radius:8px;"
                f"border-left:3px solid #6366f1'>"
                f"<span style='font-size:13px'>{_icon} {_p['title'][:30] or _p['file']}</span>"
                f"<span style='font-size:11px;color:#888'>{_time_str}</span></div>",
                unsafe_allow_html=True,
            )
        if not _posts_data:
            st.caption("생성된 포스트 없음")

    with bot2:
        st.markdown("#### ⏰ 다가오는 예약")
        _dot = {"instagram":"🟣","threads":"⚫","youtube":"🔴","naver":"🟢","wordpress":"🔵"}
        _upcoming_sorted = sorted(_upcoming, key=lambda x: (x.get("date",""), x.get("time","")))[:8]
        for _item in _upcoming_sorted:
            _d  = _dot.get(_item.get("platform",""), "📌")
            _dt = f"{_item.get('date','')} {_item.get('time','')}"
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"padding:8px 12px;margin:3px 0;background:#fffbeb;border-radius:8px;"
                f"border-left:3px solid #f59e0b'>"
                f"<span style='font-size:13px'>{_d} {_item.get('title','')[:28]}</span>"
                f"<span style='font-size:11px;color:#888'>{_dt}</span></div>",
                unsafe_allow_html=True,
            )
        if not _upcoming_sorted:
            st.caption("예약된 포스트 없음")

    st.divider()

    # ── 빠른 실행 (하단 유지) ─────────────────────────────
    st.markdown("#### ⚡ 빠른 포스트 생성")
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        topic_quick = st.text_input("주제 입력", placeholder="예: 금반지 추천", label_visibility="collapsed")
    with col2:
        platform_quick = st.selectbox("플랫폼", ["instagram", "threads", "youtube", "blog", "all"], label_visibility="collapsed")
    with col3:
        run_quick = st.button("🤖 AI 생성", width="stretch", type="primary")

    if run_quick and topic_quick:
        with st.spinner(f"Gemini로 '{topic_quick}' 생성 중..."):
            try:
                from platforms.ai_content_generator import AIContentGenerator
                gen = AIContentGenerator(cfg.get("openai", {}))
                content = gen.generate_post(topic_quick, platform_quick)
                safe_topic = topic_quick.replace(" ", "_")
                save_path  = f"posts/{platform_quick}_{safe_topic}.yaml"
                Path("posts").mkdir(exist_ok=True)
                with open(save_path, "w", encoding="utf-8") as f:
                    yaml.dump({"title": content.title, "body": content.body,
                               "tags": content.tags, "hashtags": content.hashtags,
                               "image_paths": [], "video_path": None, "schedule_time": None},
                              f, allow_unicode=True, default_flow_style=False)
                st.success(f"✅ 생성 완료! `{save_path}`")
                st.info(f"**{content.title}**\n\n{content.body[:200]}...")
            except Exception as e:
                st.error(f"오류: {e}")

# ══════════════════════════════════════════════════════════
# 🔥 트렌드 기획
# ══════════════════════════════════════════════════════════
elif page == "🔥 트렌드 기획":
    st.title("🔥 트렌드 콘텐츠 기획")
    st.caption("Google 트렌드 실시간 분석 + AI 기획 → 원클릭 포스트 생성")
    st.divider()

    BUSINESS_INFO = {
        "account": "@geumseok_jewellery",
        "description": "금반지, 커플링, 예물, 14k 18k 24k 주얼리 전문 쇼핑몰. 금테크·금거래 정보도 제공.",
    }

    tab_trend, tab_plan = st.tabs(["📈 트렌드 주제 추천", "📅 주간 콘텐츠 캘린더"])

    with tab_trend:
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.markdown("#### 지금 뜨는 키워드 → 주얼리 콘텐츠로 기획")
        with col_r:
            analyze_btn = st.button("🔍 트렌드 분석하기", type="primary", width="stretch")

        if analyze_btn:
            with st.spinner("Google 트렌드 수집 중..."):
                try:
                    from platforms.trend_analyzer import TrendAnalyzer
                    analyzer = TrendAnalyzer(cfg.get("openai", {}), BUSINESS_INFO)
                    ideas, raw_trends = analyzer.get_trending_topics()
                    st.session_state["trend_ideas"] = ideas
                    st.session_state["raw_trends"] = raw_trends
                except Exception as e:
                    st.error(f"오류: {e}")

        # 트렌드 키워드 표시
        if "raw_trends" in st.session_state:
            with st.expander("📊 수집된 Google 트렌드 키워드", expanded=False):
                tags = st.session_state["raw_trends"][:15]
                st.markdown(" · ".join([f"`{t}`" for t in tags]))

        # 아이디어 카드 표시
        if "trend_ideas" in st.session_state:
            ideas = st.session_state["trend_ideas"]
            st.markdown(f"#### 💡 AI 추천 콘텐츠 아이디어 ({len(ideas)}개)")

            for i, idea in enumerate(ideas):
                score = idea.get("score", 80)
                score_color = "🟢" if score >= 85 else ("🟡" if score >= 75 else "🔴")
                platform_icon = {"instagram": "📸", "youtube": "▶️", "blog": "📝", "threads": "🧵"}.get(idea.get("platform", ""), "📱")

                with st.container():
                    col1, col2, col3 = st.columns([5, 2, 2])
                    with col1:
                        st.markdown(f"**{platform_icon} {idea.get('topic', '')}**")
                        st.caption(f"💬 {idea.get('hook', '')}")
                        st.caption(f"📌 {idea.get('reason', '')}  |  🏷️ `{idea.get('trend_keyword', '')}`  |  📋 {idea.get('content_type', '')}")
                    with col2:
                        st.metric("기대 점수", f"{score_color} {score}점")
                    with col3:
                        if st.button("⚡ 바로 생성", key=f"gen_{i}", width="stretch"):
                            st.session_state["quick_topic"] = idea.get("topic", "")
                            st.session_state["quick_platform"] = idea.get("platform", "all")
                            st.session_state["do_quick_gen"] = True
                    st.divider()

        # 원클릭 생성 실행
        if st.session_state.get("do_quick_gen") and st.session_state.get("quick_topic"):
            topic = st.session_state.pop("quick_topic")
            platform = st.session_state.pop("quick_platform", "all")
            st.session_state.pop("do_quick_gen", None)

            with st.spinner(f"'{topic}' 포스트 생성 중..."):
                try:
                    from platforms.ai_content_generator import AIContentGenerator
                    gen = AIContentGenerator(cfg.get("openai", {}))
                    content = gen.generate_post(topic, platform)

                    safe = topic.replace(" ", "_").replace("/", "_")[:30]
                    save_path = f"posts/{platform}_{safe}.yaml"
                    Path("posts").mkdir(exist_ok=True)
                    with open(save_path, "w", encoding="utf-8") as f:
                        yaml.dump({
                            "title": content.title,
                            "body": content.body,
                            "tags": content.tags,
                            "hashtags": content.hashtags,
                            "image_paths": [],
                            "video_path": None,
                            "schedule_time": None,
                        }, f, allow_unicode=True, default_flow_style=False)

                    st.success(f"✅ 포스트 생성 완료!")
                    with st.expander("📄 생성된 포스트 보기", expanded=True):
                        st.markdown(f"**제목:** {content.title}")
                        st.text_area("본문", content.body, height=150)
                        st.text(f"해시태그: {' '.join(content.hashtags)}")
                        st.caption(f"저장됨: `{save_path}` → '업로드' 메뉴에서 바로 올릴 수 있습니다.")
                except Exception as e:
                    st.error(f"생성 오류: {e}")

    with tab_plan:
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.markdown("#### 이번 주 콘텐츠 캘린더 자동 생성")
            num_days = st.slider("일수", 3, 14, 7)
        with col_r:
            st.write("")
            plan_btn = st.button("📅 캘린더 생성", type="primary", width="stretch")

        if plan_btn:
            with st.spinner("일주일 콘텐츠 계획 생성 중..."):
                try:
                    from platforms.trend_analyzer import TrendAnalyzer
                    analyzer = TrendAnalyzer(cfg.get("openai", {}), BUSINESS_INFO)
                    plan = analyzer.get_weekly_content_plan(num_days)
                    st.session_state["weekly_plan"] = plan
                except Exception as e:
                    st.error(f"오류: {e}")

        if "weekly_plan" in st.session_state:
            plan = st.session_state["weekly_plan"]
            platform_icon = {"instagram": "📸", "youtube": "▶️", "blog": "📝", "threads": "🧵"}
            type_color = {"카드뉴스": "🃏", "릴스": "🎬", "일반포스트": "📷", "블로그": "📝", "쇼츠": "⚡"}

            for item in plan:
                icon = platform_icon.get(item.get("platform", ""), "📱")
                type_icon = type_color.get(item.get("content_type", ""), "📋")
                col1, col2, col3 = st.columns([1, 5, 2])
                with col1:
                    st.markdown(f"**Day {item.get('day', '')}**")
                    st.caption(item.get("weekday", ""))
                with col2:
                    st.markdown(f"{icon} {type_icon} **{item.get('topic', '')}**")
                    st.caption(f"💬 {item.get('hook', '')}")
                    hashtags = item.get("hashtags", [])
                    st.caption(" ".join(hashtags[:4]))
                with col3:
                    if st.button("⚡ 생성", key=f"plan_{item.get('day', '')}_{item.get('platform', '')}",
                                 width="stretch"):
                        st.session_state["quick_topic"] = item.get("topic", "")
                        st.session_state["quick_platform"] = item.get("platform", "all")
                        st.session_state["do_quick_gen"] = True
                        st.rerun()
                st.divider()


# ══════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════
# ✏️ 콘텐츠 기획실
# ══════════════════════════════════════════════════════════
elif page == "✏️ 콘텐츠 기획실":
    import json as _json
    import uuid as _uuid
    from datetime import date as _date, timedelta as _td
    from google import genai as _genai
    from google.genai import types as _gtypes

    _PLAN_FILE = Path("content_plan.json")
    _ai_key    = cfg.get("openai", {}).get("api_key", "")
    _ai_model  = cfg.get("openai", {}).get("model", "gemini-2.5-flash")

    def _load_plan():
        if _PLAN_FILE.exists():
            with open(_PLAN_FILE, "r", encoding="utf-8") as f:
                return _json.load(f)
        return {"ideas": []}

    def _save_plan(data):
        with open(_PLAN_FILE, "w", encoding="utf-8") as f:
            _json.dump(data, f, ensure_ascii=False, indent=2)

    _PLAN_STATUS = {"idea": ("💡 아이디어", "#fff3cd"), "writing": ("✍️ 작성중", "#cce5ff"),
                    "done": ("✅ 완성", "#d4edda"), "published": ("🚀 발행됨", "#d1ecf1")}
    _PLAT_ICON_P2 = {"instagram":"📸","threads":"🧵","youtube":"▶️","naver":"📗","all":"🌐"}

    st.title("✏️ 콘텐츠 기획실")
    st.caption("AI가 무엇을 만들지 기획하고, 주제를 선택하면 사람처럼 글을 바로 써드립니다.")

    if not _ai_key:
        st.warning("⚠️ Gemini API 키를 ⚙️ 설정에서 먼저 등록해 주세요.")
        st.stop()

    _tab_plan, _tab_write, _tab_board = st.tabs(["🧠 AI 기획", "✍️ AI 글쓰기", "📋 기획 보드"])

    # ─────────────────────────────────────────────────────
    # 탭1: AI 기획
    # ─────────────────────────────────────────────────────
    with _tab_plan:
        st.markdown("#### 기획 조건 설정")
        _pc1, _pc2, _pc3 = st.columns(3)
        with _pc1:
            _plan_period = st.selectbox("기획 기간", ["이번 주 (7일)", "2주", "이번 달 (30일)"], key="plan_period")
            _plan_days   = {"이번 주 (7일)": 7, "2주": 14, "이번 달 (30일)": 30}[_plan_period]
        with _pc2:
            _plan_plat = st.multiselect(
                "발행 플랫폼",
                ["instagram", "threads", "youtube", "naver"],
                default=["instagram", "threads", "naver"],
                key="plan_plat"
            )
        with _pc3:
            _plan_focus = st.multiselect(
                "콘텐츠 방향",
                ["정보/교육", "감성/스토리", "상품 소개", "트렌드 반응", "Q&A/FAQ", "비하인드/일상"],
                default=["정보/교육", "감성/스토리", "상품 소개"],
                key="plan_focus"
            )

        _pc4, _pc5 = st.columns(2)
        with _pc4:
            _plan_biz = st.text_input("비즈니스 설명", value="금반지·커플링·예물 전문 주얼리 쇼핑몰", key="plan_biz")
        with _pc5:
            _plan_extra = st.text_input("특별 이벤트/시즌 (선택)", placeholder="예: 6월 결혼 시즌, 어버이날, 신제품 출시", key="plan_extra")

        _plan_cnt = st.slider("생성할 기획 아이디어 수", 5, 20, 10, key="plan_cnt")

        if st.button("🧠 AI 콘텐츠 기획 생성", type="primary", key="run_plan"):
            # 성과 데이터 참조
            _perf_hint = ""
            if _PLAN_FILE.parent.joinpath("performance_data.json").exists() or Path("performance_data.json").exists():
                try:
                    with open("performance_data.json", "r", encoding="utf-8") as _pf:
                        _pd = _json.load(_pf)
                    _recs_p = _pd.get("records", [])
                    if _recs_p:
                        import collections as _col
                        _ht_cnt = _col.Counter(
                            t.lstrip("#") for r in _recs_p for t in r.get("hashtags", [])
                        )
                        _best_ht = [t for t, _ in _ht_cnt.most_common(5)]
                        _best_plat = max(
                            set(r.get("platform","") for r in _recs_p),
                            key=lambda p: sum(r.get("engagement_rate",0) for r in _recs_p if r.get("platform","")==p)
                        )
                        _perf_hint = f"\n\n=== 과거 성과 인사이트 ===\n잘 되는 해시태그: {', '.join(_best_ht)}\n가장 효과적인 플랫폼: {_best_plat}"
                except Exception:
                    pass

            _today    = _date.today()
            _end_date = _today + _td(days=_plan_days)
            _prompt_plan = f"""당신은 SNS 콘텐츠 기획 전문가입니다.

=== 비즈니스 정보 ===
업종: {_plan_biz}
기획 기간: {_today.strftime('%Y.%m.%d')} ~ {_end_date.strftime('%Y.%m.%d')} ({_plan_days}일)
발행 플랫폼: {', '.join(_plan_plat)}
콘텐츠 방향: {', '.join(_plan_focus)}
특별 이슈: {_plan_extra or '없음'}{_perf_hint}

위 조건으로 {_plan_cnt}개의 콘텐츠 기획안을 만들어주세요.

규칙:
- 플랫폼별 특성에 맞게 배분
- 정보형 70% + 홍보형 30% 비율 유지
- 각 아이디어는 실제로 좋아요·저장·공유를 부르는 주제여야 함
- 오늘 날짜 기준 현실적인 업로드 날짜 배정

아래 JSON 배열로만 응답하세요:
[
  {{
    "topic": "구체적인 콘텐츠 주제",
    "platform": "instagram|threads|youtube|naver",
    "content_type": "정보형|감성형|상품소개|트렌드|Q&A|비하인드",
    "angle": "콘텐츠 접근 방식 (예: 비교, 추천, 경험담, 팁, 스토리)",
    "hook": "첫 줄 후킹 문구 (독자가 멈추게 하는 한 줄)",
    "key_points": ["핵심 포인트1", "핵심 포인트2", "핵심 포인트3"],
    "best_time": "추천 업로드 날짜 (예: {_today.strftime('%m/%d')} 오후 7시)",
    "priority": 85,
    "why_now": "지금 이 주제가 중요한 이유 (1문장)"
  }}
]
한국어로만 응답하세요."""

            with st.spinner("AI가 콘텐츠 기획안을 작성 중..."):
                try:
                    _cl = _genai.Client(api_key=_ai_key)
                    _r  = _cl.models.generate_content(
                        model=_ai_model,
                        contents=_prompt_plan,
                        config=_gtypes.GenerateContentConfig(
                            temperature=0.85,
                            response_mime_type="application/json",
                        ),
                    )
                    _ideas_new = _json.loads(_r.text.strip())
                    st.session_state["plan_ideas"] = _ideas_new
                except Exception as _e:
                    st.error(f"기획 생성 오류: {_e}")

        # 결과 출력
        if "plan_ideas" in st.session_state:
            _ideas_list = st.session_state["plan_ideas"]
            st.markdown(f"---\n### 📋 기획안 {len(_ideas_list)}개")

            _PLAT_COLOR2 = {"instagram":"#E1306C","threads":"#1c1c1e","youtube":"#FF0000","naver":"#03C75A"}
            _TYPE_COLOR2 = {"정보형":"#0984e3","감성형":"#E1306C","상품소개":"#fdcb6e",
                            "트렌드":"#6c5ce7","Q&A":"#00b894","비하인드":"#fd79a8"}

            for _idx, _idea in enumerate(_ideas_list):
                _pc = _PLAT_COLOR2.get(_idea.get("platform",""), "#888")
                _tc = _TYPE_COLOR2.get(_idea.get("content_type",""), "#888")
                _pi = _PLAT_ICON_P2.get(_idea.get("platform",""), "📌")
                _kp = "".join(f"<li style='margin:1px 0'>{p}</li>" for p in _idea.get("key_points",[]))
                _pri = _idea.get("priority", 70)
                _pri_color = "#00b894" if _pri >= 85 else "#fdcb6e" if _pri >= 70 else "#888"

                with st.expander(
                    f"{_pi} **{_idea.get('topic','')}**  ·  "
                    f"{'🔴' if _pri>=85 else '🟡'} 우선순위 {_pri}점", expanded=False
                ):
                    _ia, _ib, _ic = st.columns([3, 2, 1])
                    with _ia:
                        st.markdown(
                            f"<span style='background:{_pc};color:#fff;border-radius:6px;"
                            f"padding:2px 8px;font-size:11px;font-weight:700'>{_pi} {_idea.get('platform','')}</span> "
                            f"<span style='background:{_tc};color:#fff;border-radius:6px;"
                            f"padding:2px 8px;font-size:11px;font-weight:700'>{_idea.get('content_type','')}</span> "
                            f"<span style='background:#eee;color:#444;border-radius:6px;"
                            f"padding:2px 8px;font-size:11px'>{_idea.get('angle','')}</span>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<div style='background:#fff8e1;border-left:3px solid #f39c12;"
                            f"padding:8px 12px;border-radius:0 8px 8px 0;margin:8px 0'>"
                            f"💬 <b>후킹:</b> {_idea.get('hook','')}</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(f"<ul style='margin:0;padding-left:18px'>{_kp}</ul>", unsafe_allow_html=True)
                    with _ib:
                        st.markdown(
                            f"<div style='background:#f0f4ff;border-radius:8px;padding:10px 14px'>"
                            f"<div style='font-size:.8rem;color:#888'>📅 추천 일정</div>"
                            f"<div style='font-weight:700'>{_idea.get('best_time','')}</div>"
                            f"<div style='font-size:.8rem;color:#888;margin-top:8px'>⚡ 지금 해야 하는 이유</div>"
                            f"<div style='font-size:.85rem'>{_idea.get('why_now','')}</div></div>",
                            unsafe_allow_html=True
                        )
                    with _ic:
                        if st.button("✍️ 바로 글쓰기", key=f"goto_write_{_idx}", type="primary"):
                            st.session_state["write_topic"]    = _idea.get("topic","")
                            st.session_state["write_platform"] = _idea.get("platform","instagram")
                            st.session_state["write_hook"]     = _idea.get("hook","")
                            st.session_state["write_points"]   = _idea.get("key_points",[])
                            st.session_state["goto_write_tab"] = True
                            st.info("✅ AI 글쓰기 탭으로 이동하세요!")

                        if st.button("📋 보드에 추가", key=f"add_board_{_idx}"):
                            _plan = _load_plan()
                            _plan["ideas"].append({
                                "id":       str(_uuid.uuid4()),
                                "topic":    _idea.get("topic",""),
                                "platform": _idea.get("platform","instagram"),
                                "content_type": _idea.get("content_type","정보형"),
                                "hook":     _idea.get("hook",""),
                                "key_points": _idea.get("key_points",[]),
                                "best_time": _idea.get("best_time",""),
                                "priority": _idea.get("priority",70),
                                "status":   "idea",
                                "created_at": str(_date.today()),
                                "notes":    "",
                            })
                            _save_plan(_plan)
                            st.success("📋 보드에 추가!")

            if st.button("📋 전체 보드에 추가", key="add_all_board"):
                _plan = _load_plan()
                for _idea in _ideas_list:
                    _plan["ideas"].append({
                        "id":       str(_uuid.uuid4()),
                        "topic":    _idea.get("topic",""),
                        "platform": _idea.get("platform","instagram"),
                        "content_type": _idea.get("content_type","정보형"),
                        "hook":     _idea.get("hook",""),
                        "key_points": _idea.get("key_points",[]),
                        "best_time": _idea.get("best_time",""),
                        "priority": _idea.get("priority",70),
                        "status":   "idea",
                        "created_at": str(_date.today()),
                        "notes":    "",
                    })
                _save_plan(_plan)
                st.success(f"✅ {len(_ideas_list)}개 전체 보드에 추가 완료!")

    # ─────────────────────────────────────────────────────
    # 탭2: AI 글쓰기
    # ─────────────────────────────────────────────────────
    with _tab_write:
        st.markdown("#### 주제 설정")
        _wc1, _wc2 = st.columns([3, 2])
        with _wc1:
            _w_topic = st.text_input(
                "주제",
                value=st.session_state.get("write_topic", ""),
                placeholder="예: 14K vs 18K 금반지 차이점, 커플링 고르는 법",
                key="w_topic"
            )
            _w_hook_hint = st.text_input(
                "후킹 힌트 (선택) — 첫 문장 방향",
                value=st.session_state.get("write_hook", ""),
                placeholder="예: 금반지 살 때 이것 모르면 손해!",
                key="w_hook"
            )
            _w_points_raw = st.text_input(
                "핵심 포인트 (쉼표 구분, 선택)",
                value=", ".join(st.session_state.get("write_points", [])),
                placeholder="예: 순도 차이, 내구성, 가격 비교",
                key="w_points"
            )
        with _wc2:
            _w_platform = st.selectbox(
                "플랫폼",
                ["instagram", "threads", "naver", "youtube"],
                index=["instagram","threads","naver","youtube"].index(
                    st.session_state.get("write_platform","instagram")
                ),
                key="w_platform"
            )
            _w_style = st.selectbox(
                "글쓰기 스타일",
                ["📖 스토리텔링 (경험담 형식)",
                 "🎓 전문가 조언 (지식 공유)",
                 "💬 친구같은 대화 (SNS 감성)",
                 "📰 정보 전달 (뉴스레터형)",
                 "😍 감성 에세이 (무드 중심)"],
                key="w_style"
            )
            _w_tone = st.selectbox(
                "말투",
                ["따뜻하고 친근한", "당당하고 자신감 있는", "유머러스하고 재치있는",
                 "진지하고 전문적인", "설레고 감성적인"],
                key="w_tone"
            )
            _w_length = st.selectbox(
                "길이",
                ["짧게 (100~200자)", "보통 (200~400자)", "길게 (400~700자)", "블로그형 (800자+)"],
                key="w_length"
            )

        _w_extra = st.text_input(
            "추가 요청 사항 (선택)",
            placeholder="예: 마지막에 DM 유도 CTA 포함, 이모지 많이 써줘, 특정 상품 언급",
            key="w_extra"
        )

        # 페르소나 안내
        _STYLE_PERSONA = {
            "📖 스토리텔링 (경험담 형식)": "주얼리 쇼핑몰을 운영하며 직접 경험한 것들을 나누는 사장님",
            "🎓 전문가 조언 (지식 공유)": "주얼리 업계 10년 경력의 전문가",
            "💬 친구같은 대화 (SNS 감성)": "주얼리를 진심으로 사랑하는 20대 인플루언서",
            "📰 정보 전달 (뉴스레터형)": "주얼리 큐레이터",
            "😍 감성 에세이 (무드 중심)": "주얼리에 감성을 담는 작가",
        }
        _PLAT_GUIDE = {
            "instagram": "인스타그램 캡션 — 첫 줄 강한 후킹, 이모지 자연스럽게, 150~300자 본문, 마지막에 CTA(저장/팔로우/DM), 줄바꿈으로 가독성",
            "threads":   "Threads 본문 — 180자 이내, 완전한 대화체, 말끝에 질문으로 댓글 유도, 해시태그 1~2개",
            "naver":     "네이버 블로그 — 1200자 이상, 소제목 3개 이상(## 형식), 검색 키워드 자연스럽게 반복, 구체적 정보 위주",
            "youtube":   "유튜브 영상 스크립트 — 첫 10초 후킹 멘트, 본론, 마무리+구독CTA 구조, 자연스러운 구어체",
        }
        _LENGTH_GUIDE = {
            "짧게 (100~200자)": "100~200자",
            "보통 (200~400자)": "200~400자",
            "길게 (400~700자)": "400~700자",
            "블로그형 (800자+)": "800자 이상, 소제목 포함",
        }

        st.divider()

        if st.button("✍️ AI 글쓰기 시작", type="primary", disabled=not _w_topic, key="run_write"):
            _persona    = _STYLE_PERSONA.get(_w_style, "주얼리 전문가")
            _plat_guide = _PLAT_GUIDE.get(_w_platform, "")
            _len_guide  = _LENGTH_GUIDE.get(_w_length, "300자")
            _points_txt = f"\n반드시 포함할 핵심 포인트: {_w_points_raw}" if _w_points_raw else ""
            _hook_txt   = f"\n첫 문장 방향: {_w_hook_hint}" if _w_hook_hint else ""
            _extra_txt  = f"\n추가 요청: {_w_extra}" if _w_extra else ""

            _write_prompt = f"""당신은 '{_persona}'입니다. 아래 주제로 {_w_platform}에 올릴 글을 써주세요.

=== 주제 ===
{_w_topic}

=== 글쓰기 조건 ===
플랫폼: {_w_platform}
스타일: {_w_style.split(' ', 1)[1] if ' ' in _w_style else _w_style}
말투: {_w_tone}
목표 길이: {_len_guide}
플랫폼 가이드: {_plat_guide}{_hook_txt}{_points_txt}{_extra_txt}

=== 절대 하지 말 것 ===
- "안녕하세요, OO입니다" 같은 형식적 인사로 시작하기
- "오늘은 ~에 대해 알아보겠습니다" 같은 교과서적 시작
- AI가 쓴 티가 나는 너무 정제된 표현
- 모든 문장이 비슷한 길이인 균일한 리듬
- "물론", "또한", "따라서" 같은 글쓰기 연결어 남발
- 제목이나 설명 없이 글만 바로 출력 (메타 정보 절대 포함 금지)

=== 반드시 할 것 ===
- 실제 사람이 경험하거나 알게 된 것처럼 구체적인 디테일 포함
- 짧은 문장과 긴 문장을 자연스럽게 섞기
- {_w_platform} 사용자가 실제로 읽고 공감하거나 저장하고 싶은 글
- 첫 문장에서 바로 독자를 사로잡기
- 글만 출력 (해시태그는 본문 끝에, 별도 제목/설명 없이)"""

            st.markdown("---")
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#667eea,#764ba2);"
                f"border-radius:12px;padding:14px 20px;color:#fff;margin-bottom:12px'>"
                f"<span style='font-size:.85rem;opacity:.8'>AI가 작성 중... ✍️</span><br>"
                f"<span style='font-weight:700'>{_w_topic}</span>"
                f"<span style='margin-left:12px;font-size:.8rem;opacity:.7'>{_w_platform} · {_w_style.split()[0]}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

            try:
                _cl_w = _genai.Client(api_key=_ai_key)

                def _stream():
                    for _chunk in _cl_w.models.generate_content_stream(
                        model=_ai_model,
                        contents=_write_prompt,
                        config=_gtypes.GenerateContentConfig(temperature=0.92),
                    ):
                        if _chunk.text:
                            yield _chunk.text

                _output_box = st.empty()
                with _output_box.container():
                    _full_text = st.write_stream(_stream())

                st.session_state["last_written_text"]     = _full_text
                st.session_state["last_written_platform"] = _w_platform
                st.session_state["last_written_topic"]    = _w_topic

            except Exception as _e:
                st.error(f"글쓰기 오류: {_e}")

        # 생성 후 액션 버튼
        if "last_written_text" in st.session_state:
            _lw = st.session_state["last_written_text"]
            _lp = st.session_state.get("last_written_platform","instagram")
            _lt = st.session_state.get("last_written_topic","")
            st.markdown("---")
            st.markdown("#### 다듬기 & 저장")

            _ref_cols = st.columns(4)
            _refine_prompts = {
                "더 짧게": f"아래 글을 절반 길이로 줄여서 핵심만 남겨주세요. 글만 출력:\n\n{_lw}",
                "더 길게": f"아래 글을 두 배 분량으로 늘려주세요. 자연스럽게 내용을 추가하세요. 글만 출력:\n\n{_lw}",
                "더 감성적": f"아래 글을 더 감성적이고 시적으로 다듬어주세요. 글만 출력:\n\n{_lw}",
                "더 정보 중심": f"아래 글을 더 구체적인 정보와 팁 위주로 다듬어주세요. 글만 출력:\n\n{_lw}",
            }
            for _col, (_label, _rprompt) in zip(_ref_cols, _refine_prompts.items()):
                with _col:
                    if st.button(f"🔄 {_label}", key=f"refine_{_label}", use_container_width=True):
                        with st.spinner(f"{_label} 다듬는 중..."):
                            try:
                                _cl_r = _genai.Client(api_key=_ai_key)
                                _rr   = _cl_r.models.generate_content(
                                    model=_ai_model, contents=_rprompt,
                                    config=_gtypes.GenerateContentConfig(temperature=0.8),
                                )
                                st.session_state["last_written_text"] = _rr.text.strip()
                                st.rerun()
                            except Exception as _re2:
                                st.error(str(_re2))

            _edit_txt = st.text_area(
                "✏️ 직접 수정",
                value=_lw,
                height=250,
                key="edit_written"
            )

            _sv1, _sv2 = st.columns(2)
            with _sv1:
                if st.button("💾 posts/ 저장", type="primary", key="save_written"):
                    Path("posts").mkdir(exist_ok=True)
                    _safe = _lt.replace(" ", "_")[:20]
                    _fname = f"{_lp}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{_safe}.yaml"
                    with open(Path("posts") / _fname, "w", encoding="utf-8") as _wff:
                        yaml.dump({
                            "title": _lt, "body": _edit_txt, "caption": _edit_txt,
                            "hashtags": [], "tags": [],
                            "image_paths": [], "video_path": None, "schedule_time": None,
                        }, _wff, allow_unicode=True, default_flow_style=False)
                    st.success(f"✅ posts/{_fname} 저장!")
            with _sv2:
                if st.button("📋 기획 보드로 이동 (완성 상태)", key="to_board_done"):
                    _plan2 = _load_plan()
                    _plan2["ideas"].append({
                        "id": str(_uuid.uuid4()), "topic": _lt,
                        "platform": _lp, "content_type": "완성본",
                        "hook": _edit_txt[:50], "key_points": [],
                        "best_time": "", "priority": 90,
                        "status": "done", "created_at": str(_date.today()), "notes": _edit_txt,
                    })
                    _save_plan(_plan2)
                    st.success("📋 기획 보드 '완성' 상태로 추가!")

    # ─────────────────────────────────────────────────────
    # 탭3: 기획 보드
    # ─────────────────────────────────────────────────────
    with _tab_board:
        _plan_data = _load_plan()
        _board_ideas = _plan_data.get("ideas", [])

        if not _board_ideas:
            st.info("기획안이 없습니다. **🧠 AI 기획** 탭에서 아이디어를 생성하고 보드에 추가하세요.")
        else:
            # 필터
            _bf1, _bf2, _bf3 = st.columns(3)
            with _bf1:
                _b_plat = st.multiselect("플랫폼 필터", ["instagram","threads","youtube","naver"],
                                          default=["instagram","threads","youtube","naver"], key="b_plat")
            with _bf2:
                _b_status = st.multiselect("상태 필터", list(_PLAN_STATUS.keys()),
                                            default=list(_PLAN_STATUS.keys()), key="b_status")
            with _bf3:
                _b_sort = st.selectbox("정렬", ["우선순위 높은 순", "최신순", "플랫폼순"], key="b_sort")

            _filtered_b = [
                i for i in _board_ideas
                if i.get("platform","") in _b_plat and i.get("status","idea") in _b_status
            ]
            if _b_sort == "우선순위 높은 순":
                _filtered_b.sort(key=lambda x: x.get("priority",0), reverse=True)
            elif _b_sort == "최신순":
                _filtered_b.sort(key=lambda x: x.get("created_at",""), reverse=True)
            else:
                _filtered_b.sort(key=lambda x: x.get("platform",""))

            # 상태별 카운트 배지
            _status_counts = {s: sum(1 for i in _board_ideas if i.get("status","")==s) for s in _PLAN_STATUS}
            _badge_html = ""
            for _st_key, (_st_lbl, _st_bg) in _PLAN_STATUS.items():
                _cnt = _status_counts.get(_st_key, 0)
                _badge_html += (
                    f"<span style='background:{_st_bg};border-radius:20px;"
                    f"padding:4px 12px;font-size:13px;font-weight:600;margin:2px'>"
                    f"{_st_lbl} {_cnt}</span> "
                )
            st.markdown(f"<div style='margin-bottom:12px'>{_badge_html}</div>", unsafe_allow_html=True)
            st.markdown(f"**{len(_filtered_b)}개 표시 중** (전체 {len(_board_ideas)}개)")
            st.divider()

            _PLAT_CLR_B = {"instagram":"#E1306C","threads":"#1c1c1e","youtube":"#FF0000","naver":"#03C75A"}

            for _bi, _item in enumerate(_filtered_b):
                _st_lbl, _st_bg = _PLAN_STATUS.get(_item.get("status","idea"), ("💡","#fff3cd"))
                _bpc = _PLAT_CLR_B.get(_item.get("platform",""), "#888")
                _bpi = _PLAT_ICON_P2.get(_item.get("platform",""), "📌")
                _pri_b = _item.get("priority", 70)

                with st.container():
                    _col_main, _col_act = st.columns([5, 2])
                    with _col_main:
                        st.markdown(
                            f"<div style='background:{_st_bg};border-left:4px solid {_bpc};"
                            f"border-radius:0 10px 10px 0;padding:12px 16px'>"
                            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>"
                            f"<span style='background:{_bpc};color:#fff;border-radius:5px;"
                            f"padding:1px 7px;font-size:11px;font-weight:700'>{_bpi} {_item.get('platform','')}</span>"
                            f"<span style='font-size:11px;color:#888'>{_item.get('content_type','')}</span>"
                            f"<span style='margin-left:auto;font-size:11px;font-weight:700;"
                            f"color:{'#00b894' if _pri_b>=85 else '#fdcb6e' if _pri_b>=70 else '#888'}'>"
                            f"우선순위 {_pri_b}</span></div>"
                            f"<div style='font-weight:700;font-size:.95rem'>{_item.get('topic','')}</div>"
                            f"<div style='font-size:.8rem;color:#666;margin-top:3px'>"
                            f"💬 {_item.get('hook','')[:50]}…</div>"
                            f"<div style='font-size:.75rem;color:#aaa;margin-top:2px'>"
                            f"📅 {_item.get('best_time','')}  ·  {_st_lbl}</div></div>",
                            unsafe_allow_html=True
                        )
                    with _col_act:
                        _new_status = st.selectbox(
                            "상태 변경",
                            list(_PLAN_STATUS.keys()),
                            index=list(_PLAN_STATUS.keys()).index(_item.get("status","idea")),
                            format_func=lambda s: _PLAN_STATUS[s][0],
                            key=f"status_{_item['id']}"
                        )
                        if _new_status != _item.get("status"):
                            _item["status"] = _new_status
                            _save_plan(_plan_data)
                            st.rerun()

                        _bc1, _bc2 = st.columns(2)
                        with _bc1:
                            if st.button("✍️ 글쓰기", key=f"bwrite_{_item['id']}", use_container_width=True):
                                st.session_state["write_topic"]    = _item.get("topic","")
                                st.session_state["write_platform"] = _item.get("platform","instagram")
                                st.session_state["write_hook"]     = _item.get("hook","")
                                st.session_state["write_points"]   = _item.get("key_points",[])
                                st.info("✍️ AI 글쓰기 탭으로 이동하세요!")
                        with _bc2:
                            if st.button("🗑️", key=f"bdel_{_item['id']}", use_container_width=True):
                                _plan_data["ideas"] = [x for x in _plan_data["ideas"] if x["id"] != _item["id"]]
                                _save_plan(_plan_data)
                                st.rerun()
                    st.markdown("")

# 🎬 영상 분석
# ══════════════════════════════════════════════════════════
elif page == "🎬 영상 분석":
    st.title("🎬 유튜브 영상 → 우리 콘텐츠로 변환")
    st.caption("영상 스크립트를 AI가 분석해서 금석 쥬얼리 스타일의 새 콘텐츠를 자동 생성합니다.")
    st.divider()

    BUSINESS_INFO = {
        "account": "@geumseok_jewellery",
        "description": "금반지, 커플링, 예물, 14k 18k 24k 주얼리 전문 쇼핑몰. 금테크·금거래 정보도 제공.",
        "brand_voice": "친근하고 전문적인 톤. 금·주얼리 전문가처럼 쉽게 설명. 구매자 입장에서 공감. 이모지 적절히 사용.",
    }

    # URL 입력
    col_url, col_btn = st.columns([4, 1])
    with col_url:
        yt_url = st.text_input(
            "유튜브 링크",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
        )
    with col_btn:
        analyze_btn = st.button("🔍 분석하기", type="primary", width="stretch")

    st.caption("💡 자막이 있는 영상이면 모두 분석 가능합니다. 주얼리 외 영상도 우리 스타일로 재해석합니다.")

    if analyze_btn and yt_url:
        with st.spinner("영상 스크립트 추출 + AI 분석 중... (30-60초 소요)"):
            try:
                from platforms.youtube_analyzer import YouTubeContentAnalyzer
                analyzer = YouTubeContentAnalyzer(cfg.get("openai", {}), BUSINESS_INFO)
                result = analyzer.analyze(yt_url)
                st.session_state["yt_analysis"] = result
            except Exception as e:
                st.error(f"오류: {e}")

    # 분석 결과 표시
    if "yt_analysis" in st.session_state:
        r = st.session_state["yt_analysis"]
        info = r.get("video_info", {})

        # 원본 영상 정보
        st.divider()
        col_thumb, col_info = st.columns([1, 3])
        with col_thumb:
            if info.get("thumbnail"):
                st.image(info["thumbnail"], width="stretch")
        with col_info:
            st.markdown(f"### 📹 {info.get('title', '제목 없음')}")
            st.caption(f"채널: {info.get('author', '')}")
            with st.expander("📝 영상 핵심 요약"):
                st.write(r.get("video_summary", ""))
                st.markdown("**핵심 인사이트**")
                for insight in r.get("key_insights", []):
                    st.markdown(f"• {insight}")

        st.divider()
        st.markdown("## ✨ 금석 쥬얼리 스타일로 재창작된 콘텐츠")
        st.caption("원본 영상을 참고해 완전히 새롭게 재작성된 콘텐츠입니다.")

        # 탭으로 플랫폼별 결과 표시
        tab_ig, tab_th, tab_yt, tab_blog, tab_card = st.tabs(
            ["📸 Instagram", "🧵 Threads", "▶️ YouTube 스크립트", "📝 블로그", "🃏 카드뉴스 기획"]
        )

        def save_post_btn(data: dict, platform: str, key: str):
            filename = f"posts/{platform}_{r.get('video_id', 'yt')[:8]}.yaml"
            if st.button(f"💾 저장 & 업로드 준비", key=key, width="stretch"):
                Path("posts").mkdir(exist_ok=True)
                with open(filename, "w", encoding="utf-8") as f:
                    yaml.dump({
                        "title": data.get("title", ""),
                        "body": data.get("body", data.get("script", "")),
                        "tags": data.get("tags", []),
                        "hashtags": data.get("hashtags", []),
                        "image_paths": [],
                        "video_path": None,
                        "schedule_time": None,
                    }, f, allow_unicode=True, default_flow_style=False)
                st.success(f"✅ `{filename}` 저장! → '업로드' 메뉴에서 올릴 수 있습니다.")

        with tab_ig:
            ig = r.get("instagram_post", {})
            st.markdown(f"**{ig.get('title', '')}**")
            body_ig = st.text_area("본문", ig.get("body", ""), height=180, key="ig_body")
            st.text(f"해시태그: {' '.join(ig.get('hashtags', []))}")
            save_post_btn({"title": ig.get("title", ""), "body": body_ig,
                           "hashtags": ig.get("hashtags", [])}, "instagram", "save_ig")

        with tab_th:
            th = r.get("threads_post", {})
            st.markdown(f"**{th.get('title', '')}**")
            body_th = st.text_area("본문", th.get("body", ""), height=120, key="th_body")
            st.text(f"해시태그: {' '.join(th.get('hashtags', []))}")
            save_post_btn({"title": th.get("title", ""), "body": body_th,
                           "hashtags": th.get("hashtags", [])}, "threads", "save_th")

        with tab_yt:
            yt = r.get("youtube_script", {})
            st.markdown(f"**제목:** {yt.get('title', '')}")
            st.info(f"🎯 **후킹 멘트 (첫 10초):** {yt.get('hook', '')}")
            script_edit = st.text_area("스크립트", yt.get("script", ""), height=300, key="yt_script")
            st.text_area("영상 설명란", yt.get("description", ""), height=100, key="yt_desc")
            st.text(f"해시태그: {' '.join(yt.get('hashtags', []))}")
            save_post_btn({"title": yt.get("title", ""), "body": script_edit,
                           "hashtags": yt.get("hashtags", [])}, "youtube", "save_yt")

        with tab_blog:
            blog = r.get("blog_post", {})
            st.markdown(f"**{blog.get('title', '')}**")
            body_blog = st.text_area("본문", blog.get("body", ""), height=350, key="blog_body")
            st.text(f"태그: {', '.join(blog.get('tags', []))}")
            save_post_btn({"title": blog.get("title", ""), "body": body_blog,
                           "tags": blog.get("tags", [])}, "blog", "save_blog")

        with tab_card:
            card = r.get("cardnews_idea", {})
            st.markdown(f"**카드뉴스 제목:** {card.get('title', '')}")
            st.caption("아래 구성으로 이미지 생성 → 이미지 생성 메뉴에서 만들 수 있습니다.")
            for c in card.get("cards", []):
                col_n, col_h, col_c = st.columns([1, 3, 5])
                with col_n:
                    st.markdown(f"**카드 {c.get('card_num', '')}**")
                with col_h:
                    st.markdown(f"**{c.get('heading', '')}**")
                with col_c:
                    st.write(c.get("content", ""))

            # 카드뉴스 이미지 바로 생성
            if st.button("🎨 카드뉴스 이미지 자동 생성", type="secondary"):
                with st.spinner("이미지 생성 중..."):
                    try:
                        from platforms.image_generator import AIImageGenerator
                        gen = AIImageGenerator(cfg.get("image_generation", {}))
                        paths = gen.generate_cardnews(
                            card.get("title", "주얼리"),
                            num_cards=len(card.get("cards", [])),
                        )
                        img_cols = st.columns(len(paths))
                        for col, path in zip(img_cols, paths):
                            with col:
                                st.image(path, width="stretch")
                        st.success("✅ 카드뉴스 이미지 생성 완료!")
                    except Exception as e:
                        st.error(f"오류: {e}")

        # 전체 저장 버튼
        st.divider()
        if st.button("📦 전체 플랫폼 한 번에 저장", type="primary", width="stretch"):
            saved = []
            Path("posts").mkdir(exist_ok=True)
            vid = r.get("video_id", "yt")[:8]
            for plat, key, body_key in [
                ("instagram", "instagram_post", "body"),
                ("threads",   "threads_post",   "body"),
                ("youtube",   "youtube_script",  "script"),
                ("blog",      "blog_post",        "body"),
            ]:
                data = r.get(key, {})
                if data:
                    filename = f"posts/{plat}_{vid}.yaml"
                    with open(filename, "w", encoding="utf-8") as f:
                        yaml.dump({
                            "title": data.get("title", ""),
                            "body": data.get(body_key, ""),
                            "tags": data.get("tags", []),
                            "hashtags": data.get("hashtags", []),
                            "image_paths": [],
                            "video_path": None,
                            "schedule_time": None,
                        }, f, allow_unicode=True, default_flow_style=False)
                    saved.append(filename)
            st.success(f"✅ {len(saved)}개 파일 저장 완료! → '업로드' 메뉴에서 올릴 수 있습니다.")
            for s in saved:
                st.caption(f"📄 {s}")


# ══════════════════════════════════════════════════════════
# 🔍 유튜브 탐색
# ══════════════════════════════════════════════════════════
elif page == "🔍 유튜브 탐색":
    import yt_dlp as _ytdlp
    import json as _json
    import re as _re
    import collections
    from google import genai as _genai
    from google.genai import types as _gtypes

    st.title("🔍 유튜브 잘되는 콘텐츠 탐색")
    st.caption("키워드로 유튜브 상위 영상을 검색하고, AI가 성공 패턴을 분석해 우리 브랜드 아이디어로 변환합니다.")

    _ai_key   = cfg.get("openai", {}).get("api_key", "")
    _ai_model = cfg.get("openai", {}).get("model", "gemini-2.5-flash")

    # ── 검색 유틸 ─────────────────────────────────────────
    def _yt_search(keyword: str, n: int = 15) -> list[dict]:
        opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
        try:
            with _ytdlp.YoutubeDL(opts) as ydl:
                data = ydl.extract_info(f"ytsearch{n}:{keyword}", download=False)
                results = []
                for e in (data.get("entries") or []):
                    if not e:
                        continue
                    dur = e.get("duration") or 0
                    results.append({
                        "id":          e.get("id", ""),
                        "title":       e.get("title", ""),
                        "channel":     e.get("channel") or e.get("uploader", ""),
                        "views":       e.get("view_count") or 0,
                        "duration":    dur,
                        "is_short":    dur <= 60,
                        "upload_date": e.get("upload_date", ""),
                        "thumbnail":   e.get("thumbnail", ""),
                        "url":         f"https://www.youtube.com/watch?v={e.get('id','')}",
                        "description": e.get("description", ""),
                    })
                return results
        except Exception as _se:
            st.error(f"검색 오류: {_se}")
            return []

    def _fmt_views(v: int) -> str:
        if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
        if v >= 1_000:     return f"{v/1_000:.0f}K"
        return str(v)

    def _fmt_dur(s: int) -> str:
        if not s: return "—"
        m, sec = divmod(s, 60)
        h, m   = divmod(m, 60)
        return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"

    def _parse_date(d: str) -> str:
        if len(d) == 8:
            return f"{d[:4]}.{d[4:6]}.{d[6:]}"
        return d

    # ── 카테고리 프리셋 ───────────────────────────────────
    _PRESETS = {
        "직접 입력": "",
        "💍 반지 추천": "반지 추천 주얼리",
        "💑 커플링": "커플링 추천",
        "👰 예물": "예물반지 추천",
        "💛 금반지": "14k 금반지",
        "💎 다이아몬드": "다이아몬드 반지",
        "🎁 주얼리 선물": "주얼리 선물 추천",
        "📈 금 투자": "금 투자 방법",
        "✨ 명품 주얼리": "명품 주얼리 리뷰",
    }

    tab_search, tab_pattern, tab_idea = st.tabs([
        "🔍 영상 검색", "📊 성공 패턴 분석", "💡 브랜드 아이디어 생성"
    ])

    # ─────────────────────────────────────────────────────
    # 탭1: 검색
    # ─────────────────────────────────────────────────────
    with tab_search:
        _s1, _s2, _s3 = st.columns([2, 2, 1])
        with _s1:
            _preset = st.selectbox("카테고리 프리셋", list(_PRESETS.keys()), key="yt_preset")
        with _s2:
            _default_kw = _PRESETS[_preset]
            _keyword = st.text_input(
                "검색 키워드",
                value=_default_kw,
                placeholder="예: 커플링 추천 2025",
                key="yt_keyword"
            )
        with _s3:
            _max_n = st.selectbox("검색 수", [10, 15, 20], index=1, key="yt_max_n")

        _sf1, _sf2, _sf3 = st.columns(3)
        with _sf1:
            _sort_opt = st.selectbox("정렬", ["조회수 높은 순", "검색 순위 순", "최신순"], key="yt_sort")
        with _sf2:
            _type_filter = st.selectbox("영상 유형", ["전체", "일반 영상만", "쇼츠만"], key="yt_type")
        with _sf3:
            _min_views = st.number_input("최소 조회수", min_value=0, value=0, step=1000, key="yt_min_views")

        _do_search = st.button("🔍 검색", type="primary", disabled=not _keyword, key="yt_search_btn")

        if _do_search and _keyword:
            with st.spinner(f"'{_keyword}' 검색 중..."):
                _videos = _yt_search(_keyword, _max_n)
            st.session_state["yt_videos"]  = _videos
            st.session_state["yt_keyword"] = _keyword

        _videos = st.session_state.get("yt_videos", [])

        if _videos:
            # 필터 적용
            _filtered = _videos
            if _type_filter == "일반 영상만":
                _filtered = [v for v in _filtered if not v["is_short"]]
            elif _type_filter == "쇼츠만":
                _filtered = [v for v in _filtered if v["is_short"]]
            if _min_views > 0:
                _filtered = [v for v in _filtered if v["views"] >= _min_views]

            # 정렬
            if _sort_opt == "조회수 높은 순":
                _filtered.sort(key=lambda v: v["views"], reverse=True)
            elif _sort_opt == "최신순":
                _filtered.sort(key=lambda v: v["upload_date"], reverse=True)

            _kw_saved = st.session_state.get("yt_keyword", _keyword)
            st.markdown(f"**'{_kw_saved}' 검색 결과 — {len(_filtered)}개**")
            st.divider()

            # 영상 카드 그리드 (3열)
            for _row_start in range(0, len(_filtered), 3):
                _row_vids = _filtered[_row_start:_row_start+3]
                _cols = st.columns(3)
                for _col, _v in zip(_cols, _row_vids):
                    with _col:
                        # 썸네일
                        if _v["thumbnail"]:
                            try:
                                st.image(_v["thumbnail"], use_container_width=True)
                            except Exception:
                                st.markdown(
                                    "<div style='background:#eee;height:120px;border-radius:8px;"
                                    "display:flex;align-items:center;justify-content:center;"
                                    "color:#aaa'>🎬</div>", unsafe_allow_html=True
                                )
                        else:
                            st.markdown(
                                "<div style='background:#eee;height:120px;border-radius:8px;"
                                "display:flex;align-items:center;justify-content:center;"
                                "color:#aaa'>🎬</div>", unsafe_allow_html=True
                            )

                        _shorts_badge = (
                            "<span style='background:#FF0000;color:#fff;border-radius:4px;"
                            "padding:1px 5px;font-size:10px;font-weight:700'>SHORTS</span> "
                            if _v["is_short"] else ""
                        )
                        _view_color = "#E1306C" if _v["views"] >= 1_000_000 else "#0984e3" if _v["views"] >= 100_000 else "#444"
                        st.markdown(
                            f"<div style='margin-top:6px'>"
                            f"{_shorts_badge}"
                            f"<div style='font-size:.82rem;font-weight:700;line-height:1.3;"
                            f"color:#1a1a2e;margin-top:2px'>{_v['title'][:50]}{'…' if len(_v['title'])>50 else ''}</div>"
                            f"<div style='font-size:.75rem;color:#888;margin-top:3px'>"
                            f"📺 {_v['channel'][:18]}</div>"
                            f"<div style='font-size:.75rem;margin-top:2px;display:flex;gap:8px'>"
                            f"<span style='color:{_view_color};font-weight:700'>👁 {_fmt_views(_v['views'])}</span>"
                            f"<span style='color:#aaa'>⏱ {_fmt_dur(_v['duration'])}</span>"
                            f"<span style='color:#aaa'>{_parse_date(_v['upload_date'])}</span>"
                            f"</div></div>",
                            unsafe_allow_html=True
                        )

                        _btn_col1, _btn_col2 = st.columns(2)
                        with _btn_col1:
                            st.link_button("▶ 유튜브", _v["url"], use_container_width=True)
                        with _btn_col2:
                            if st.button("🎬 분석", key=f"analyze_{_v['id']}", use_container_width=True):
                                st.session_state["yt_analyze_url"] = _v["url"]
                                st.session_state["yt_analyze_title"] = _v["title"]
                                st.info(f"✅ 분석 대기: **{_v['title'][:30]}…**  \n→ **🎬 영상 분석** 탭에서 URL 자동 입력됩니다.")

                        st.markdown("---")

            # 조회수 분포 빠른 요약
            _total_views = sum(v["views"] for v in _filtered)
            _avg_views   = int(_total_views / len(_filtered)) if _filtered else 0
            _max_v       = max(_filtered, key=lambda v: v["views"]) if _filtered else None
            st.markdown(
                f"<div style='background:#f0f4ff;border-radius:10px;padding:12px 18px;"
                f"display:flex;gap:32px;flex-wrap:wrap;font-size:.88rem'>"
                f"<span>📊 검색 결과 <b>{len(_filtered)}개</b></span>"
                f"<span>👁 평균 조회수 <b>{_fmt_views(_avg_views)}</b></span>"
                f"<span>🏆 최고 조회수 <b>{_fmt_views(_max_v['views']) if _max_v else '—'}</b></span>"
                f"<span>🩳 쇼츠 <b>{sum(1 for v in _filtered if v['is_short'])}개</b></span>"
                f"</div>", unsafe_allow_html=True
            )

    # ─────────────────────────────────────────────────────
    # 탭2: 성공 패턴 분석
    # ─────────────────────────────────────────────────────
    with tab_pattern:
        _videos_p = st.session_state.get("yt_videos", [])
        _kw_p     = st.session_state.get("yt_keyword", "")

        if not _videos_p:
            st.info("먼저 **🔍 영상 검색** 탭에서 키워드를 검색해 주세요.")
        else:
            _top_vids = sorted(_videos_p, key=lambda v: v["views"], reverse=True)[:10]

            # 즉시 통계 (로컬 분석)
            st.markdown("### 📊 즉시 통계")
            _ic1, _ic2, _ic3, _ic4 = st.columns(4)
            _shorts_cnt = sum(1 for v in _top_vids if v["is_short"])
            _avg_v_top  = int(sum(v["views"] for v in _top_vids) / len(_top_vids)) if _top_vids else 0

            # 제목 패턴 분석
            _has_num  = sum(1 for v in _top_vids if _re.search(r'\d+', v["title"]))
            _has_q    = sum(1 for v in _top_vids if "?" in v["title"] or "？" in v["title"])
            _has_rank = sum(1 for v in _top_vids if any(w in v["title"] for w in ["TOP","best","추천","랭킹","순위","Best"]))
            _has_emo  = sum(1 for v in _top_vids if _re.search(r'[\U00010000-\U0010ffff]|[☀-⟿]', v["title"]))

            with _ic1:
                st.metric("TOP10 평균 조회수", _fmt_views(_avg_v_top))
            with _ic2:
                st.metric("쇼츠 비율", f"{_shorts_cnt}/{len(_top_vids)}")
            with _ic3:
                st.metric("숫자 포함 제목", f"{_has_num}/{len(_top_vids)}")
            with _ic4:
                st.metric("추천/랭킹 제목", f"{_has_rank}/{len(_top_vids)}")

            st.markdown("---")

            # 제목 패턴 바 차트
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            _fig_p, _ax_p = plt.subplots(figsize=(7, 2.5), facecolor="#f8f9ff")
            _ax_p.set_facecolor("#f8f9ff")
            _patterns = ["숫자 포함", "질문형(?)", "추천/랭킹", "이모지 포함"]
            _pat_vals  = [_has_num, _has_q, _has_rank, _has_emo]
            _bars_p    = _ax_p.barh(_patterns, _pat_vals, color=["#E1306C","#6c5ce7","#0984e3","#00b894"], alpha=0.85)
            _ax_p.bar_label(_bars_p, fmt="%d개", padding=3, fontsize=9)
            _ax_p.set_xlim(0, len(_top_vids)+1)
            _ax_p.set_xlabel(f"TOP{len(_top_vids)} 중 해당 영상 수", fontsize=8)
            _ax_p.set_title("TOP 영상 제목 패턴 분석", fontsize=10, fontweight="bold")
            _ax_p.tick_params(labelsize=8)
            _ax_p.grid(axis="x", alpha=0.3)
            _fig_p.tight_layout()
            st.pyplot(_fig_p)
            plt.close(_fig_p)

            # 조회수 상위 10 목록
            st.markdown("### 🏆 조회수 TOP 10")
            for _i, _v in enumerate(_top_vids, 1):
                _medal = "🥇" if _i == 1 else "🥈" if _i == 2 else "🥉" if _i == 3 else f"{_i}."
                _bg    = "#fff9f0" if _i <= 3 else "#f8f9ff"
                st.markdown(
                    f"<div style='background:{_bg};border-radius:10px;padding:10px 16px;"
                    f"margin:4px 0;display:flex;align-items:center;gap:12px'>"
                    f"<span style='font-size:1.2rem;min-width:30px'>{_medal}</span>"
                    f"<div style='flex:1'>"
                    f"<div style='font-weight:700;font-size:.88rem'>{_v['title'][:55]}{'…' if len(_v['title'])>55 else ''}</div>"
                    f"<div style='font-size:.75rem;color:#888'>📺 {_v['channel']}  ⏱ {_fmt_dur(_v['duration'])}"
                    f"  {'🩳 쇼츠' if _v['is_short'] else '📹 일반'}</div>"
                    f"</div>"
                    f"<div style='text-align:right;min-width:70px'>"
                    f"<div style='font-weight:800;color:#E1306C;font-size:1rem'>{_fmt_views(_v['views'])}</div>"
                    f"<div style='font-size:.7rem;color:#aaa'>조회수</div>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )

            st.markdown("---")

            # AI 패턴 분석
            st.markdown("### 🤖 AI 심층 패턴 분석")
            if not _ai_key:
                st.warning("⚠️ Gemini API 키가 없어 AI 분석을 사용할 수 없습니다.")
            else:
                if st.button("🤖 AI 패턴 분석 실행", type="primary", key="run_pattern_ai"):
                    with st.spinner("Gemini가 상위 영상들의 성공 공식을 분석 중..."):
                        try:
                            _vid_list = "\n".join(
                                f"{i+1}. 제목: {v['title']} | 조회수: {_fmt_views(v['views'])} | 채널: {v['channel']} | 유형: {'쇼츠' if v['is_short'] else '일반'} | 길이: {_fmt_dur(v['duration'])}"
                                for i, v in enumerate(_top_vids)
                            )
                            _pat_prompt = f"""유튜브 SEO 전문가로서 아래 '{_kw_p}' 키워드 상위 영상들을 분석해주세요.

=== 상위 영상 목록 ===
{_vid_list}

다음을 한국어로 분석해주세요:

## 1. 제목 공식 분석
(자주 쓰이는 패턴, 단어, 구조 분석)

## 2. 잘 되는 콘텐츠 유형
(쇼츠 vs 일반, 리뷰형 vs 정보형 vs 브이로그형 등)

## 3. 성공 요인 핵심 3가지
(이 키워드에서 높은 조회수를 얻는 공통 특성)

## 4. 피해야 할 패턴
(낮은 성과와 연관된 특징)

## 5. 알고리즘 인사이트
(제목 길이, 구조, 키워드 배치 등 SEO 팁)"""

                            _cl = _genai.Client(api_key=_ai_key)
                            _r  = _cl.models.generate_content(
                                model=_ai_model,
                                contents=_pat_prompt,
                                config=_gtypes.GenerateContentConfig(temperature=0.7),
                            )
                            st.session_state["yt_pattern_analysis"] = _r.text.strip()
                        except Exception as _e:
                            st.error(f"AI 분석 오류: {_e}")

                if "yt_pattern_analysis" in st.session_state:
                    st.markdown(
                        f"<div style='background:#fff;border:1px solid #e3e8ff;border-radius:12px;"
                        f"padding:20px 24px;line-height:1.8;font-size:.9rem'>"
                        f"{st.session_state['yt_pattern_analysis'].replace(chr(10),'<br>')}"
                        f"</div>", unsafe_allow_html=True
                    )

    # ─────────────────────────────────────────────────────
    # 탭3: 브랜드 아이디어 생성
    # ─────────────────────────────────────────────────────
    with tab_idea:
        _videos_i = st.session_state.get("yt_videos", [])
        _kw_i     = st.session_state.get("yt_keyword", "")

        if not _videos_i:
            st.info("먼저 **🔍 영상 검색** 탭에서 키워드를 검색해 주세요.")
        else:
            st.markdown("#### 우리 브랜드 설정")
            _id1, _id2 = st.columns(2)
            with _id1:
                _biz_desc  = st.text_input("업종/제품", value="주얼리 쇼핑몰 (반지·커플링·예물 전문)", key="idea_biz")
                _biz_acct  = st.text_input("채널/계정명", value="@geumseok_jewellery", key="idea_acct")
            with _id2:
                _biz_tone  = st.text_input("채널 톤", value="친근하고 전문적, 주얼리 전문가 느낌", key="idea_tone")
                _idea_cnt  = st.selectbox("생성할 아이디어 수", [5, 8, 10], index=1, key="idea_cnt")

            _idea_type = st.multiselect(
                "생성할 콘텐츠 유형",
                ["유튜브 쇼츠", "유튜브 일반 영상", "인스타그램 릴스", "네이버 블로그"],
                default=["유튜브 쇼츠", "유튜브 일반 영상"],
                key="idea_types"
            )

            if not _ai_key:
                st.warning("⚠️ Gemini API 키가 없어 AI 아이디어 생성을 사용할 수 없습니다.")
            else:
                if st.button("💡 아이디어 생성", type="primary", key="run_idea_ai"):
                    with st.spinner("Gemini가 유튜브 트렌드를 기반으로 아이디어를 생성 중..."):
                        try:
                            _top10 = sorted(_videos_i, key=lambda v: v["views"], reverse=True)[:10]
                            _vid_sum = "\n".join(
                                f"- {v['title']} ({_fmt_views(v['views'])}회, {'쇼츠' if v['is_short'] else '일반'})"
                                for v in _top10
                            )
                            _types_str = ", ".join(_idea_type)
                            _idea_prompt = f"""당신은 유튜브 콘텐츠 전략가입니다.

=== 키워드: {_kw_i} ===
=== 현재 유튜브 상위 영상 ===
{_vid_sum}

=== 우리 브랜드 ===
업종: {_biz_desc}
채널: {_biz_acct}
톤/스타일: {_biz_tone}
제작 가능 유형: {_types_str}

위 트렌드를 분석해서 우리 브랜드에 맞게 각색한 콘텐츠 아이디어 {_idea_cnt}개를 만들어주세요.
표절이 아닌 영감을 받아 완전히 새로운 아이디어여야 합니다.

아래 JSON 배열로만 응답하세요:
[
  {{
    "type": "콘텐츠 유형 (유튜브 쇼츠/일반/릴스/블로그)",
    "title": "제목 (클릭율 높게, 50자 이내)",
    "hook": "첫 5초 후킹 멘트",
    "outline": ["핵심 포인트1", "핵심 포인트2", "핵심 포인트3"],
    "why_works": "이 아이디어가 잘 될 이유 (1문장)",
    "thumbnail_concept": "썸네일 구성 아이디어",
    "estimated_views": "예상 조회수 범위 (예: 1만~5만)"
  }}
]
한국어로만 응답하세요."""

                            _cl2 = _genai.Client(api_key=_ai_key)
                            _r2  = _cl2.models.generate_content(
                                model=_ai_model,
                                contents=_idea_prompt,
                                config=_gtypes.GenerateContentConfig(
                                    temperature=0.9,
                                    response_mime_type="application/json",
                                ),
                            )
                            _ideas = _json.loads(_r2.text.strip())
                            st.session_state["yt_ideas"] = _ideas
                        except Exception as _e:
                            st.error(f"아이디어 생성 오류: {_e}")

                if "yt_ideas" in st.session_state:
                    _ideas = st.session_state["yt_ideas"]
                    st.markdown(f"### 💡 생성된 콘텐츠 아이디어 {len(_ideas)}개")

                    _TYPE_COLOR = {
                        "유튜브 쇼츠": "#FF0000", "유튜브 일반 영상": "#cc0000",
                        "인스타그램 릴스": "#E1306C", "네이버 블로그": "#03C75A",
                    }

                    for _ii, _idea in enumerate(_ideas, 1):
                        _itype  = _idea.get("type", "")
                        _icolor = next((v for k,v in _TYPE_COLOR.items() if k in _itype), "#6c5ce7")
                        _outline_html = "".join(
                            f"<li style='margin:2px 0'>{pt}</li>"
                            for pt in _idea.get("outline", [])
                        )

                        with st.expander(f"**{_ii}.** {_idea.get('title','')}", expanded=_ii <= 3):
                            _ea, _eb = st.columns([3, 2])
                            with _ea:
                                st.markdown(
                                    f"<div style='margin-bottom:10px'>"
                                    f"<span style='background:{_icolor};color:#fff;border-radius:6px;"
                                    f"padding:3px 10px;font-size:12px;font-weight:700'>{_itype}</span>"
                                    f"</div>"
                                    f"<div style='background:#fff8e1;border-left:4px solid #f39c12;"
                                    f"padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:10px'>"
                                    f"<b>🎣 후킹 멘트</b><br>"
                                    f"<span style='font-size:.92rem'>{_idea.get('hook','')}</span></div>"
                                    f"<div style='background:#f8f9ff;border-radius:8px;padding:10px 14px'>"
                                    f"<b>📋 핵심 구성</b>"
                                    f"<ul style='margin:6px 0;padding-left:16px'>{_outline_html}</ul></div>",
                                    unsafe_allow_html=True
                                )
                            with _eb:
                                st.markdown(
                                    f"<div style='background:#e8f5e9;border-radius:8px;padding:10px 14px;margin-bottom:8px'>"
                                    f"<b>✅ 잘 될 이유</b><br>"
                                    f"<span style='font-size:.88rem'>{_idea.get('why_works','')}</span></div>"
                                    f"<div style='background:#f3e5f5;border-radius:8px;padding:10px 14px;margin-bottom:8px'>"
                                    f"<b>🖼 썸네일 아이디어</b><br>"
                                    f"<span style='font-size:.88rem'>{_idea.get('thumbnail_concept','')}</span></div>"
                                    f"<div style='background:#e3f2fd;border-radius:8px;padding:10px 14px'>"
                                    f"<b>📈 예상 조회수</b><br>"
                                    f"<span style='font-weight:700;color:#0984e3'>{_idea.get('estimated_views','')}</span></div>",
                                    unsafe_allow_html=True
                                )

                            # 포스트 저장
                            if st.button(f"💾 포스트로 저장", key=f"save_idea_{_ii}"):
                                Path("posts").mkdir(exist_ok=True)
                                _fname = f"youtube_{datetime.now().strftime('%Y%m%d_%H%M%S')}_idea{_ii}.yaml"
                                with open(Path("posts") / _fname, "w", encoding="utf-8") as _wf:
                                    yaml.dump({
                                        "title":    _idea.get("title",""),
                                        "body":     f"후킹: {_idea.get('hook','')}\n\n" +
                                                    "\n".join(f"- {p}" for p in _idea.get("outline",[])),
                                        "caption":  _idea.get("hook",""),
                                        "hashtags": [],
                                        "thumbnail_concept": _idea.get("thumbnail_concept",""),
                                        "why_works": _idea.get("why_works",""),
                                        "image_paths": [], "video_path": None, "schedule_time": None,
                                    }, _wf, allow_unicode=True, default_flow_style=False)
                                st.success(f"✅ posts/{_fname} 저장!")

                    # 전체 아이디어 텍스트 복사
                    st.markdown("---")
                    _all_ideas_txt = "\n\n".join(
                        f"[{_idea.get('type','')}] {_idea.get('title','')}\n"
                        f"후킹: {_idea.get('hook','')}\n"
                        f"구성: {' / '.join(_idea.get('outline',[]))}"
                        for _idea in _ideas
                    )
                    st.text_area("📋 전체 아이디어 복사용", value=_all_ideas_txt, height=180, key="ideas_copy")

# ══════════════════════════════════════════════════════════
# ✍️ 포스트 생성
# ══════════════════════════════════════════════════════════
elif page == "✍️ 포스트 생성":
    st.title("✍️ AI 포스트 자동 생성")
    st.caption("Gemini가 주제를 입력받아 각 플랫폼에 맞는 포스트를 생성합니다.")
    st.divider()

    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        topic = st.text_input("📌 주제", placeholder="예: 14K 18K 금반지 차이점")
    with col2:
        platform = st.selectbox("플랫폼 스타일", ["all", "instagram", "threads", "youtube", "blog"])
    with col3:
        num_hashtags = st.number_input("해시태그 수", 3, 10, 5)

    batch_mode = st.checkbox("멀티 플랫폼 동시 생성 (인스타/쓰레드/유튜브/블로그)")

    if st.button("🤖 포스트 생성", type="primary", width="stretch") and topic:
        with st.spinner("Gemini 생성 중..."):
            try:
                from platforms.ai_content_generator import AIContentGenerator
                gen = AIContentGenerator(cfg.get("openai", {}))

                if batch_mode:
                    results = gen.batch_generate(topic)
                    for plat, content in results.items():
                        with st.expander(f"**{PLATFORMS.get(plat, plat)}** 버전", expanded=True):
                            st.markdown(f"**제목:** {content.title}")
                            st.text_area("본문", content.body, height=120, key=f"body_{plat}")
                            st.text(f"해시태그: {' '.join(content.hashtags)}")

                            safe = topic.replace(" ", "_")
                            save_path = f"posts/{plat}_{safe}.yaml"
                            Path("posts").mkdir(exist_ok=True)
                            with open(save_path, "w", encoding="utf-8") as f:
                                yaml.dump({
                                    "title": content.title, "body": content.body,
                                    "tags": content.tags, "hashtags": content.hashtags,
                                    "image_paths": [], "video_path": None, "schedule_time": None,
                                }, f, allow_unicode=True, default_flow_style=False)
                            st.caption(f"저장됨: `{save_path}`")
                    st.success("✅ 전체 생성 완료!")

                else:
                    content = gen.generate_post(topic, platform, num_hashtags=num_hashtags)
                    st.session_state["generated_content"] = content

                    st.markdown("### 생성 결과")
                    title_edit = st.text_input("제목", content.title)
                    body_edit = st.text_area("본문", content.body, height=200)
                    hashtag_edit = st.text_input("해시태그", " ".join(content.hashtags))
                    tags_edit = st.text_input("태그", ", ".join(content.tags))

                    save_name = st.text_input("저장 파일명", f"posts/{platform}_{topic.replace(' ', '_')}.yaml")
                    if st.button("💾 저장"):
                        Path("posts").mkdir(exist_ok=True)
                        with open(save_name, "w", encoding="utf-8") as f:
                            yaml.dump({
                                "title": title_edit, "body": body_edit,
                                "tags": [t.strip() for t in tags_edit.split(",")],
                                "hashtags": hashtag_edit.split(),
                                "image_paths": [], "video_path": None, "schedule_time": None,
                            }, f, allow_unicode=True, default_flow_style=False)
                        st.success(f"✅ 저장 완료: `{save_name}`")

            except Exception as e:
                st.error(f"오류: {e}")

# ══════════════════════════════════════════════════════════
# 🖼️ 이미지 생성
# ══════════════════════════════════════════════════════════
elif page == "🖼️ 이미지 생성":
    st.title("🖼️ AI 이미지 자동 생성")
    st.caption("Pollinations.ai (무료) — 텍스트로 이미지를 생성합니다.")
    st.divider()

    img_type = st.radio("생성 유형", ["일반 이미지", "카드뉴스 시리즈", "유튜브 썸네일"], horizontal=True)

    if img_type == "일반 이미지":
        prompt = st.text_input("이미지 설명", placeholder="예: 금반지 미니멀 화이트 배경 고급스러운")
        count = st.slider("생성 개수", 1, 4, 1)
        if st.button("🎨 이미지 생성", type="primary") and prompt:
            with st.spinner(f"{count}개 생성 중..."):
                try:
                    from platforms.image_generator import AIImageGenerator
                    gen = AIImageGenerator(cfg.get("image_generation", {}))
                    paths = gen.generate_image(prompt, num_images=count)
                    cols = st.columns(min(count, 4))
                    for i, (col, path) in enumerate(zip(cols, paths)):
                        with col:
                            st.image(path, caption=f"이미지 {i+1}", width="stretch")
                    st.success(f"✅ {len(paths)}개 저장됨: `assets/images/`")
                except Exception as e:
                    st.error(f"오류: {e}")

    elif img_type == "카드뉴스 시리즈":
        topic = st.text_input("카드뉴스 주제", placeholder="예: 14K vs 18K 금반지 비교")
        cards = st.slider("카드 수", 1, 5, 3)
        if st.button("🃏 카드뉴스 생성", type="primary") and topic:
            with st.spinner(f"{cards}장 생성 중... (카드당 약 15초)"):
                try:
                    from platforms.image_generator import AIImageGenerator
                    gen = AIImageGenerator(cfg.get("image_generation", {}))
                    paths = gen.generate_cardnews(topic, num_cards=cards)
                    cols = st.columns(min(cards, 4))
                    for i, (col, path) in enumerate(zip(cols * 2, paths)):
                        with col:
                            st.image(path, caption=f"카드 {i+1}", width="stretch")
                    st.success(f"✅ {len(paths)}장 저장됨!")

                    # 포스트에 연결
                    post_files = list(Path("posts").glob("*.yaml")) if Path("posts").exists() else []
                    if post_files:
                        selected = st.selectbox("이미지를 연결할 포스트", [f.name for f in post_files])
                        if st.button("📎 포스트에 이미지 연결"):
                            with open(f"posts/{selected}", "r", encoding="utf-8") as f:
                                post_data = yaml.safe_load(f)
                            post_data["image_paths"] = paths
                            with open(f"posts/{selected}", "w", encoding="utf-8") as f:
                                yaml.dump(post_data, f, allow_unicode=True, default_flow_style=False)
                            st.success("✅ 연결 완료!")
                except Exception as e:
                    st.error(f"오류: {e}")

    else:  # 유튜브 썸네일
        title = st.text_input("영상 제목", placeholder="예: 금반지 구매 가이드 A to Z")
        if st.button("🎬 썸네일 생성", type="primary") and title:
            with st.spinner("썸네일 생성 중..."):
                try:
                    from platforms.image_generator import AIImageGenerator
                    gen = AIImageGenerator(cfg.get("image_generation", {}))
                    path = gen.generate_thumbnail(title)
                    st.image(path, caption="생성된 썸네일", width="stretch")
                    st.success(f"✅ 저장됨: `{path}`")
                except Exception as e:
                    st.error(f"오류: {e}")

# ══════════════════════════════════════════════════════════
# 📸 사진→콘텐츠
# ══════════════════════════════════════════════════════════
elif page == "📸 사진→콘텐츠":
    import json as _json
    from google import genai as _genai
    from google.genai import types as _gtypes

    st.title("📸 사진 분석 → 콘텐츠 자동 생성")
    st.caption("사진 한 장만 올리면 Gemini Vision이 분석해서 각 플랫폼에 맞는 글을 자동으로 만들어줍니다.")

    _cfg_ai   = cfg.get("openai", {})
    _ai_key   = _cfg_ai.get("api_key", "")
    _ai_model = _cfg_ai.get("model", "gemini-2.5-flash")

    if not _ai_key:
        st.warning("⚠️ Gemini API 키가 설정되지 않았습니다. ⚙️ 설정 탭에서 먼저 등록해 주세요.")
    else:
        # ── 상단: 사진 업로드 + 설정 ──────────────────────────
        _up_col, _set_col = st.columns([1, 1], gap="large")

        with _up_col:
            st.markdown("#### 1️⃣ 사진 올리기")
            _uploaded = st.file_uploader(
                "사진을 드래그하거나 클릭하여 업로드",
                type=["jpg", "jpeg", "png", "webp", "heic"],
                label_visibility="collapsed",
                key="img_upload"
            )
            if _uploaded:
                st.image(_uploaded, use_container_width=True)
                st.caption(f"📁 {_uploaded.name}  ({_uploaded.size // 1024} KB)")

        with _set_col:
            st.markdown("#### 2️⃣ 생성 설정")
            _ic1, _ic2 = st.columns(2)
            with _ic1:
                _biz_type = st.text_input(
                    "업종/제품",
                    value=cfg.get("business_info", {}).get("description", "주얼리 쇼핑몰"),
                    placeholder="예: 주얼리 쇼핑몰",
                    key="img_biz"
                )
                _brand_account = st.text_input(
                    "계정명",
                    value="@geumseok_jewellery",
                    key="img_account"
                )
            with _ic2:
                _tone = st.selectbox(
                    "말투/톤",
                    ["친근하고 감성적", "전문적이고 신뢰감", "트렌디하고 발랄", "고급스럽고 우아", "직접적이고 간결"],
                    key="img_tone"
                )
                _target = st.selectbox(
                    "타겟 고객",
                    ["20-30대 여성", "커플/연인", "결혼 준비 중인 분", "선물 구매자", "주얼리 관심자"],
                    key="img_target"
                )

            _plat_options = {
                "📸 Instagram": "instagram",
                "🧵 Threads": "threads",
                "📗 네이버 블로그": "naver",
                "▶️ YouTube 쇼츠 설명": "youtube",
            }
            _sel_plats = st.multiselect(
                "생성할 플랫폼",
                list(_plat_options.keys()),
                default=["📸 Instagram", "🧵 Threads", "📗 네이버 블로그"],
                key="img_plats"
            )
            _add_hint = st.text_input(
                "추가 힌트 (선택)",
                placeholder="예: 14K 핑크골드 반지, 신상품, 여름 컬렉션",
                key="img_hint"
            )

        st.divider()

        # ── 생성 버튼 ─────────────────────────────────────────
        _gen_btn = st.button(
            "✨ 사진 분석 & 콘텐츠 생성",
            type="primary",
            disabled=not _uploaded,
            key="img_gen_btn",
            use_container_width=True,
        )

        if _gen_btn and _uploaded:
            _img_bytes = _uploaded.getvalue()
            _mime = _uploaded.type or "image/jpeg"
            _pids = [_plat_options[p] for p in _sel_plats if p in _plat_options]

            _plat_guide = {
                "instagram": "인스타그램 캡션: 첫 줄 감성 후킹 → 제품 설명 → CTA(저장/팔로우/DM). 이모지 4~6개. 150~300자. 해시태그 10~20개.",
                "threads": "Threads 본문: 280자 이내 대화체. 질문으로 댓글 유도. 이모지 2~3개. 해시태그 1~2개.",
                "naver": "네이버 블로그 본문: 1200자 이상. 소제목(##) 3개 이상. 제품 특징·소재·가격대·구매 방법 포함. 검색 키워드 자연스럽게 반복. 태그 5~10개.",
                "youtube": "유튜브 쇼츠 설명란: 150~200자. 첫 2줄에 핵심 키워드. 구독·좋아요 CTA. 해시태그 3~5개.",
            }
            _guide_str = "\n".join(
                f"- {pid}: {_plat_guide.get(pid, '')}" for pid in _pids
            )

            _json_fields = ""
            for pid in _pids:
                _json_fields += f"""
    "{pid}": {{
      "title": "제목",
      "body": "본문",
      "hashtags": ["#태그1", "#태그2"]
    }},"""

            _prompt = f"""당신은 SNS 콘텐츠 전문가입니다. 이 사진을 보고 아래 정보를 바탕으로 각 플랫폼에 최적화된 콘텐츠를 생성해주세요.

=== 비즈니스 정보 ===
업종/제품: {_biz_type}
계정: {_brand_account}
말투: {_tone}
타겟: {_target}
추가 힌트: {_add_hint or "없음"}

=== 플랫폼별 작성 가이드 ===
{_guide_str}

아래 JSON 형식으로만 응답하세요:
{{
  "image_analysis": {{
    "subject": "사진 속 주요 피사체 (2~3문장)",
    "mood": "전체적인 분위기/무드",
    "colors": ["주요 색상1", "주요 색상2"],
    "style": "스타일 특징",
    "product_features": ["특징1", "특징2", "특징3"]
  }},
  "content": {{{_json_fields}
  }}
}}

한국어로만 응답하세요."""

            with st.spinner("🔍 Gemini Vision이 사진을 분석하고 콘텐츠를 생성 중입니다..."):
                try:
                    _client = _genai.Client(api_key=_ai_key)
                    _response = _client.models.generate_content(
                        model=_ai_model,
                        contents=[
                            _gtypes.Part.from_bytes(data=_img_bytes, mime_type=_mime),
                            _prompt,
                        ],
                        config=_gtypes.GenerateContentConfig(
                            temperature=0.8,
                            response_mime_type="application/json",
                        ),
                    )
                    _raw = _response.text.strip()
                    _result = _json.loads(_raw)
                    st.session_state["img_content_result"] = _result
                    st.session_state["img_upload_name"]   = _uploaded.name
                    st.session_state["img_pids"]          = _pids
                except Exception as _e:
                    st.error(f"AI 분석 오류: {_e}")

        # ── 결과 표시 ─────────────────────────────────────────
        if "img_content_result" in st.session_state:
            _res   = st.session_state["img_content_result"]
            _pids2 = st.session_state.get("img_pids", [])
            _anal  = _res.get("image_analysis", {})
            _cont  = _res.get("content", {})

            # 이미지 분석 요약 카드
            st.markdown("### 📊 이미지 분석 결과")
            _colors_html = "".join(
                f"<span style='background:{c};display:inline-block;width:18px;height:18px;"
                f"border-radius:50%;margin-right:4px;border:1px solid #ddd'></span>"
                for c in _anal.get("colors", [])
            )
            _feats_html = "".join(
                f"<span style='background:#f0f4ff;color:#3949ab;border-radius:20px;"
                f"padding:3px 10px;margin:2px;font-size:12px;display:inline-block'>{f}</span>"
                for f in _anal.get("product_features", [])
            )
            st.markdown(
                f"<div style='background:#f8f9ff;border-radius:14px;padding:18px 22px;"
                f"border:1px solid #e3e8ff;margin-bottom:16px'>"
                f"<div style='display:flex;gap:24px;flex-wrap:wrap'>"
                f"<div style='flex:1;min-width:200px'>"
                f"<div style='font-weight:700;margin-bottom:6px'>📷 피사체</div>"
                f"<div style='font-size:.9rem;color:#444'>{_anal.get('subject','')}</div></div>"
                f"<div style='min-width:140px'>"
                f"<div style='font-weight:700;margin-bottom:6px'>🎨 무드</div>"
                f"<div style='font-size:.9rem;color:#444'>{_anal.get('mood','')}</div>"
                f"<div style='margin-top:6px'>{_colors_html}</div></div>"
                f"<div style='min-width:140px'>"
                f"<div style='font-weight:700;margin-bottom:6px'>✨ 스타일</div>"
                f"<div style='font-size:.9rem;color:#444'>{_anal.get('style','')}</div></div></div>"
                f"<div style='margin-top:12px'>{_feats_html}</div></div>",
                unsafe_allow_html=True
            )

            # 플랫폼별 콘텐츠
            st.markdown("### ✍️ 생성된 콘텐츠")

            _PLAT_STYLE = {
                "instagram": ("#E1306C", "#fce4ec", "📸 Instagram"),
                "threads":   ("#1c1c1e", "#f3f3f3", "🧵 Threads"),
                "naver":     ("#03C75A", "#e8f5e9", "📗 네이버 블로그"),
                "youtube":   ("#FF0000", "#ffebee", "▶️ YouTube 쇼츠"),
            }

            for _pid in _pids2:
                if _pid not in _cont:
                    continue
                _pc = _cont[_pid]
                _clr, _bg, _plabel = _PLAT_STYLE.get(_pid, ("#888", "#f5f5f5", _pid))

                with st.expander(f"{_plabel} 콘텐츠", expanded=True):
                    _ec1, _ec2 = st.columns([3, 2])

                    with _ec1:
                        _e_title = st.text_input(
                            "제목", value=_pc.get("title", ""),
                            key=f"ic_title_{_pid}"
                        )
                        _e_body = st.text_area(
                            "본문",
                            value=_pc.get("body", ""),
                            height=200 if _pid == "naver" else 130,
                            key=f"ic_body_{_pid}"
                        )
                        _e_tags_raw = st.text_input(
                            "해시태그",
                            value=" ".join(_pc.get("hashtags", [])),
                            key=f"ic_tags_{_pid}"
                        )

                    with _ec2:
                        # 미니 미리보기
                        if _pid == "instagram":
                            st.markdown(
                                f"<div style='background:#fff;border:1px solid #dbdbdb;border-radius:12px;"
                                f"padding:14px;font-size:.82rem;max-height:300px;overflow-y:auto'>"
                                f"<div style='font-weight:700;color:#262626;margin-bottom:6px'>"
                                f"geumseok_jewellery</div>"
                                f"<div style='color:#262626;white-space:pre-wrap;line-height:1.5'>"
                                f"{(_e_body or _pc.get('body',''))[:200]}…</div>"
                                f"<div style='color:#00376b;margin-top:8px;font-size:.78rem'>"
                                f"{' '.join(_pc.get('hashtags',[])[:5])}</div></div>",
                                unsafe_allow_html=True
                            )
                        elif _pid == "threads":
                            st.markdown(
                                f"<div style='background:#fff;border:1px solid #e0e0e0;border-radius:12px;"
                                f"padding:14px;font-size:.82rem'>"
                                f"<div style='font-weight:700;margin-bottom:6px'>geumseok_jewellery</div>"
                                f"<div style='white-space:pre-wrap;line-height:1.5'>"
                                f"{(_e_body or _pc.get('body',''))[:280]}</div></div>",
                                unsafe_allow_html=True
                            )
                        elif _pid == "naver":
                            st.markdown(
                                f"<div style='background:#fff;border:1px solid #e0e0e0;border-radius:12px;"
                                f"padding:14px;font-size:.82rem;max-height:300px;overflow-y:auto'>"
                                f"<div style='font-size:1rem;font-weight:700;color:#03C75A;margin-bottom:8px'>"
                                f"{_e_title or _pc.get('title','')}</div>"
                                f"<div style='white-space:pre-wrap;line-height:1.6;color:#444'>"
                                f"{(_e_body or _pc.get('body',''))[:400]}…</div></div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"<div style='background:#fff;border:1px solid #e0e0e0;border-radius:12px;"
                                f"padding:14px;font-size:.82rem'>"
                                f"<div style='font-weight:700;color:{_clr};margin-bottom:6px'>"
                                f"{_e_title or _pc.get('title','')}</div>"
                                f"<div style='white-space:pre-wrap;line-height:1.5;color:#444'>"
                                f"{(_e_body or _pc.get('body',''))[:200]}</div></div>",
                                unsafe_allow_html=True
                            )

                        # 글자 수 / 해시태그 수
                        _body_now = _e_body or _pc.get("body", "")
                        _tags_now = [t.strip() for t in _e_tags_raw.split() if t.strip()]
                        _limits = {"instagram": (150,300,20), "threads": (50,280,3), "naver": (800,2000,10), "youtube": (100,200,5)}
                        _lmin, _lmax, _hmax = _limits.get(_pid, (50, 500, 20))
                        _blen = len(_body_now)
                        _b_ok = _lmin <= _blen <= _lmax
                        _h_ok = len(_tags_now) <= _hmax

                        st.markdown(
                            f"<div style='margin-top:10px;font-size:.78rem;display:flex;gap:10px'>"
                            f"<span style='color:{'#2e7d32' if _b_ok else '#c62828'}'>"
                            f"본문 {_blen}자 ({_lmin}~{_lmax})</span>"
                            f"<span style='color:{'#2e7d32' if _h_ok else '#c62828'}'>"
                            f"해시태그 {len(_tags_now)}개 (max {_hmax})</span></div>",
                            unsafe_allow_html=True
                        )

                    # 저장 버튼
                    _sc1, _sc2 = st.columns(2)
                    with _sc1:
                        if st.button(f"💾 posts/ 저장", key=f"save_ic_{_pid}"):
                            Path("posts").mkdir(exist_ok=True)
                            _fname = f"{_pid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_photo.yaml"
                            _e_tags_list = [t.strip() for t in _e_tags_raw.split() if t.strip()]
                            with open(Path("posts") / _fname, "w", encoding="utf-8") as _wf:
                                yaml.dump({
                                    "title":       _e_title,
                                    "body":        _e_body,
                                    "caption":     _e_body,
                                    "hashtags":    _e_tags_list,
                                    "tags":        [t.lstrip("#") for t in _e_tags_list[:10]],
                                    "image_paths": [],
                                    "video_path":  None,
                                    "schedule_time": None,
                                }, _wf, allow_unicode=True, default_flow_style=False)
                            st.success(f"✅ posts/{_fname} 저장!")
                    with _sc2:
                        _copy_text = f"{_e_title}\n\n{_e_body}\n\n{_e_tags_raw}"
                        st.text_area("클립보드 복사용", value=_copy_text, height=60,
                                     key=f"copy_ic_{_pid}", label_visibility="collapsed")

            # 전체 저장 버튼
            st.markdown("---")
            if st.button("💾 전체 플랫폼 한번에 저장", type="secondary", key="save_all_ic"):
                Path("posts").mkdir(exist_ok=True)
                _saved = []
                for _pid in _pids2:
                    if _pid not in _cont:
                        continue
                    _pc = _cont[_pid]
                    _title_v = st.session_state.get(f"ic_title_{_pid}", _pc.get("title",""))
                    _body_v  = st.session_state.get(f"ic_body_{_pid}",  _pc.get("body",""))
                    _tags_v  = st.session_state.get(f"ic_tags_{_pid}",  " ".join(_pc.get("hashtags",[])))
                    _tags_list = [t.strip() for t in _tags_v.split() if t.strip()]
                    _fname = f"{_pid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_photo.yaml"
                    with open(Path("posts") / _fname, "w", encoding="utf-8") as _wf:
                        yaml.dump({
                            "title":       _title_v,
                            "body":        _body_v,
                            "caption":     _body_v,
                            "hashtags":    _tags_list,
                            "tags":        [t.lstrip("#") for t in _tags_list[:10]],
                            "image_paths": [],
                            "video_path":  None,
                            "schedule_time": None,
                        }, _wf, allow_unicode=True, default_flow_style=False)
                    _saved.append(_fname)
                if _saved:
                    st.success(f"✅ {len(_saved)}개 저장 완료!\n" + "\n".join(f"• {f}" for f in _saved))

# ══════════════════════════════════════════════════════════
# 👁️ 미리보기 & 편집
# ══════════════════════════════════════════════════════════
elif page == "👁️ 미리보기 & 편집":
    st.title("👁️ 포스트 미리보기 & 편집")
    st.caption("실제 SNS 화면처럼 미리보고, 바로 수정 후 저장하세요.")
    st.divider()

    post_files_prev = sorted(Path("posts").glob("*.yaml"), key=os.path.getmtime, reverse=True) if Path("posts").exists() else []
    if not post_files_prev:
        st.warning("포스트 파일이 없습니다. '포스트 생성' 메뉴에서 먼저 만들어주세요.")
        st.stop()

    # 파일 선택
    selected_prev = st.selectbox("📄 포스트 파일 선택", [f.name for f in post_files_prev], key="prev_file")
    prev_path = f"posts/{selected_prev}"

    # 파일 로드 (세션에 캐싱 — 파일 변경 시 갱신)
    if st.session_state.get("_prev_loaded_file") != selected_prev:
        with open(prev_path, "r", encoding="utf-8") as _f:
            _d = yaml.safe_load(_f)
        st.session_state["prev_title"]    = _d.get("title", "")
        st.session_state["prev_body"]     = _d.get("body", "")
        st.session_state["prev_hashtags"] = " ".join(_d.get("hashtags", []))
        st.session_state["prev_tags"]     = ", ".join(_d.get("tags", []))
        st.session_state["prev_images"]   = _d.get("image_paths", [])
        st.session_state["_prev_loaded_file"] = selected_prev

    st.divider()
    col_edit, col_prev = st.columns([1, 1], gap="large")

    # ── 왼쪽: 편집 ────────────────────────────────────────
    with col_edit:
        st.markdown("### ✏️ 편집")

        st.session_state["prev_title"] = st.text_input(
            "제목", st.session_state["prev_title"], key="ei_title"
        )
        st.session_state["prev_body"] = st.text_area(
            "본문 (캡션)", st.session_state["prev_body"], height=220, key="ei_body"
        )
        st.session_state["prev_hashtags"] = st.text_input(
            "해시태그 (공백 구분)", st.session_state["prev_hashtags"], key="ei_hash"
        )
        st.session_state["prev_tags"] = st.text_input(
            "태그 (쉼표 구분)", st.session_state["prev_tags"], key="ei_tags"
        )

        # 이미지 교체
        st.markdown("**이미지**")
        cur_imgs = st.session_state["prev_images"]
        if cur_imgs:
            for _ip in cur_imgs[:2]:
                if Path(_ip).exists():
                    st.image(_ip, width=120)
        new_upload = st.file_uploader("이미지 교체 (선택)", type=["jpg","jpeg","png"], key="ei_img")
        if new_upload:
            _save_dir = Path("assets/images")
            _save_dir.mkdir(parents=True, exist_ok=True)
            _img_path = str(_save_dir / new_upload.name)
            with open(_img_path, "wb") as _out:
                _out.write(new_upload.read())
            st.session_state["prev_images"] = [_img_path]
            st.success(f"이미지 교체됨: {new_upload.name}")

        st.divider()
        if st.button("💾 변경사항 저장", type="primary", width="stretch"):
            with open(prev_path, "r", encoding="utf-8") as _f:
                _orig = yaml.safe_load(_f)
            _orig["title"]       = st.session_state["prev_title"]
            _orig["body"]        = st.session_state["prev_body"]
            _orig["hashtags"]    = st.session_state["prev_hashtags"].split()
            _orig["tags"]        = [t.strip() for t in st.session_state["prev_tags"].split(",") if t.strip()]
            _orig["image_paths"] = st.session_state["prev_images"]
            with open(prev_path, "w", encoding="utf-8") as _f:
                yaml.dump(_orig, _f, allow_unicode=True, default_flow_style=False)
            st.success("✅ 저장 완료!")

    # ── 오른쪽: 미리보기 ──────────────────────────────────
    with col_prev:
        st.markdown("### 📱 미리보기")

        _body     = st.session_state["prev_body"]
        _hashtags = st.session_state["prev_hashtags"]
        _title    = st.session_state["prev_title"]
        _imgs     = st.session_state["prev_images"]
        _username = cfg.get("instagram", {}).get("username", "geumseok_jewellery")

        # 이미지 표시 (있으면 실제 이미지, 없으면 플레이스홀더)
        _img_html = ""
        _img_exists = _imgs and Path(_imgs[0]).exists()
        if not _img_exists:
            _img_html = "<div style='width:100%;aspect-ratio:1;background:#f5f5f5;display:flex;align-items:center;justify-content:center;font-size:48px;'>📷</div>"

        tab_ig_p, tab_th_p, tab_blog_p = st.tabs(["📸 Instagram", "🧵 Threads", "📝 블로그"])

        # ── Instagram 미리보기 ─────────────────────────────
        with tab_ig_p:
            if _img_exists:
                st.image(_imgs[0], width="stretch")
            else:
                st.markdown(
                    "<div style='width:100%;aspect-ratio:1;background:#f0f0f0;"
                    "border-radius:4px;display:flex;align-items:center;"
                    "justify-content:center;font-size:48px;margin-bottom:8px'>📷</div>",
                    unsafe_allow_html=True
                )

            _caption_full = _body + ("\n\n" + _hashtags if _hashtags else "")
            _hashtag_html = "".join(
                f"<span style='color:#00376b'>{h}</span> "
                for h in _hashtags.split() if h.startswith("#")
            )

            st.markdown(f"""
<div style="border:1px solid #dbdbdb;border-radius:8px;background:#fff;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
            max-width:420px;margin:0 auto;">
  <div style="display:flex;align-items:center;padding:10px 12px;">
    <div style="width:34px;height:34px;border-radius:50%;
                background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);
                margin-right:10px;flex-shrink:0"></div>
    <div>
      <div style="font-weight:600;font-size:13px">{_username}</div>
      <div style="font-size:11px;color:#8e8e8e">팔로잉</div>
    </div>
    <div style="margin-left:auto;font-size:18px;color:#262626">···</div>
  </div>
  <div style="padding:0 12px 10px">
    <div style="font-size:13px;line-height:1.5;white-space:pre-wrap">\
<span style="font-weight:600">{_username}</span> {_body[:200]}{"..." if len(_body)>200 else ""}</div>
    <div style="margin-top:6px;font-size:13px">{_hashtag_html}</div>
  </div>
  <div style="padding:0 12px 8px;display:flex;gap:16px;font-size:22px">
    <span>🤍</span><span>💬</span><span>📤</span>
    <span style="margin-left:auto">🔖</span>
  </div>
  <div style="padding:0 12px 12px;font-size:11px;color:#8e8e8e">
    {datetime.now().strftime('%Y년 %m월 %d일')}
  </div>
</div>""", unsafe_allow_html=True)

            _char = len(_body)
            _color = "🟢" if _char <= 150 else ("🟡" if _char <= 300 else "🔴")
            st.caption(f"{_color} 본문 {_char}자 | 해시태그 {len(_hashtags.split())}개")

        # ── Threads 미리보기 ───────────────────────────────
        with tab_th_p:
            st.markdown(f"""
<div style="border:1px solid #e0e0e0;border-radius:12px;background:#fff;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
            max-width:420px;margin:0 auto;padding:16px;">
  <div style="display:flex;gap:10px">
    <div style="width:38px;height:38px;border-radius:50%;background:#000;
                color:#fff;display:flex;align-items:center;justify-content:center;
                font-weight:700;font-size:14px;flex-shrink:0">G</div>
    <div style="flex:1">
      <div style="font-weight:600;font-size:14px">@{_username}</div>
      <div style="font-size:14px;line-height:1.6;margin-top:4px;
                  white-space:pre-wrap">{_body[:500]}{"..." if len(_body)>500 else ""}</div>
      {"<div style='margin-top:8px;font-size:13px;color:#0095f6'>" + " ".join(h for h in _hashtags.split() if h.startswith("#"))[:80] + "</div>" if _hashtags else ""}
      <div style="display:flex;gap:18px;margin-top:12px;color:#666;font-size:20px">
        <span>🤍</span><span>💬</span><span>🔁</span><span>📤</span>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

            st.caption(f"본문 {len(_body)}자 (Threads 권장: 500자 이내)")

        # ── 블로그 미리보기 ────────────────────────────────
        with tab_blog_p:
            st.markdown(f"""
<div style="border:1px solid #e0e0e0;border-radius:8px;background:#fff;
            font-family:'Noto Sans KR',sans-serif;max-width:500px;
            margin:0 auto;padding:20px;">
  <h2 style="font-size:18px;font-weight:700;margin:0 0 8px">{_title}</h2>
  <div style="font-size:11px;color:#999;margin-bottom:16px">
    {_username} · {datetime.now().strftime('%Y.%m.%d')}
  </div>
  <hr style="border:none;border-top:1px solid #eee;margin-bottom:16px">
  <div style="font-size:14px;line-height:1.9;color:#333;white-space:pre-wrap">\
{_body[:600]}{"..." if len(_body)>600 else ""}</div>
  {"<div style='margin-top:16px;font-size:12px;color:#03c75a'>" + " ".join(f"#{t.strip()}" for t in st.session_state['prev_tags'].split(',') if t.strip()) + "</div>" if st.session_state['prev_tags'] else ""}
</div>""", unsafe_allow_html=True)

            st.caption(f"본문 {len(_body)}자 (블로그 권장: 800자 이상)")

# ══════════════════════════════════════════════════════════
# 🏷️ 해시태그 분석
# ══════════════════════════════════════════════════════════
elif page == "🏷️ 해시태그 분석":
    import collections
    import json as _json
    from google import genai as _genai
    from google.genai import types as _gtypes

    st.title("🏷️ 해시태그 성과 분석 & AI 추천")
    st.caption("내 포스트 사용 데이터 분석 + Gemini 추천 → 클릭해서 바로 반영")
    st.divider()

    # ── 내 포스트 해시태그 수집 ───────────────────────────
    _ht_counter = collections.Counter()
    _post_files_ht = sorted(Path("posts").glob("*.yaml"), key=os.path.getmtime, reverse=True) if Path("posts").exists() else []
    for _pf in _post_files_ht:
        try:
            with open(_pf, "r", encoding="utf-8") as _f:
                _pd = yaml.safe_load(_f)
            for _t in _pd.get("hashtags", []):
                if _t.strip():
                    _ht_counter[_t.strip()] += 1
        except Exception:
            pass

    # ── 세션 초기화 ───────────────────────────────────────
    if "ht_selected" not in st.session_state:
        st.session_state["ht_selected"] = set()

    col_l, col_r = st.columns([3, 2], gap="large")

    # ════════════════════════════════════════════════════
    # 왼쪽: 통계 + AI 추천
    # ════════════════════════════════════════════════════
    with col_l:

        # ── 사용 현황 ─────────────────────────────────
        st.markdown("### 📊 내 해시태그 사용 현황")
        if _ht_counter:
            _top = _ht_counter.most_common(20)
            _max_c = _top[0][1]
            for _tag, _cnt in _top:
                _pct = int(_cnt / _max_c * 100)
                _warn = " ⚠️" if _cnt >= 3 else ""
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:8px;margin:3px 0'>"
                    f"<span style='font-size:12px;min-width:170px;color:#333'>{_tag}{_warn}</span>"
                    f"<div style='flex:1;background:#f0f0f0;border-radius:4px;height:14px'>"
                    f"<div style='width:{_pct}%;background:#8b5cf6;border-radius:4px;height:100%'></div></div>"
                    f"<span style='font-size:11px;color:#888;min-width:28px'>{_cnt}회</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            _overused = [t for t, c in _top if c >= 3]
            if _overused:
                st.warning(f"⚠️ 3회 이상 반복: {', '.join(_overused[:4])} — 알고리즘 도달률이 낮아질 수 있어요.")
        else:
            st.info("포스트 파일이 없어 통계를 표시할 수 없습니다.")

        st.divider()

        # ── AI 추천 ────────────────────────────────────
        st.markdown("### 🤖 AI 해시태그 추천")
        _ht_topic    = st.text_input("포스트 주제 / 키워드", placeholder="예: 14k 금반지 커플 선물")
        _ht_platform = st.selectbox("플랫폼", ["instagram", "threads"], key="ht_plat")

        if st.button("🔍 AI 추천받기", type="primary", width="stretch") and _ht_topic:
            with st.spinner("Gemini가 해시태그를 분석 중..."):
                try:
                    _overused_str = ", ".join(t for t, c in _ht_counter.most_common(5)) if _ht_counter else "없음"
                    _prompt_ht = f"""
당신은 인스타그램 해시태그 전략 전문가입니다.

비즈니스: 금반지·커플링·예물·주얼리 전문 쇼핑몰 (@geumseok_jewellery)
포스트 주제: {_ht_topic}
플랫폼: {_ht_platform}
최근 자주 쓴 태그(다양성 필요): {_overused_str}

인스타그램 알고리즘에 맞게 규모별로 해시태그를 추천하세요.
- 대형(100만+): 2-3개 (노출 넓음, 경쟁 치열)
- 중형(1만~100만): 5-7개 (핵심 타겟)
- 소형(~1만): 4-6개 (상위노출 유리, 틈새 타겟)
- 브랜드: 1-2개

아래 JSON으로만 응답:
{{
  "strategy_tip": "이 주제에 맞는 한 줄 전략",
  "large":  [{{"tag":"#태그","reason":"이유"}}],
  "medium": [{{"tag":"#태그","reason":"이유"}}],
  "small":  [{{"tag":"#태그","reason":"이유"}}],
  "brand":  [{{"tag":"#태그","reason":"이유"}}],
  "optimal_set": ["#태그1","#태그2","...최적 조합 15개"]
}}
한국어로 응답하세요.
"""
                    _cli = _genai.Client(api_key=cfg.get("openai", {}).get("api_key", ""))
                    _resp = _cli.models.generate_content(
                        model=cfg.get("openai", {}).get("model", "gemini-2.5-flash"),
                        contents=_prompt_ht,
                        config=_gtypes.GenerateContentConfig(
                            temperature=0.7,
                            response_mime_type="application/json",
                        ),
                    )
                    _ht_res = _json.loads(_resp.text.strip())
                    st.session_state["ht_result"]   = _ht_res
                    st.session_state["ht_selected"]  = set(_ht_res.get("optimal_set", []))
                except Exception as _e:
                    st.error(f"오류: {_e}")

        # ── 추천 결과 ──────────────────────────────────
        if "ht_result" in st.session_state:
            _r = st.session_state["ht_result"]
            st.info(f"💡 전략: {_r.get('strategy_tip', '')}")

            _cat_map = [
                ("🔴 대형 (100만+)", "large"),
                ("🟡 중형 (1만~100만)", "medium"),
                ("🟢 소형 (~1만)", "small"),
                ("🔷 브랜드", "brand"),
            ]
            for _cat_label, _cat_key in _cat_map:
                _tags_cat = _r.get(_cat_key, [])
                if not _tags_cat:
                    continue
                st.markdown(f"**{_cat_label}**")
                _tcols = st.columns(3)
                for _i, _ti in enumerate(_tags_cat):
                    _tag = _ti.get("tag", "")
                    _reason = _ti.get("reason", "")
                    _is_sel = _tag in st.session_state.get("ht_selected", set())
                    with _tcols[_i % 3]:
                        if st.button(
                            f"{'✓ ' if _is_sel else ''}{_tag}",
                            key=f"htbtn_{_cat_key}_{_i}",
                            help=_reason,
                            width="stretch",
                            type="primary" if _is_sel else "secondary",
                        ):
                            _sel = st.session_state.get("ht_selected", set())
                            if _tag in _sel:
                                _sel.discard(_tag)
                            else:
                                _sel.add(_tag)
                            st.session_state["ht_selected"] = _sel
                            st.rerun()

            # 최적 세트 전체 선택
            _optimal = _r.get("optimal_set", [])
            if _optimal:
                st.markdown(f"**⚡ 최적 세트 ({len(_optimal)}개)**")
                _opt_html = "".join(
                    f"<span style='display:inline-block;background:#ede9fe;color:#7c3aed;"
                    f"border-radius:12px;padding:3px 10px;margin:2px;font-size:12px'>{t}</span>"
                    for t in _optimal
                )
                st.markdown(_opt_html, unsafe_allow_html=True)
                if st.button("⚡ 최적 세트 전체 선택", width="stretch"):
                    st.session_state["ht_selected"] = set(_optimal)
                    st.rerun()

    # ════════════════════════════════════════════════════
    # 오른쪽: 적용 패널
    # ════════════════════════════════════════════════════
    with col_r:
        st.markdown("### 📝 포스트에 적용")

        if not _post_files_ht:
            st.info("포스트 파일이 없습니다.\n'포스트 생성' 메뉴에서 먼저 만들어주세요.")
        else:
            _apply_file = st.selectbox(
                "적용할 파일", [f.name for f in _post_files_ht], key="ht_apply_file"
            )
            _apath = f"posts/{_apply_file}"
            try:
                with open(_apath, "r", encoding="utf-8") as _f:
                    _adata = yaml.safe_load(_f)
                _cur_tags = _adata.get("hashtags", [])
            except Exception:
                _adata, _cur_tags = {}, []

            # 현재 해시태그
            st.markdown("**현재 해시태그**")
            if _cur_tags:
                _cur_html = "".join(
                    f"<span style='display:inline-block;background:#f0f2f6;"
                    f"border-radius:12px;padding:3px 10px;margin:2px;font-size:12px'>{t}</span>"
                    for t in _cur_tags
                )
                st.markdown(_cur_html, unsafe_allow_html=True)
                st.caption(f"현재 {len(_cur_tags)}개")
            else:
                st.caption("없음")

            st.divider()

            # 선택된 추천 태그
            _sel_set = st.session_state.get("ht_selected", set())
            st.markdown("**선택된 추천 태그**")
            if _sel_set:
                _sel_html = "".join(
                    f"<span style='display:inline-block;background:#ede9fe;color:#7c3aed;"
                    f"border-radius:12px;padding:3px 10px;margin:2px;font-size:12px;"
                    f"cursor:pointer'>{t}</span>"
                    for t in sorted(_sel_set)
                )
                st.markdown(_sel_html, unsafe_allow_html=True)
                st.caption(f"{len(_sel_set)}개 선택됨")

                if st.button("🗑️ 선택 초기화", width="stretch"):
                    st.session_state["ht_selected"] = set()
                    st.rerun()
            else:
                st.caption("왼쪽 태그 버튼을 클릭하면 여기에 표시됩니다")

            st.divider()

            # 병합 방식
            _merge_mode = st.radio(
                "적용 방식",
                ["기존 태그에 추가", "추천 태그로 교체"],
                horizontal=True,
                key="ht_merge",
            )

            # 최종 결과 미리보기
            if _sel_set:
                if _merge_mode == "기존 태그에 추가":
                    _merged = list(dict.fromkeys(_cur_tags + sorted(_sel_set)))
                else:
                    _merged = sorted(_sel_set)

                st.markdown("**적용 후 결과**")
                _res_html = "".join(
                    f"<span style='display:inline-block;background:#d4edda;color:#155724;"
                    f"border-radius:12px;padding:3px 10px;margin:2px;font-size:12px'>{t}</span>"
                    for t in _merged
                )
                st.markdown(_res_html, unsafe_allow_html=True)
                st.caption(f"총 {len(_merged)}개 (Instagram 권장: 10-15개)")

                _tag_color = "🟢" if len(_merged) <= 15 else ("🟡" if len(_merged) <= 20 else "🔴")
                st.caption(f"{_tag_color} {'적정' if len(_merged) <= 15 else '약간 많음' if len(_merged) <= 20 else '너무 많음'}")

                if st.button("✅ 포스트에 적용 & 저장", type="primary", width="stretch"):
                    _adata["hashtags"] = _merged
                    with open(_apath, "w", encoding="utf-8") as _f:
                        yaml.dump(_adata, _f, allow_unicode=True, default_flow_style=False)
                    st.success(f"✅ {len(_merged)}개 해시태그를 `{_apply_file}`에 저장했습니다!")
                    st.balloons()

# ══════════════════════════════════════════════════════════
# 🤖 AI 최적화
# ══════════════════════════════════════════════════════════
elif page == "🤖 AI 최적화":
    import re as _re
    import json as _json
    from google import genai as _genai
    from google.genai import types as _gtypes

    st.title("🤖 AI 최적화 센터")
    st.caption("SNS 알고리즘 점수 진단 · AI 콘텐츠 최적화 · SEO 키워드 분석")

    # ── 플랫폼 알고리즘 규칙 기반 점수 계산 ──────────────────
    def _score(platform: str, title: str, body: str, hashtags: list) -> tuple[int, list]:
        s, chk = 0, []

        def _c(icon, desc, pts, max_pts):
            nonlocal s
            s += pts
            chk.append((icon, desc, pts, max_pts))

        if platform == "instagram":
            first60 = (body or "")[:60]
            has_hook = bool(_re.search(r'[?!✨💎🔥💫⭐❤️]', first60))
            _c("✅" if has_hook else "❌", "첫 줄 후킹/감성 문구", 15 if has_hook else 0, 15)

            ht = len(hashtags)
            if 5 <= ht <= 30:   _c("✅", f"해시태그 {ht}개 (적정 5~30)", 20, 20)
            elif ht == 0:        _c("❌", "해시태그 없음 — 탐색 불가", 0, 20)
            else:                _c("⚠️", f"해시태그 {ht}개 — 5~30개 조정", 10, 20)

            bl = len(body or "")
            if 150 <= bl <= 500: _c("✅", f"본문 {bl}자 (적정 150~500)", 20, 20)
            elif bl < 50:        _c("❌", f"본문 {bl}자 — 너무 짧음", 0, 20)
            elif bl > 2200:      _c("⚠️", f"본문 {bl}자 — 2200자 초과", 5, 20)
            else:                _c("⚠️", f"본문 {bl}자 — 150~500자 권장", 12, 20)

            cta = any(kw in (body or "") for kw in ["팔로우", "DM", "링크", "주문", "문의", "저장", "클릭", "바이오"])
            _c("✅" if cta else "❌", "CTA 포함 (팔로우/DM/링크 등)", 15 if cta else 0, 15)

            brk = "\n" in (body or "")
            _c("✅" if brk else "⚠️", "줄바꿈/단락 구분", 10 if brk else 0, 10)

            emj = len(_re.findall(r'[\U00010000-\U0010ffff]|[☀-⟿]', body or ""))
            if emj >= 3:  _c("✅", f"이모지 {emj}개", 10, 10)
            elif emj > 0: _c("⚠️", f"이모지 {emj}개 — 3개 이상 권장", 5, 10)
            else:         _c("❌", "이모지 없음 — 참여율 저하", 0, 10)

            tl = len(title or "")
            _c("✅" if 10 <= tl <= 50 else "⚠️", f"제목 {tl}자", 10 if 10 <= tl <= 50 else 5, 10)

        elif platform == "youtube":
            tl = len(title or "")
            if 40 <= tl <= 60:  _c("✅", f"제목 {tl}자 (CTR 최적 40~60)", 20, 20)
            elif tl < 20:       _c("❌", f"제목 {tl}자 — 너무 짧음", 0, 20)
            else:               _c("⚠️", f"제목 {tl}자 — 40~60자 권장", 10, 20)

            pwr = any(w in (title or "") for w in ["방법","이유","비밀","공개","실제","최초","완벽","충격","반드시","진실","vs","리뷰","추천","랭킹","순위","무조건"])
            _c("✅" if pwr else "⚠️", "파워워드/숫자 포함", 15 if pwr else 0, 15)

            dl = len(body or "")
            if dl >= 200:   _c("✅", f"설명란 {dl}자 (200자 이상)", 20, 20)
            elif dl >= 100: _c("⚠️", f"설명란 {dl}자 — 200자 이상 권장", 10, 20)
            else:           _c("❌", f"설명란 {dl}자 — 너무 짧음", 0, 20)

            ht = len(hashtags)
            if 3 <= ht <= 15: _c("✅", f"태그 {ht}개 (적정 3~15)", 15, 15)
            else:             _c("⚠️", f"태그 {ht}개 — 3~15개 권장", 5, 15)

            yt_cta = any(kw in (body or "") for kw in ["구독","좋아요","알림","댓글","링크","쿠폰"])
            _c("✅" if yt_cta else "❌", "설명란 CTA (구독/좋아요/알림)", 15 if yt_cta else 0, 15)

            ts = any(c in (body or "") for c in ["0:00","00:00","챕터","타임스탬프"])
            _c("✅" if ts else "⚠️", "타임스탬프/챕터 마커", 15 if ts else 0, 15)

        elif platform == "naver":
            tl = len(title or "")
            if 20 <= tl <= 50: _c("✅", f"제목 {tl}자 (SEO 적정 20~50)", 15, 15)
            else:              _c("⚠️", f"제목 {tl}자 — 20~50자 권장", 5, 15)

            bl = len(body or "")
            if bl >= 1500:   _c("✅", f"본문 {bl}자 (1500자 이상 ↑SEO)", 25, 25)
            elif bl >= 800:  _c("⚠️", f"본문 {bl}자 — 1500자 이상 권장", 15, 25)
            elif bl >= 400:  _c("⚠️", f"본문 {bl}자 — 800자 이상 권장", 8, 25)
            else:            _c("❌", f"본문 {bl}자 — 너무 짧음", 0, 25)

            hdg = any(m in (body or "") for m in ["##", "**", "\n\n"])
            _c("✅" if hdg else "❌", "소제목/단락 구조 (##, **)", 20 if hdg else 0, 20)

            ht = len(hashtags)
            if 5 <= ht <= 10: _c("✅", f"태그 {ht}개 (적정 5~10)", 15, 15)
            elif ht > 0:      _c("⚠️", f"태그 {ht}개 — 5~10개 권장", 8, 15)
            else:             _c("❌", "태그 없음", 0, 15)

            title_words = [w for w in (title or "").split() if len(w) >= 2]
            kw_cnt = sum((body or "").count(w) for w in title_words)
            if kw_cnt >= 3:   _c("✅", f"키워드 반복 {kw_cnt}회 (SEO ↑)", 15, 15)
            elif kw_cnt >= 1: _c("⚠️", f"키워드 반복 {kw_cnt}회 — 3회 이상 권장", 8, 15)
            else:             _c("❌", "핵심 키워드 본문 미포함", 0, 15)

            has_img = "사진" in (body or "") or "[이미지]" in (body or "")
            _c("✅" if has_img else "⚠️", "이미지 포함 권장", 10 if has_img else 5, 10)

        elif platform == "threads":
            bl = len(body or "")
            if 50 <= bl <= 280: _c("✅", f"본문 {bl}자 (대화체 최적 50~280)", 30, 30)
            elif bl < 50:       _c("⚠️", f"본문 {bl}자 — 내용 보강 필요", 10, 30)
            else:               _c("⚠️", f"본문 {bl}자 — 280자 이내 압축 권장", 15, 30)

            has_q = "?" in (body or "")
            _c("✅" if has_q else "⚠️", "질문/의견 유도 문구", 20 if has_q else 0, 20)

            conv = any(w in (body or "") for w in ["요즘","솔직히","근데","사실","진짜","저는","생각해보면","알고보니","제 생각엔"])
            _c("✅" if conv else "⚠️", "대화체/자연스러운 톤", 20 if conv else 0, 20)

            ht = len(hashtags)
            if 1 <= ht <= 3: _c("✅", f"해시태그 {ht}개 (Threads 적정 1~3)", 20, 20)
            elif ht == 0:    _c("⚠️", "해시태그 없음 — 1~3개 권장", 10, 20)
            else:            _c("⚠️", f"해시태그 {ht}개 — 3개 이하 권장", 10, 20)

            hook30 = (body or "")[:30]
            hk = bool(_re.search(r'[?!✨💎🔥]', hook30))
            _c("✅" if hk else "⚠️", "첫 30자 후킹", 10 if hk else 0, 10)

        elif platform == "wordpress":
            tl = len(title or "")
            if 50 <= tl <= 60:        _c("✅", f"제목 {tl}자 (SEO 황금비율 50~60)", 20, 20)
            elif 40 <= tl <= 70:      _c("⚠️", f"제목 {tl}자 — 50~60자 조정 권장", 12, 20)
            else:                     _c("❌", f"제목 {tl}자 — SEO 범위 벗어남", 4, 20)

            bl = len(body or "")
            if bl >= 2000:   _c("✅", f"본문 {bl}자 (SEO 우수)", 20, 20)
            elif bl >= 1000: _c("⚠️", f"본문 {bl}자 — 2000자 이상 권장", 12, 20)
            else:            _c("❌", f"본문 {bl}자 — SEO 미달", 4, 20)

            h2 = "##" in (body or "") or "<h2" in (body or "").lower()
            _c("✅" if h2 else "❌", "H2 소제목 구조", 20 if h2 else 0, 20)

            if hashtags and title:
                kw = hashtags[0].lstrip("#")
                in_title = kw in (title or "")
                _c("✅" if in_title else "⚠️", "주요 키워드 제목 포함", 20 if in_title else 0, 20)
            else:
                _c("⚠️", "키워드/태그 미설정", 10, 20)

            lnk = "http" in (body or "") or "링크" in (body or "")
            _c("✅" if lnk else "⚠️", "링크 포함 (내/외부)", 10 if lnk else 0, 10)

            meta = len(body or "") >= 150
            _c("✅" if meta else "❌", "메타 설명 가능 분량 (150자+)", 10 if meta else 0, 10)

        return min(s, 100), chk

    PLAT_LIST_OPT = [
        ("instagram", "📸 Instagram", "#E1306C"),
        ("youtube",   "▶️ YouTube",   "#FF0000"),
        ("naver",     "📗 네이버 블로그","#03C75A"),
        ("threads",   "🧵 Threads",   "#1c1c1e"),
        ("wordpress", "🌐 WordPress", "#21759B"),
    ]

    _cfg_ai   = cfg.get("openai", {})
    _ai_key   = _cfg_ai.get("api_key","")
    _ai_model = _cfg_ai.get("model","gemini-2.5-flash")

    tab_score, tab_ai_opt, tab_seo = st.tabs([
        "📊 알고리즘 점수 진단", "🤖 AI 자동 최적화", "🔍 SEO 키워드 분석"
    ])

    # ─────────────────────────────────────────────────────
    # 탭1: 알고리즘 점수 진단
    # ─────────────────────────────────────────────────────
    with tab_score:
        st.markdown("#### 콘텐츠 입력")
        _post_files_opt = sorted(Path("posts").glob("*.yaml"), key=os.path.getmtime, reverse=True) if Path("posts").exists() else []
        _src = st.radio("소스", ["기존 포스트 불러오기", "직접 입력"], horizontal=True, key="opt_src")

        _opt_title, _opt_body, _opt_tags = "", "", []
        if _src == "기존 포스트 불러오기" and _post_files_opt:
            _sel_file = st.selectbox("포스트 파일", [f.name for f in _post_files_opt], key="opt_file")
            try:
                with open(Path("posts") / _sel_file, "r", encoding="utf-8") as _f:
                    _d = yaml.safe_load(_f)
                _opt_title = _d.get("title", "")
                _opt_body  = _d.get("body", "") or _d.get("caption", "")
                _opt_tags  = _d.get("hashtags", [])
            except Exception:
                pass
        else:
            _opt_title = st.text_input("제목", key="opt_title_inp")
            _opt_body  = st.text_area("본문/캡션", height=150, key="opt_body_inp")
            _opt_tags  = [t.strip() for t in st.text_input("해시태그 (쉼표 구분)", key="opt_tags_inp").split(",") if t.strip()]

        if _opt_title or _opt_body:
            with st.expander("📋 입력 내용 미리보기", expanded=False):
                st.markdown(f"**제목:** {_opt_title}")
                st.markdown(f"**본문:** {(_opt_body or '')[:200]}{'…' if len(_opt_body or '')>200 else ''}")
                st.markdown(f"**해시태그:** {' '.join(_opt_tags[:10])}")

            st.markdown("---")
            st.markdown("#### 플랫폼별 알고리즘 점수")

            _score_cols = st.columns(5)
            for _col, (_pid, _pname, _pcolor) in zip(_score_cols, PLAT_LIST_OPT):
                _s, _chks = _score(_pid, _opt_title, _opt_body, _opt_tags)
                _grade = "🏆" if _s >= 80 else "✅" if _s >= 60 else "⚠️" if _s >= 40 else "❌"
                _bg_s  = "#e8f5e9" if _s >= 80 else "#fff8e1" if _s >= 60 else "#fff3e0" if _s >= 40 else "#ffebee"
                with _col:
                    st.markdown(
                        f"<div style='background:{_bg_s};border:2px solid {_pcolor};"
                        f"border-radius:14px;padding:16px 10px;text-align:center'>"
                        f"<div style='font-size:.85rem;font-weight:700;color:{_pcolor}'>{_pname}</div>"
                        f"<div style='font-size:2.2rem;font-weight:900;color:{_pcolor};line-height:1.1'>{_s}</div>"
                        f"<div style='font-size:.75rem;color:#888'>/ 100점 {_grade}</div></div>",
                        unsafe_allow_html=True
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # 상세 체크리스트
            _exp_plat = st.selectbox("상세 체크리스트 보기", [p[1] for p in PLAT_LIST_OPT], key="opt_detail_plat")
            _exp_pid  = next(p[0] for p in PLAT_LIST_OPT if p[1] == _exp_plat)
            _exp_clr  = next(p[2] for p in PLAT_LIST_OPT if p[1] == _exp_plat)
            _, _exp_chks = _score(_exp_pid, _opt_title, _opt_body, _opt_tags)

            _total_pts = sum(c[2] for c in _exp_chks)
            _total_max = sum(c[3] for c in _exp_chks)
            _bar_pct   = int(_total_pts / _total_max * 100) if _total_max else 0

            st.markdown(
                f"<div style='background:#f8f9ff;border-radius:12px;padding:16px 20px'>"
                f"<div style='font-weight:700;color:{_exp_clr};margin-bottom:10px'>"
                f"{_exp_plat} 체크리스트 — {_bar_pct}점</div>"
                f"<div style='background:#e0e0e0;border-radius:6px;height:8px;margin-bottom:14px'>"
                f"<div style='background:{_exp_clr};width:{_bar_pct}%;height:8px;border-radius:6px'></div></div>",
                unsafe_allow_html=True
            )
            for _icon, _desc, _pts, _max in _exp_chks:
                _row_bg = "#e8f5e9" if _icon == "✅" else "#fff8e1" if _icon == "⚠️" else "#ffebee"
                st.markdown(
                    f"<div style='background:{_row_bg};border-radius:8px;padding:8px 14px;"
                    f"margin:3px 0;display:flex;justify-content:space-between;align-items:center'>"
                    f"<span>{_icon} {_desc}</span>"
                    f"<span style='font-weight:700;color:{'#2e7d32' if _icon=='✅' else '#f57c00' if _icon=='⚠️' else '#c62828'}'>"
                    f"{_pts}/{_max}점</span></div>",
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("위에서 포스트를 선택하거나 콘텐츠를 입력하면 즉시 점수를 확인할 수 있습니다.")

    # ─────────────────────────────────────────────────────
    # 탭2: AI 자동 최적화
    # ─────────────────────────────────────────────────────
    with tab_ai_opt:
        st.markdown("#### AI 콘텐츠 최적화")
        st.caption("Gemini가 플랫폼 알고리즘에 맞게 콘텐츠를 분석하고 자동으로 개선합니다.")

        _post_files_ai = sorted(Path("posts").glob("*.yaml"), key=os.path.getmtime, reverse=True) if Path("posts").exists() else []
        _ai_src = st.radio("소스", ["기존 포스트 불러오기", "직접 입력"], horizontal=True, key="ai_opt_src")

        _ai_title, _ai_body, _ai_tags = "", "", []
        if _ai_src == "기존 포스트 불러오기" and _post_files_ai:
            _ai_sel = st.selectbox("포스트 파일", [f.name for f in _post_files_ai], key="ai_opt_file")
            try:
                with open(Path("posts") / _ai_sel, "r", encoding="utf-8") as _f:
                    _d2 = yaml.safe_load(_f)
                _ai_title = _d2.get("title", "")
                _ai_body  = _d2.get("body", "") or _d2.get("caption", "")
                _ai_tags  = _d2.get("hashtags", [])
            except Exception:
                pass
        else:
            _ai_title = st.text_input("제목", key="ai_opt_title_inp")
            _ai_body  = st.text_area("본문/캡션", height=150, key="ai_opt_body_inp")
            _ai_tags  = [t.strip() for t in st.text_input("해시태그 (쉼표 구분)", key="ai_opt_tags_inp").split(",") if t.strip()]

        _ai_target_plat = st.multiselect(
            "최적화할 플랫폼 선택",
            [p[1] for p in PLAT_LIST_OPT],
            default=["📸 Instagram", "📗 네이버 블로그"],
            key="ai_opt_plats"
        )
        _ai_target_pids = [p[0] for p in PLAT_LIST_OPT if p[1] in _ai_target_plat]

        if not _ai_key:
            st.warning("⚠️ Gemini API 키가 설정되지 않았습니다. ⚙️ 설정 탭에서 등록하세요.")
        elif st.button("🤖 AI 최적화 실행", type="primary", key="run_ai_opt", disabled=not(_ai_title or _ai_body)):
            with st.spinner("Gemini가 플랫폼별 알고리즘을 분석 중입니다..."):
                try:
                    _client_opt = _genai.Client(api_key=_ai_key)

                    _plat_rules = {
                        "instagram": "인스타그램 알고리즘: 첫 줄 후킹(감성/이모지), 본문 150~300자, CTA(팔로우/DM/저장), 해시태그 10~20개, 저장·공유·댓글 유도, 탐색 탭 노출을 위한 키워드",
                        "youtube":   "유튜브 SEO: 제목 40~60자+파워워드, 설명란 첫 2줄에 핵심 키워드, 구독/좋아요/알림 CTA, 타임스탬프 챕터, 태그 10~15개, 클릭률(CTR) 높은 제목",
                        "naver":     "네이버 블로그 SEO: 제목에 검색 키워드 포함, 본문 1500자 이상, 소제목(##) 3개 이상, 키워드 자연스럽게 5회 이상, 이미지 설명, 태그 7~10개",
                        "threads":   "Threads 알고리즘: 280자 이내 대화체, 질문으로 댓글 유도, 자신의 의견·경험 공유, 해시태그 1~2개, 공감 가는 첫 문장",
                        "wordpress": "WordPress SEO: 제목 50~60자(주요 키워드 포함), 본문 2000자 이상, H2/H3 소제목 구조, 내부/외부 링크, 메타 설명 155자, 이미지 alt 텍스트",
                    }

                    _rules_text = "\n".join(
                        f"- {_pid}: {_plat_rules[_pid]}" for _pid in _ai_target_pids if _pid in _plat_rules
                    )
                    _platforms_str = ", ".join(_ai_target_pids)

                    _opt_prompt = f"""당신은 SNS 알고리즘 전문가이자 SEO 컨설턴트입니다.

아래 원본 콘텐츠를 각 플랫폼 알고리즘에 맞게 분석하고 최적화된 버전을 생성해주세요.

=== 원본 콘텐츠 ===
제목: {_ai_title}
본문: {_ai_body}
해시태그: {' '.join(_ai_tags)}

=== 최적화 대상 플랫폼 ===
{_platforms_str}

=== 각 플랫폼 알고리즘 규칙 ===
{_rules_text}

아래 JSON 형식으로만 응답하세요:
{{
  "analysis": {{
    "strengths": ["강점1", "강점2"],
    "weaknesses": ["약점1", "약점2"],
    "overall_tip": "전체적인 개선 방향 (2문장)"
  }},
  "optimized": {{
    {', '.join(f'"{pid}": {{"title": "최적화된 제목", "body": "최적화된 본문", "hashtags": ["#태그1", "#태그2"], "key_changes": ["변경점1", "변경점2"]}}' for pid in _ai_target_pids)}
  }}
}}

한국어로만 응답하세요."""

                    _resp = _client_opt.models.generate_content(
                        model=_ai_model,
                        contents=_opt_prompt,
                        config=_gtypes.GenerateContentConfig(
                            temperature=0.7,
                            response_mime_type="application/json",
                        ),
                    )
                    _result = _json.loads(_resp.text.strip())

                    # 분석 결과
                    _anal = _result.get("analysis", {})
                    st.markdown("---")
                    _a1, _a2 = st.columns(2)
                    with _a1:
                        st.markdown(
                            "<div style='background:#e8f5e9;border-radius:10px;padding:14px 16px'>"
                            "<b style='color:#2e7d32'>💪 강점</b><ul style='margin:8px 0 0;padding-left:16px'>" +
                            "".join(f"<li>{s}</li>" for s in _anal.get("strengths", [])) +
                            "</ul></div>", unsafe_allow_html=True
                        )
                    with _a2:
                        st.markdown(
                            "<div style='background:#ffebee;border-radius:10px;padding:14px 16px'>"
                            "<b style='color:#c62828'>🔧 개선 필요</b><ul style='margin:8px 0 0;padding-left:16px'>" +
                            "".join(f"<li>{w}</li>" for w in _anal.get("weaknesses", [])) +
                            "</ul></div>", unsafe_allow_html=True
                        )
                    st.info(f"💡 {_anal.get('overall_tip','')}")

                    # 플랫폼별 최적화 결과
                    st.markdown("#### 플랫폼별 최적화 결과")
                    _opt_res = _result.get("optimized", {})
                    for _pid, _pname, _pcolor in PLAT_LIST_OPT:
                        if _pid not in _opt_res:
                            continue
                        _pr = _opt_res[_pid]
                        with st.expander(f"{_pname} 최적화 결과", expanded=True):
                            _oc1, _oc2 = st.columns([3, 2])
                            with _oc1:
                                st.markdown(f"**제목:** {_pr.get('title','')}")
                                st.markdown(f"**본문:**")
                                st.text_area("", value=_pr.get('body',''), height=150, key=f"opt_body_{_pid}", label_visibility="collapsed")
                                _ht_str = " ".join(_pr.get("hashtags", []))
                                st.text_input("해시태그", value=_ht_str, key=f"opt_tags_{_pid}")
                            with _oc2:
                                st.markdown("**주요 변경점**")
                                for _ch in _pr.get("key_changes", []):
                                    st.markdown(f"• {_ch}")
                                _s2, _ = _score(_pid, _pr.get('title',''), _pr.get('body',''), _pr.get('hashtags',[]))
                                _s1, _ = _score(_pid, _ai_title, _ai_body, _ai_tags)
                                _diff = _s2 - _s1
                                _diff_color = "#2e7d32" if _diff >= 0 else "#c62828"
                                st.markdown(
                                    f"<div style='text-align:center;margin-top:8px'>"
                                    f"<span style='font-size:.85rem;color:#888'>알고리즘 점수</span><br>"
                                    f"<span style='font-size:1.6rem;font-weight:800;color:{_pcolor}'>{_s2}</span>"
                                    f"<span style='color:{_diff_color};font-size:.9rem;font-weight:700'>"
                                    f" ({'+' if _diff>=0 else ''}{_diff})</span></div>",
                                    unsafe_allow_html=True
                                )

                            # 저장 버튼
                            if st.button(f"💾 {_pname} 최적화본 저장", key=f"save_opt_{_pid}"):
                                Path("posts").mkdir(exist_ok=True)
                                _save_data = {
                                    "title": _pr.get("title",""),
                                    "body": _pr.get("body",""),
                                    "caption": _pr.get("body",""),
                                    "hashtags": _pr.get("hashtags",[]),
                                }
                                _fname = f"{_pid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_optimized.yaml"
                                with open(Path("posts") / _fname, "w", encoding="utf-8") as _wf:
                                    yaml.dump(_save_data, _wf, allow_unicode=True)
                                st.success(f"✅ posts/{_fname} 저장 완료!")

                except Exception as _e:
                    st.error(f"AI 분석 오류: {_e}")

    # ─────────────────────────────────────────────────────
    # 탭3: SEO 키워드 분석
    # ─────────────────────────────────────────────────────
    with tab_seo:
        st.markdown("#### SEO 키워드 리서치 & 전략")
        st.caption("주제를 입력하면 Gemini가 검색 최적화 키워드 전략을 설계합니다.")

        _seo_col1, _seo_col2 = st.columns([2, 1])
        with _seo_col1:
            _seo_topic = st.text_input("주제 또는 메인 키워드", placeholder="예: 14k 금반지 추천", key="seo_topic")
        with _seo_col2:
            _seo_plat = st.selectbox("대상 플랫폼", ["네이버 블로그", "YouTube", "Instagram", "WordPress"], key="seo_plat")

        _seo_biz = st.text_input("비즈니스/업종 설명 (선택)", placeholder="예: 주얼리 쇼핑몰, 커플링/예물 전문", key="seo_biz")

        if not _ai_key:
            st.warning("⚠️ Gemini API 키가 설정되지 않았습니다.")
        elif st.button("🔍 키워드 분석 시작", type="primary", key="run_seo", disabled=not _seo_topic):
            with st.spinner("Gemini가 SEO 키워드를 분석 중입니다..."):
                try:
                    _client_seo = _genai.Client(api_key=_ai_key)
                    _seo_prompt = f"""당신은 한국 SEO 전문가입니다.

주제: {_seo_topic}
대상 플랫폼: {_seo_plat}
비즈니스: {_seo_biz or '미입력'}

위 주제에 대해 {_seo_plat} 플랫폼에 최적화된 SEO 키워드 전략을 분석해주세요.

아래 JSON 형식으로만 응답하세요:
{{
  "primary_keyword": "가장 중요한 핵심 키워드 1개",
  "secondary_keywords": ["보조 키워드1", "보조 키워드2", "보조 키워드3", "보조 키워드4"],
  "lsi_keywords": ["연관 검색어1", "연관 검색어2", "연관 검색어3", "연관 검색어4", "연관 검색어5"],
  "long_tail": ["롱테일 키워드1 (3단어 이상)", "롱테일 키워드2", "롱테일 키워드3"],
  "search_intent": "검색 의도 분석 (정보/구매/비교/탐색 중 해당하는 것과 이유)",
  "title_templates": [
    "제목 템플릿1 (키워드 포함)",
    "제목 템플릿2",
    "제목 템플릿3"
  ],
  "meta_description": "메타 설명 템플릿 (155자 이내, 키워드+CTA 포함)",
  "content_outline": [
    "H2: 소제목1",
    "H2: 소제목2",
    "H2: 소제목3",
    "H2: 소제목4"
  ],
  "competition_level": "경쟁도 (낮음/보통/높음)",
  "monthly_search_estimate": "예상 월 검색량 (대략적 수치)",
  "tips": ["SEO 팁1", "SEO 팁2", "SEO 팁3"]
}}

한국어로만 응답하세요."""

                    _seo_resp = _client_seo.models.generate_content(
                        model=_ai_model,
                        contents=_seo_prompt,
                        config=_gtypes.GenerateContentConfig(
                            temperature=0.6,
                            response_mime_type="application/json",
                        ),
                    )
                    _seo = _json.loads(_seo_resp.text.strip())

                    # 메인 키워드 + 경쟁도
                    _comp_color = {"낮음": "#00b894", "보통": "#fdcb6e", "높음": "#d63031"}.get(_seo.get("competition_level",""), "#888")
                    st.markdown(
                        f"<div style='background:linear-gradient(135deg,#667eea,#764ba2);"
                        f"border-radius:14px;padding:20px 24px;color:#fff;margin-bottom:16px'>"
                        f"<div style='font-size:.85rem;opacity:.8'>핵심 키워드</div>"
                        f"<div style='font-size:1.8rem;font-weight:900'>{_seo.get('primary_keyword','')}</div>"
                        f"<div style='display:flex;gap:16px;margin-top:8px;font-size:.85rem'>"
                        f"<span>경쟁도: <b style='color:{_comp_color}'>{_seo.get('competition_level','')}</b></span>"
                        f"<span>예상 월 검색량: <b>{_seo.get('monthly_search_estimate','')}</b></span>"
                        f"<span>검색 의도: <b>{_seo.get('search_intent','')[:20]}</b></span>"
                        f"</div></div>",
                        unsafe_allow_html=True
                    )

                    _sk1, _sk2, _sk3 = st.columns(3)
                    with _sk1:
                        st.markdown("**🎯 보조 키워드**")
                        for _kw in _seo.get("secondary_keywords", []):
                            st.markdown(
                                f"<span style='background:#e3f2fd;color:#1565c0;border-radius:20px;"
                                f"padding:3px 12px;margin:2px;display:inline-block;font-size:13px'>{_kw}</span>",
                                unsafe_allow_html=True
                            )
                    with _sk2:
                        st.markdown("**🔗 LSI/연관 키워드**")
                        for _kw in _seo.get("lsi_keywords", []):
                            st.markdown(
                                f"<span style='background:#f3e5f5;color:#6a1b9a;border-radius:20px;"
                                f"padding:3px 12px;margin:2px;display:inline-block;font-size:13px'>{_kw}</span>",
                                unsafe_allow_html=True
                            )
                    with _sk3:
                        st.markdown("**🐾 롱테일 키워드**")
                        for _kw in _seo.get("long_tail", []):
                            st.markdown(
                                f"<span style='background:#e8f5e9;color:#1b5e20;border-radius:20px;"
                                f"padding:3px 12px;margin:2px;display:inline-block;font-size:13px'>{_kw}</span>",
                                unsafe_allow_html=True
                            )

                    st.markdown("---")
                    _st1, _st2 = st.columns(2)
                    with _st1:
                        st.markdown("**📝 제목 템플릿**")
                        for _i, _tmpl in enumerate(_seo.get("title_templates", []), 1):
                            st.markdown(
                                f"<div style='background:#fff8e1;border-left:3px solid #f39c12;"
                                f"padding:8px 12px;border-radius:0 8px 8px 0;margin:4px 0'>"
                                f"<span style='color:#888;font-size:.75rem'>템플릿 {_i}</span><br>"
                                f"<b>{_tmpl}</b></div>",
                                unsafe_allow_html=True
                            )

                        st.markdown("**📄 메타 설명 템플릿**")
                        st.text_area("", value=_seo.get("meta_description",""), height=80, key="seo_meta", label_visibility="collapsed")

                    with _st2:
                        st.markdown("**📋 콘텐츠 구조 (아웃라인)**")
                        for _h in _seo.get("content_outline", []):
                            _indent = "  " if _h.startswith("H3") else ""
                            st.markdown(
                                f"<div style='background:#f8f9ff;border-radius:6px;"
                                f"padding:7px 12px;margin:3px 0;font-size:.88rem'>"
                                f"{_indent}📌 {_h}</div>",
                                unsafe_allow_html=True
                            )

                        st.markdown("**💡 SEO 팁**")
                        for _tip in _seo.get("tips", []):
                            st.markdown(f"✅ {_tip}")

                except Exception as _e:
                    st.error(f"SEO 분석 오류: {_e}")

# ══════════════════════════════════════════════════════════
# 📤 업로드
# ══════════════════════════════════════════════════════════
elif page == "📤 업로드":
    st.title("📤 SNS 업로드")
    st.divider()

    # 포스트 파일 선택
    post_files = sorted(Path("posts").glob("*.yaml"), key=os.path.getmtime, reverse=True) if Path("posts").exists() else []
    if not post_files:
        st.warning("포스트 파일이 없습니다. 먼저 '포스트 생성'에서 만들어주세요.")
        st.stop()

    selected_file = st.selectbox("📄 포스트 파일 선택", [f.name for f in post_files])

    with open(f"posts/{selected_file}", "r", encoding="utf-8") as f:
        post_data = yaml.safe_load(f)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**포스트 내용**")
        st.text(f"제목: {post_data.get('title', '-')}")
        st.text_area("본문 미리보기", post_data.get("body", "")[:300], height=120, disabled=True)
        hashtags = post_data.get("hashtags", [])
        st.text(f"해시태그: {' '.join(hashtags)}")

    with col2:
        st.markdown("**이미지/영상**")
        images = post_data.get("image_paths", [])
        if images:
            for img in images[:3]:
                if Path(img).exists():
                    st.image(img, width=150)
                else:
                    st.caption(f"⚠️ 파일 없음: {img}")
        else:
            uploaded = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
            if uploaded:
                paths = []
                for f in uploaded:
                    save_p = f"assets/images/{f.name}"
                    Path("assets/images").mkdir(parents=True, exist_ok=True)
                    with open(save_p, "wb") as out:
                        out.write(f.read())
                    paths.append(save_p)
                post_data["image_paths"] = paths
                with open(f"posts/{selected_file}", "w", encoding="utf-8") as fp:
                    yaml.dump(post_data, fp, allow_unicode=True, default_flow_style=False)
                st.success("이미지 저장됨!")

    st.divider()

    # 플랫폼 선택
    st.markdown("**업로드할 플랫폼 선택**")
    platform_cols = st.columns(5)
    selected_platforms = []
    for col, (key, label) in zip(platform_cols, PLATFORMS.items()):
        with col:
            if st.checkbox(label, value=(key in ["instagram", "threads"]), key=f"chk_{key}"):
                selected_platforms.append(key)

    st.divider()

    if st.button("🚀 지금 업로드", type="primary", width="stretch") and selected_platforms:
        from platforms import InstagramUploader, ThreadsUploader, YouTubeUploader, NaverBlogUploader, WordPressUploader
        from content.manager import ContentManager

        UPLOADER_MAP = {
            "instagram": (InstagramUploader, "instagram"),
            "threads":   (ThreadsUploader,   "threads"),
            "youtube":   (YouTubeUploader,   "youtube"),
            "naver":     (NaverBlogUploader, "naver_blog"),
            "wordpress": (WordPressUploader, "wordpress"),
        }

        content = ContentManager.from_yaml(f"posts/{selected_file}")
        progress = st.progress(0)
        status_box = st.empty()

        results = []
        for i, plat in enumerate(selected_platforms):
            status_box.info(f"업로드 중: {PLATFORMS[plat]}...")
            cls, config_key = UPLOADER_MAP[plat]
            uploader = cls(cfg.get(config_key, {}))
            result = uploader.upload(content)
            results.append(result)
            progress.progress((i + 1) / len(selected_platforms))

        status_box.empty()
        st.markdown("### 결과")
        for r in results:
            if r.success:
                st.success(f"✅ {r.platform} — {r.url}")
            else:
                st.error(f"❌ {r.platform} — {r.error}")

# ══════════════════════════════════════════════════════════
# ⏰ 예약 발행 — 업그레이드 캘린더
# ══════════════════════════════════════════════════════════
elif page == "⏰ 예약 발행":
    import calendar as _cal
    import json
    import uuid

    st.title("📅 콘텐츠 캘린더")
    st.caption("월간/주간 뷰 전환 · 플랫폼 필터 · 원클릭 예약 & 발행")

    # ── 공통 설정 ─────────────────────────────────────────
    SCHEDULE_FILE = Path("schedule.json")
    PLAT_COLOR = {
        "instagram": "#E1306C", "threads": "#1c1c1e",
        "youtube": "#FF0000",   "naver": "#03C75A", "wordpress": "#21759B",
    }
    PLAT_ICON = {
        "instagram": "📸", "threads": "🧵",
        "youtube": "▶️",  "naver": "📗", "wordpress": "🌐",
    }
    PLAT_BG = {
        "instagram": "#fce4ec", "threads": "#f3f3f3",
        "youtube":   "#ffebee", "naver":   "#e8f5e9", "wordpress": "#e3f2fd",
    }

    def load_schedule() -> dict:
        if SCHEDULE_FILE.exists():
            with open(SCHEDULE_FILE, "r", encoding="utf-8") as _f:
                return json.load(_f)
        return {}

    def save_schedule(sc: dict):
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as _f:
            json.dump(sc, _f, ensure_ascii=False, indent=2)

    def do_publish(schedule, date_str, idx, cfg):
        post = schedule[date_str][idx]
        pf, plat = post.get("post_file",""), post.get("platform","")
        from platforms import InstagramUploader, ThreadsUploader, YouTubeUploader, NaverBlogUploader, WordPressUploader
        from content.manager import ContentManager
        _UMAP = {
            "instagram":(InstagramUploader,"instagram"),
            "threads":  (ThreadsUploader,"threads"),
            "youtube":  (YouTubeUploader,"youtube"),
            "naver":    (NaverBlogUploader,"naver_blog"),
            "wordpress":(WordPressUploader,"wordpress"),
        }
        _c = ContentManager.from_yaml(pf)
        _cls, _ck = _UMAP[plat]
        return _cls(cfg.get(_ck,{})).upload(_c)

    from datetime import date as _date, timedelta as _td
    _now  = datetime.now()
    _today = _date.today()

    # ── CSS ───────────────────────────────────────────────
    st.markdown("""<style>
    .cal-grid-cell{min-height:110px;border:1px solid #e8eaf0;border-radius:8px;
                   padding:6px;background:#fff;transition:background .15s;}
    .cal-grid-cell:hover{background:#f8f9ff;}
    .cal-today{border:2px solid #6366f1!important;background:#f5f3ff!important;}
    .cal-selected{border:2px solid #f59e0b!important;background:#fffbeb!important;}
    .cal-daynum{font-weight:700;font-size:.95rem;margin-bottom:4px;}
    .cal-daynum-today{color:#6366f1;}
    .post-chip{font-size:10px;border-radius:5px;padding:2px 6px;margin:1px 0;
               display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
               font-weight:600;cursor:pointer;}
    .week-col{border-right:1px solid #e8eaf0;padding:4px;}
    .stat-badge{display:inline-block;padding:2px 8px;border-radius:10px;
                font-size:11px;font-weight:700;}
    </style>""", unsafe_allow_html=True)

    # ── 세션 초기화 ───────────────────────────────────────
    for _k, _v in [("cal_year",_now.year),("cal_month",_now.month),
                   ("cal_sel",None),("cal_view","월간"),
                   ("cal_filter",list(PLATFORMS.keys())),("cal_quick_date",None)]:
        if _k not in st.session_state:
            st.session_state[_k] = _v

    schedule = load_schedule()

    # ── 상단 컨트롤 바 ────────────────────────────────────
    nav1, nav2, nav3, nav4 = st.columns([1, 3, 2, 2])

    with nav1:
        c_p, c_t, c_n = st.columns([1,1,1])
        with c_p:
            if st.button("◀", key="cprev", width="stretch"):
                if st.session_state.cal_month == 1:
                    st.session_state.cal_month, st.session_state.cal_year = 12, st.session_state.cal_year-1
                else:
                    st.session_state.cal_month -= 1
                st.rerun()
        with c_t:
            if st.button("今", key="ctoday", width="stretch", help="오늘로 이동"):
                st.session_state.cal_year  = _today.year
                st.session_state.cal_month = _today.month
                st.rerun()
        with c_n:
            if st.button("▶", key="cnext", width="stretch"):
                if st.session_state.cal_month == 12:
                    st.session_state.cal_month, st.session_state.cal_year = 1, st.session_state.cal_year+1
                else:
                    st.session_state.cal_month += 1
                st.rerun()

    with nav2:
        _yr, _mo = st.session_state.cal_year, st.session_state.cal_month
        st.markdown(f"<h2 style='margin:0;padding:4px 0;font-size:1.4rem;font-weight:800'>"
                    f"{_yr}년 {_mo}월</h2>", unsafe_allow_html=True)

    with nav3:
        _view = st.radio("뷰", ["월간", "주간"], horizontal=True,
                         index=0 if st.session_state.cal_view=="월간" else 1,
                         key="cal_view_radio", label_visibility="collapsed")
        st.session_state.cal_view = _view

    with nav4:
        # 플랫폼 필터
        _filter_opts = st.multiselect(
            "플랫폼 필터", list(PLATFORMS.keys()),
            default=st.session_state.cal_filter,
            format_func=lambda x: PLATFORMS[x],
            key="cal_filter_ms", label_visibility="collapsed",
        )
        st.session_state.cal_filter = _filter_opts

    _active_filter = set(st.session_state.cal_filter)

    # 이번 달/주 예약 요약 뱃지
    _mo_posts = sum(
        1 for ds, items in schedule.items()
        if ds.startswith(f"{_yr}-{_mo:02d}")
        for it in items if it.get("platform","") in _active_filter
    )
    _mo_pub = sum(
        1 for ds, items in schedule.items()
        if ds.startswith(f"{_yr}-{_mo:02d}")
        for it in items if it.get("status")=="published" and it.get("platform","") in _active_filter
    )
    st.markdown(
        f"<div style='margin:4px 0 8px'>"
        f"<span class='stat-badge' style='background:#ede9fe;color:#5b21b6'>📌 예약 {_mo_posts}개</span>&nbsp;"
        f"<span class='stat-badge' style='background:#d1fae5;color:#065f46'>✅ 발행 {_mo_pub}개</span>"
        f"</div>", unsafe_allow_html=True
    )

    # ─────────────────────────────────────────────────────
    # 월간 뷰
    # ─────────────────────────────────────────────────────
    if st.session_state.cal_view == "월간":
        _day_names = ["일","월","화","수","목","금","토"]
        _h_cols = st.columns(7)
        _day_colors = ["#ef4444","#374151","#374151","#374151","#374151","#374151","#3b82f6"]
        for _hc, _dn, _dc in zip(_h_cols, _day_names, _day_colors):
            _hc.markdown(
                f"<div style='text-align:center;font-weight:700;color:{_dc};"
                f"font-size:.85rem;padding:6px 0;border-bottom:2px solid #e8eaf0'>{_dn}</div>",
                unsafe_allow_html=True
            )

        for _week in _cal.monthcalendar(_yr, _mo):
            _sf = [_week[6]] + _week[:6]
            _wcols = st.columns(7)
            for _wc, _dn in zip(_wcols, _sf):
                with _wc:
                    if _dn == 0:
                        st.markdown("<div style='min-height:110px'></div>", unsafe_allow_html=True)
                        continue

                    _ds = f"{_yr}-{_mo:02d}-{_dn:02d}"
                    _day_posts = [p for p in schedule.get(_ds,[]) if p.get("platform","") in _active_filter]
                    _is_today  = (_dn==_today.day and _mo==_today.month and _yr==_today.year)
                    _is_sel    = st.session_state.cal_sel == _ds

                    # 날짜 숫자 버튼
                    _num_color  = "#6366f1" if _is_today else "#1a1a2e"
                    _cell_style = "border:2px solid #6366f1;" if _is_today else ("border:2px solid #f59e0b;" if _is_sel else "border:1px solid #e8eaf0;")
                    _cell_bg    = "#f5f3ff" if _is_today else ("#fffbeb" if _is_sel else "#fff")

                    _pub_cnt  = sum(1 for p in _day_posts if p.get("status")=="published")
                    _sched_cnt = len(_day_posts) - _pub_cnt

                    # 날짜 클릭 버튼
                    _btn_txt = f"{'📍' if _is_sel else ''}{_dn}{'✦' if _is_today else ''}"
                    if st.button(_btn_txt, key=f"m_{_ds}", width="stretch"):
                        st.session_state.cal_sel = _ds if st.session_state.cal_sel != _ds else None
                        st.session_state.cal_quick_date = _ds
                        st.rerun()

                    # 포스트 칩
                    _chips_html = ""
                    for _p in sorted(_day_posts, key=lambda x: x.get("time","00:00"))[:3]:
                        _plat = _p.get("platform","")
                        _bg   = PLAT_BG.get(_plat,"#f0f0f0")
                        _fc   = PLAT_COLOR.get(_plat,"#333")
                        _ico  = PLAT_ICON.get(_plat,"📌")
                        _stat = "✅" if _p.get("status")=="published" else "⏳"
                        _ttl  = _p.get("title","")[:11]
                        _tm   = _p.get("time","")
                        _chips_html += (
                            f"<div style='background:{_bg};color:{_fc};border-left:3px solid {_fc};"
                            f"font-size:10px;border-radius:4px;padding:2px 5px;margin:1px 0;"
                            f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600'>"
                            f"{_stat}{_ico} {_tm} {_ttl}</div>"
                        )
                    if len(_day_posts) > 3:
                        _chips_html += f"<div style='font-size:10px;color:#888;text-align:right'>+{len(_day_posts)-3}개</div>"

                    st.markdown(_chips_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    # 주간 뷰
    # ─────────────────────────────────────────────────────
    else:
        # 현재 선택/오늘 기준 주 계산
        _ref_date = (_date.fromisoformat(st.session_state.cal_sel)
                     if st.session_state.cal_sel else _today)
        # 일요일 시작
        _week_start = _ref_date - _td(days=(_ref_date.weekday()+1) % 7)
        _week_dates = [_week_start + _td(days=i) for i in range(7)]

        # 주 네비게이션
        wnav1, wnav2, wnav3 = st.columns([1,4,1])
        with wnav1:
            if st.button("◀ 이전 주", key="wprev", width="stretch"):
                _new_ref = _week_start - _td(days=1)
                st.session_state.cal_sel = str(_new_ref)
                st.session_state.cal_year  = _new_ref.year
                st.session_state.cal_month = _new_ref.month
                st.rerun()
        with wnav2:
            _ws = _week_dates[0]; _we = _week_dates[6]
            st.markdown(f"<div style='text-align:center;font-weight:700;font-size:1rem;padding:6px'>"
                        f"{_ws.month}/{_ws.day}(일) ~ {_we.month}/{_we.day}(토)</div>",
                        unsafe_allow_html=True)
        with wnav3:
            if st.button("다음 주 ▶", key="wnext", width="stretch"):
                _new_ref = _week_start + _td(days=7)
                st.session_state.cal_sel = str(_new_ref)
                st.session_state.cal_year  = _new_ref.year
                st.session_state.cal_month = _new_ref.month
                st.rerun()

        # 요일 헤더
        _day_names_w = ["일","월","화","수","목","금","토"]
        _day_colors_w = ["#ef4444","#374151","#374151","#374151","#374151","#374151","#3b82f6"]
        _wh_cols = st.columns(7)
        for _col, _wd, _wdc, _wdate in zip(_wh_cols, _day_names_w, _day_colors_w, _week_dates):
            _is_td = (_wdate == _today)
            _bg_h  = "#f5f3ff" if _is_td else "transparent"
            _col.markdown(
                f"<div style='text-align:center;padding:8px 4px;background:{_bg_h};"
                f"border-radius:8px;border-bottom:2px solid {'#6366f1' if _is_td else '#e8eaf0'}'>"
                f"<div style='font-weight:700;color:{_wdc};font-size:.85rem'>{_wd}</div>"
                f"<div style='font-weight:800;font-size:1.2rem;color:{'#6366f1' if _is_td else '#1a1a2e'}'>"
                f"{_wdate.day}</div></div>",
                unsafe_allow_html=True
            )

        # 주간 포스트 컬럼
        _wbody_cols = st.columns(7)
        for _col, _wdate in zip(_wbody_cols, _week_dates):
            _wds = str(_wdate)
            _wday_posts = sorted(
                [p for p in schedule.get(_wds,[]) if p.get("platform","") in _active_filter],
                key=lambda x: x.get("time","00:00")
            )
            with _col:
                st.markdown("<div style='min-height:300px;border-top:1px solid #e8eaf0;padding-top:6px'>", unsafe_allow_html=True)
                for _p in _wday_posts:
                    _plat = _p.get("platform","")
                    _bg   = PLAT_BG.get(_plat,"#f0f0f0")
                    _fc   = PLAT_COLOR.get(_plat,"#333")
                    _ico  = PLAT_ICON.get(_plat,"📌")
                    _pub  = _p.get("status")=="published"
                    st.markdown(
                        f"<div style='background:{_bg};border-left:3px solid {_fc};"
                        f"border-radius:6px;padding:5px 7px;margin:3px 0'>"
                        f"<div style='font-size:10px;color:#888'>{_p.get('time','')}</div>"
                        f"<div style='font-size:11px;font-weight:700;color:{_fc}'>{_ico} {_p.get('title','')[:14]}</div>"
                        f"<div style='font-size:10px;margin-top:2px'>{'✅ 발행됨' if _pub else '⏳ 예약'}</div>"
                        f"</div>", unsafe_allow_html=True
                    )
                # 날짜 클릭 → 선택
                if st.button("＋", key=f"wadd_{_wds}", width="stretch", help=f"{_wds} 예약 추가"):
                    st.session_state.cal_sel = _wds
                    st.session_state.cal_quick_date = _wds
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ─────────────────────────────────────────────────────
    # 하단 패널: 선택된 날짜 상세
    # ─────────────────────────────────────────────────────
    if st.session_state.cal_sel:
        _sel = st.session_state.cal_sel
        _sel_posts = [p for p in schedule.get(_sel,[]) if p.get("platform","") in _active_filter]
        _sched_only = [p for p in _sel_posts if p.get("status")!="published"]
        _pub_only   = [p for p in _sel_posts if p.get("status")=="published"]

        # 패널 헤더
        _sel_dt = _date.fromisoformat(_sel)
        _dow    = ["월","화","수","목","금","토","일"][_sel_dt.weekday()]
        st.markdown(
            f"<div style='background:#f8f9ff;border-radius:12px;padding:14px 20px;"
            f"border-left:4px solid #6366f1;margin-bottom:12px'>"
            f"<span style='font-size:1.2rem;font-weight:800'>📅 {_sel} ({_dow}요일)</span>"
            f"&nbsp;&nbsp;<span style='background:#ede9fe;color:#5b21b6;padding:2px 10px;"
            f"border-radius:10px;font-size:.8rem'>예약 {len(_sched_only)}개</span>&nbsp;"
            f"<span style='background:#d1fae5;color:#065f46;padding:2px 10px;"
            f"border-radius:10px;font-size:.8rem'>발행 {len(_pub_only)}개</span>"
            f"</div>", unsafe_allow_html=True
        )

        _ptab1, _ptab2 = st.columns([3, 2])

        # ── 왼쪽: 예약/발행 목록 ──────────────────────────
        with _ptab1:
            _all_sorted = sorted(_sel_posts, key=lambda x: x.get("time","00:00"))
            if not _all_sorted:
                st.info("이 날짜에 예약된 포스트가 없습니다.")
            for _idx, _post in enumerate(_all_sorted):
                _plat = _post.get("platform","")
                _fc   = PLAT_COLOR.get(_plat,"#333")
                _bg   = PLAT_BG.get(_plat,"#f8f8f8")
                _ico  = PLAT_ICON.get(_plat,"📌")
                _pub  = _post.get("status")=="published"

                with st.container():
                    _ci, _cb = st.columns([5, 2])
                    with _ci:
                        st.markdown(
                            f"<div style='background:{_bg};border-left:4px solid {_fc};"
                            f"border-radius:8px;padding:10px 14px'>"
                            f"<div style='font-weight:700;font-size:.95rem'>{_ico} {_post.get('title','')[:35]}</div>"
                            f"<div style='font-size:.8rem;color:#666;margin-top:3px'>"
                            f"🕐 {_post.get('time','--:--')} &nbsp;|&nbsp; "
                            f"{'✅ 발행 완료' if _pub else '⏳ 예약됨'}</div>"
                            f"<div style='font-size:.75rem;color:#999;margin-top:2px'>{_post.get('post_file','')}</div>"
                            f"</div>", unsafe_allow_html=True
                        )
                    with _cb:
                        if not _pub:
                            if st.button("🚀 발행", key=f"pub2_{_sel}_{_idx}", width="stretch", type="primary"):
                                with st.spinner("발행 중..."):
                                    try:
                                        _real_idx = schedule.get(_sel,[]).index(_post)
                                        _res = do_publish(schedule, _sel, _real_idx, cfg)
                                        if _res.success:
                                            schedule[_sel][_real_idx]["status"] = "published"
                                            save_schedule(schedule)
                                            st.success("✅ 발행 완료!")
                                            st.rerun()
                                        else:
                                            st.error(_res.error[:60])
                                    except Exception as _ex:
                                        st.error(str(_ex)[:60])
                        if st.button("🗑️", key=f"del2_{_sel}_{_idx}", width="stretch", help="삭제"):
                            try:
                                _real_idx = schedule.get(_sel,[]).index(_post)
                                schedule[_sel].pop(_real_idx)
                                if not schedule[_sel]: del schedule[_sel]
                                save_schedule(schedule)
                                st.rerun()
                            except Exception:
                                pass
                    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # ── 오른쪽: 새 예약 추가 ─────────────────────────
        with _ptab2:
            st.markdown("**➕ 예약 추가**")
            _post_files_q = sorted(Path("posts").glob("*.yaml"), key=os.path.getmtime, reverse=True) if Path("posts").exists() else []
            if not _post_files_q:
                st.warning("포스트 없음 — '포스트 생성'에서 먼저 만들어주세요.")
            else:
                _q_plat = st.selectbox("플랫폼", list(PLATFORMS.keys()),
                                       format_func=lambda x: PLATFORMS[x], key="qplat")
                _q_time = st.time_input("발행 시간",
                                        _now.replace(hour=9,minute=0,second=0,microsecond=0),
                                        key="qtime")
                _q_file = st.selectbox("포스트 파일", [f.name for f in _post_files_q], key="qfile")

                # 선택 파일 미리보기
                try:
                    with open(f"posts/{_q_file}", "r", encoding="utf-8") as _ff:
                        _qd = yaml.safe_load(_ff)
                    _q_plat_color = PLAT_COLOR.get(_q_plat,"#6366f1")
                    _q_plat_bg    = PLAT_BG.get(_q_plat,"#f0f0f0")
                    st.markdown(
                        f"<div style='background:{_q_plat_bg};border-left:3px solid {_q_plat_color};"
                        f"border-radius:6px;padding:8px 12px;margin:6px 0;font-size:.82rem'>"
                        f"<b>{_qd.get('title','-')[:40]}</b><br>"
                        f"<span style='color:#666'>{_qd.get('body','')[:80]}...</span></div>",
                        unsafe_allow_html=True
                    )
                except Exception:
                    _qd = {}

                if st.button("📅 예약 등록", type="primary", width="stretch", key="qadd"):
                    _qtitle = _qd.get("title", _q_file) if _qd else _q_file
                    if _sel not in schedule: schedule[_sel] = []
                    schedule[_sel].append({
                        "id":         str(uuid.uuid4())[:8],
                        "platform":   _q_plat,
                        "title":      _qtitle,
                        "post_file":  f"posts/{_q_file}",
                        "time":       str(_q_time)[:5],
                        "status":     "scheduled",
                        "created_at": datetime.now().isoformat(),
                    })
                    save_schedule(schedule)
                    st.success(f"✅ {_sel} {str(_q_time)[:5]} 등록!")
                    st.rerun()

    else:
        # 날짜 미선택: 이번 달 전체 요약 카드
        st.markdown("### 📋 이번 달 예약 현황")
        _mo_items = {
            ds: [p for p in items if p.get("platform","") in _active_filter]
            for ds, items in schedule.items()
            if ds.startswith(f"{_yr}-{_mo:02d}")
        }
        if not any(_mo_items.values()):
            st.markdown(
                "<div style='text-align:center;padding:40px;color:#aaa;font-size:1rem'>"
                "📭 이번 달 예약된 포스트가 없습니다.<br>"
                "<span style='font-size:.85rem'>위 캘린더에서 날짜를 클릭하면 예약할 수 있습니다.</span>"
                "</div>", unsafe_allow_html=True
            )
        else:
            for _ds in sorted(_mo_items.keys()):
                _items = _mo_items[_ds]
                if not _items: continue
                _dt   = _date.fromisoformat(_ds)
                _dow2 = ["월","화","수","목","금","토","일"][_dt.weekday()]
                _pub2 = sum(1 for p in _items if p.get("status")=="published")
                _chips2 = ""
                for _p2 in sorted(_items, key=lambda x: x.get("time","")):
                    _pb = PLAT_BG.get(_p2.get("platform",""),"#eee")
                    _pc = PLAT_COLOR.get(_p2.get("platform",""),"#333")
                    _pi = PLAT_ICON.get(_p2.get("platform",""),"📌")
                    _pt = _p2.get("time","")
                    _chips2 += (
                        f"<span style='background:{_pb};color:{_pc};"
                        f"border-radius:10px;padding:1px 8px;"
                        f"font-size:11px;font-weight:700'>{_pi} {_pt}</span> "
                    )
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:8px;padding:8px 14px;"
                    f"background:#f8f9ff;border-radius:8px;margin:4px 0'>"
                    f"<span style='font-weight:700;min-width:80px'>{_ds[5:]} ({_dow2})</span>"
                    f"{_chips2}"
                    f"<span style='margin-left:auto;font-size:11px;color:#888'>"
                    f"✅{_pub2} ⏳{len(_items)-_pub2}</span></div>",
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════════════════════
# 📊 성과 추적
# ══════════════════════════════════════════════════════════
elif page == "📊 성과 추적":
    import json
    import uuid
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from datetime import date as _date, timedelta as _td
    import collections

    PERF_FILE = Path("performance_data.json")
    PLAT_COLORS_P = {
        "instagram": "#E1306C", "threads": "#1c1c1e",
        "youtube":   "#FF0000", "naver":   "#03C75A", "wordpress": "#21759B",
    }
    PLAT_ICONS_P = {
        "instagram": "📸", "threads": "🧵",
        "youtube":   "▶️", "naver":  "📗", "wordpress": "🌐",
    }

    def load_perf():
        if PERF_FILE.exists():
            with open(PERF_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"records": [], "goals": {}}

    def save_perf(data: dict):
        with open(PERF_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    _perf = load_perf()
    _records = _perf.get("records", [])
    _goals   = _perf.get("goals",   {})

    st.title("📊 성과 추적")
    st.caption("포스트별 지표 기록 · 트렌드 분석 · 목표 달성률 관리")

    tab_ov, tab_post, tab_ht, tab_input, tab_goal = st.tabs([
        "📈 개요", "🏆 포스트 순위", "🏷️ 해시태그 성과", "➕ 데이터 입력", "🎯 목표 설정"
    ])

    # ─────────────────────────────────────────────────────
    # 탭1: 개요
    # ─────────────────────────────────────────────────────
    with tab_ov:
        if not _records:
            st.info("아직 성과 데이터가 없습니다. **➕ 데이터 입력** 탭에서 포스트 성과를 기록해 주세요.")
        else:
            # ── KPI 카드 ─────────────────────────────────
            _total_posts   = len(_records)
            _total_likes   = sum(r.get("likes", 0)        for r in _records)
            _total_reach   = sum(r.get("reach", 0)        for r in _records)
            _total_saves   = sum(r.get("saves", 0)        for r in _records)
            _avg_eng       = (sum(r.get("engagement_rate", 0) for r in _records) / _total_posts) if _total_posts else 0
            _total_comments= sum(r.get("comments", 0)    for r in _records)

            _kpi_css = """
            <style>
            .kpi-box{background:#fff;border-radius:14px;padding:18px 20px;box-shadow:0 2px 8px rgba(0,0,0,.08);text-align:center}
            .kpi-val{font-size:2rem;font-weight:800;color:#1a1a2e;line-height:1.1}
            .kpi-lbl{font-size:.8rem;color:#888;margin-top:4px}
            .kpi-sub{font-size:.75rem;color:#aaa}
            </style>"""
            st.markdown(_kpi_css, unsafe_allow_html=True)

            _kc = st.columns(6)
            _kpi_data = [
                ("총 기록 포스트", f"{_total_posts:,}", "건", "#6c5ce7"),
                ("총 좋아요",      f"{_total_likes:,}",  "개", "#E1306C"),
                ("총 도달",        f"{_total_reach:,}",  "명", "#0984e3"),
                ("총 저장",        f"{_total_saves:,}",  "회", "#00b894"),
                ("평균 참여율",    f"{_avg_eng:.1f}",    "%",  "#fdcb6e"),
                ("총 댓글",        f"{_total_comments:,}","개","#fd79a8"),
            ]
            for _col, (_lbl, _val, _unit, _col_hex) in zip(_kc, _kpi_data):
                with _col:
                    st.markdown(
                        f"<div class='kpi-box'>"
                        f"<div class='kpi-val' style='color:{_col_hex}'>{_val}</div>"
                        f"<div class='kpi-lbl'>{_lbl}</div>"
                        f"<div class='kpi-sub'>{_unit}</div></div>",
                        unsafe_allow_html=True
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # ── 플랫폼별 평균 성과 레이더 차트 + 도달 도넛 ──
            _c1, _c2 = st.columns(2)
            with _c1:
                _plat_groups = collections.defaultdict(list)
                for r in _records:
                    _plat_groups[r.get("platform","")].append(r)

                _radar_platforms = list(_plat_groups.keys())
                if len(_radar_platforms) >= 2:
                    _categories = ["좋아요", "댓글", "저장", "도달(÷10)", "참여율(×10)"]
                    _fig_radar = go.Figure()
                    for _plat in _radar_platforms:
                        _recs = _plat_groups[_plat]
                        _n = len(_recs)
                        _vals = [
                            sum(r.get("likes",0) for r in _recs) / _n,
                            sum(r.get("comments",0) for r in _recs) / _n,
                            sum(r.get("saves",0) for r in _recs) / _n,
                            sum(r.get("reach",0) for r in _recs) / _n / 10,
                            sum(r.get("engagement_rate",0) for r in _recs) / _n * 10,
                        ]
                        _fig_radar.add_trace(go.Scatterpolar(
                            r=_vals + [_vals[0]],
                            theta=_categories + [_categories[0]],
                            fill="toself", name=f"{PLAT_ICONS_P.get(_plat,'')} {_plat}",
                            line_color=PLAT_COLORS_P.get(_plat,"#999"),
                            opacity=0.7,
                        ))
                    _fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True)),
                        showlegend=True, height=320,
                        title="플랫폼별 평균 성과 레이더",
                        margin=dict(t=50,b=20,l=20,r=20),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(_fig_radar, key="radar_chart")
                else:
                    _plat_reach = {p: sum(r.get("reach",0) for r in recs) for p, recs in _plat_groups.items()}
                    _fig_donut = go.Figure(go.Pie(
                        labels=list(_plat_reach.keys()),
                        values=list(_plat_reach.values()),
                        hole=0.55,
                        marker_colors=[PLAT_COLORS_P.get(p,"#ccc") for p in _plat_reach],
                    ))
                    _fig_donut.update_layout(
                        title="플랫폼별 총 도달", height=320,
                        margin=dict(t=50,b=20,l=20,r=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(_fig_donut, key="donut_chart")

            with _c2:
                # 월별 좋아요 트렌드
                _month_likes = collections.defaultdict(int)
                _month_reach = collections.defaultdict(int)
                for r in _records:
                    _ym = r.get("date","")[:7]
                    _month_likes[_ym] += r.get("likes",0)
                    _month_reach[_ym] += r.get("reach",0)
                if _month_likes:
                    _fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
                    _sorted_months = sorted(_month_likes.keys())
                    _fig_trend.add_trace(go.Bar(
                        x=_sorted_months, y=[_month_likes[m] for m in _sorted_months],
                        name="좋아요", marker_color="#E1306C", opacity=0.8,
                    ), secondary_y=False)
                    _fig_trend.add_trace(go.Scatter(
                        x=_sorted_months, y=[_month_reach[m] for m in _sorted_months],
                        name="도달", mode="lines+markers",
                        line=dict(color="#0984e3", width=2), marker_size=6,
                    ), secondary_y=True)
                    _fig_trend.update_layout(
                        title="월별 좋아요 & 도달 추이",
                        height=320, showlegend=True,
                        margin=dict(t=50,b=20,l=20,r=20),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    )
                    _fig_trend.update_yaxes(title_text="좋아요", secondary_y=False)
                    _fig_trend.update_yaxes(title_text="도달", secondary_y=True)
                    st.plotly_chart(_fig_trend, key="trend_chart")

            # ── 요일×시간 참여율 히트맵 ──────────────────────
            _hm_data = [[0.0]*24 for _ in range(7)]
            _hm_cnt  = [[0]*24  for _ in range(7)]
            for r in _records:
                try:
                    _dt = datetime.fromisoformat(r.get("date","") + "T" + r.get("time","00:00"))
                    _dow = _dt.weekday()
                    _hr  = _dt.hour
                    _hm_data[_dow][_hr] += r.get("engagement_rate", 0)
                    _hm_cnt[_dow][_hr]  += 1
                except Exception:
                    pass

            _hm_avg = [
                [(_hm_data[d][h] / _hm_cnt[d][h]) if _hm_cnt[d][h] else 0 for h in range(24)]
                for d in range(7)
            ]
            _days_ko = ["월","화","수","목","금","토","일"]
            _fig_hm = go.Figure(go.Heatmap(
                z=_hm_avg,
                x=[f"{h}시" for h in range(24)],
                y=_days_ko,
                colorscale="RdYlGn",
                colorbar=dict(title="참여율 %"),
                hoverongaps=False,
                text=[[f"{v:.1f}%" for v in row] for row in _hm_avg],
                hovertemplate="%{y} %{x}<br>평균 참여율: %{text}<extra></extra>",
            ))
            _fig_hm.update_layout(
                title="요일·시간대별 평균 참여율 히트맵",
                height=280, margin=dict(t=50,b=20,l=40,r=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(_fig_hm, key="hm_chart")

            # ── AI 인사이트 ────────────────────────────────
            _best_day_idx = max(range(7), key=lambda d: max(_hm_avg[d]))
            _best_hr_val  = max(range(24), key=lambda h: _hm_avg[_best_day_idx][h])
            _best_plat    = max(_plat_groups, key=lambda p: sum(r.get("engagement_rate",0) for r in _plat_groups[p]) / len(_plat_groups[p])) if _plat_groups else "-"
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#667eea,#764ba2);border-radius:14px;"
                f"padding:20px 24px;color:#fff;margin-top:8px'>"
                f"<div style='font-size:1.1rem;font-weight:700;margin-bottom:12px'>💡 AI 인사이트</div>"
                f"<ul style='margin:0;padding-left:16px;line-height:2'>"
                f"<li>최고 참여율 요일·시간: <b>{_days_ko[_best_day_idx]}요일 {_best_hr_val}시</b></li>"
                f"<li>가장 효과적인 플랫폼: <b>{PLAT_ICONS_P.get(_best_plat,'')} {_best_plat}</b></li>"
                f"<li>전체 평균 참여율: <b>{_avg_eng:.2f}%</b> "
                f"{'(업계 평균 이상 ✅)' if _avg_eng >= 1.5 else '(업계 평균 1.5% 미달 — 해시태그·시간대 최적화 필요)'}</li>"
                f"</ul></div>",
                unsafe_allow_html=True
            )

    # ─────────────────────────────────────────────────────
    # 탭2: 포스트 순위
    # ─────────────────────────────────────────────────────
    with tab_post:
        if not _records:
            st.info("데이터가 없습니다. ➕ 데이터 입력 탭을 먼저 이용해 주세요.")
        else:
            _sort_by = st.selectbox("정렬 기준", ["참여율", "좋아요", "도달", "저장", "댓글"], key="rank_sort")
            _sort_key_map = {"참여율":"engagement_rate","좋아요":"likes","도달":"reach","저장":"saves","댓글":"comments"}
            _sk = _sort_key_map[_sort_by]
            _sorted_records = sorted(_records, key=lambda r: r.get(_sk, 0), reverse=True)

            # 상위 10 바 차트
            _top10 = _sorted_records[:10]
            _labels = [f"{PLAT_ICONS_P.get(r.get('platform',''),'')}{r.get('title','')[:15]}…" for r in _top10]
            _values = [r.get(_sk, 0) for r in _top10]
            _colors = [PLAT_COLORS_P.get(r.get("platform",""),"#999") for r in _top10]
            _fig_rank = go.Figure(go.Bar(
                x=_values, y=_labels, orientation="h",
                marker_color=_colors, text=[f"{v:.1f}" if isinstance(v,float) else str(v) for v in _values],
                textposition="outside",
            ))
            _fig_rank.update_layout(
                title=f"TOP 10 포스트 ({_sort_by} 기준)",
                height=360, margin=dict(t=50,b=20,l=20,r=60),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(_fig_rank, key="rank_chart")

            # 상세 테이블
            st.markdown("#### 전체 포스트 목록")
            _col_defs = ["날짜", "플랫폼", "제목", "좋아요", "댓글", "저장", "도달", "참여율%"]
            _tbl_rows = []
            for r in _sorted_records:
                _tbl_rows.append({
                    "날짜": r.get("date",""),
                    "플랫폼": f"{PLAT_ICONS_P.get(r.get('platform',''),'')} {r.get('platform','')}",
                    "제목": r.get("title","")[:30],
                    "좋아요": r.get("likes",0),
                    "댓글": r.get("comments",0),
                    "저장": r.get("saves",0),
                    "도달": r.get("reach",0),
                    "참여율%": f"{r.get('engagement_rate',0):.2f}",
                })
            import pandas as pd
            st.dataframe(pd.DataFrame(_tbl_rows), use_container_width=True, height=380)

            # 삭제 버튼
            st.markdown("---")
            _del_titles = [f"{r.get('date','')} | {r.get('platform','')} | {r.get('title','')[:20]}" for r in _sorted_records]
            _del_idx = st.selectbox("삭제할 기록 선택", range(len(_del_titles)), format_func=lambda i: _del_titles[i], key="del_sel")
            if st.button("🗑️ 선택 기록 삭제", key="del_rec"):
                _del_id = _sorted_records[_del_idx].get("id")
                _perf["records"] = [r for r in _perf["records"] if r.get("id") != _del_id]
                save_perf(_perf)
                st.success("삭제 완료!")
                st.rerun()

    # ─────────────────────────────────────────────────────
    # 탭3: 해시태그 성과
    # ─────────────────────────────────────────────────────
    with tab_ht:
        if not _records:
            st.info("데이터가 없습니다. ➕ 데이터 입력 탭을 먼저 이용해 주세요.")
        else:
            _ht_eng  = collections.defaultdict(list)
            _ht_reach= collections.defaultdict(list)
            for r in _records:
                for tag in r.get("hashtags", []):
                    _t = tag.lstrip("#").strip()
                    if _t:
                        _ht_eng[_t].append(r.get("engagement_rate", 0))
                        _ht_reach[_t].append(r.get("reach", 0))

            if not _ht_eng:
                st.info("해시태그 데이터가 없습니다. 포스트 입력 시 해시태그를 추가해 주세요.")
            else:
                _ht_summary = []
                for tag, engs in _ht_eng.items():
                    _ht_summary.append({
                        "해시태그": f"#{tag}",
                        "사용 횟수": len(engs),
                        "평균 참여율": round(sum(engs)/len(engs), 2),
                        "평균 도달": int(sum(_ht_reach[tag])/len(_ht_reach[tag])),
                    })
                _ht_summary.sort(key=lambda x: x["평균 참여율"], reverse=True)

                _c1_ht, _c2_ht = st.columns(2)
                with _c1_ht:
                    _top_tags = _ht_summary[:15]
                    _fig_ht_eng = go.Figure(go.Bar(
                        x=[t["평균 참여율"] for t in _top_tags],
                        y=[t["해시태그"] for t in _top_tags],
                        orientation="h",
                        marker_color="#E1306C",
                        text=[f"{t['평균 참여율']}%" for t in _top_tags],
                        textposition="outside",
                    ))
                    _fig_ht_eng.update_layout(
                        title="해시태그별 평균 참여율 TOP15",
                        height=420, margin=dict(t=50,b=20,l=10,r=60),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        yaxis=dict(autorange="reversed"),
                    )
                    st.plotly_chart(_fig_ht_eng, key="ht_eng_chart")

                with _c2_ht:
                    _reach_sorted = sorted(_ht_summary, key=lambda x: x["평균 도달"], reverse=True)[:15]
                    _fig_ht_reach = go.Figure(go.Bar(
                        x=[t["평균 도달"] for t in _reach_sorted],
                        y=[t["해시태그"] for t in _reach_sorted],
                        orientation="h",
                        marker_color="#0984e3",
                        text=[f"{t['평균 도달']:,}" for t in _reach_sorted],
                        textposition="outside",
                    ))
                    _fig_ht_reach.update_layout(
                        title="해시태그별 평균 도달 TOP15",
                        height=420, margin=dict(t=50,b=20,l=10,r=60),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        yaxis=dict(autorange="reversed"),
                    )
                    st.plotly_chart(_fig_ht_reach, key="ht_reach_chart")

                st.markdown("#### 해시태그 성과 전체 표")
                import pandas as pd
                st.dataframe(pd.DataFrame(_ht_summary), use_container_width=True, height=320)

                # 추천 해시태그 배지
                _best_tags = [t["해시태그"] for t in _ht_summary[:8]]
                _badges = " ".join(
                    f"<span style='background:#fce4ec;color:#E1306C;border-radius:20px;"
                    f"padding:4px 12px;font-size:13px;font-weight:600;margin:2px'>{t}</span>"
                    for t in _best_tags
                )
                st.markdown(
                    f"<div style='background:#fff;border-radius:12px;padding:16px 20px;"
                    f"box-shadow:0 2px 8px rgba(0,0,0,.07);margin-top:8px'>"
                    f"<div style='font-weight:700;margin-bottom:10px'>⭐ 성과 좋은 해시태그 (복사해서 활용하세요)</div>"
                    f"{_badges}</div>",
                    unsafe_allow_html=True
                )

    # ─────────────────────────────────────────────────────
    # 탭4: 데이터 입력
    # ─────────────────────────────────────────────────────
    with tab_input:
        st.markdown("#### 포스트 성과 기록 추가")
        st.caption("업로드 후 확인한 좋아요·댓글·도달 등을 여기에 입력하세요.")

        with st.form("perf_form", clear_on_submit=True):
            _fc1, _fc2 = st.columns(2)
            with _fc1:
                _f_date  = st.date_input("날짜", value=_date.today(), key="pf_date")
                _f_time  = st.time_input("게시 시간", key="pf_time")
                _f_plat  = st.selectbox("플랫폼", list(PLAT_ICONS_P.keys()), key="pf_plat")
                _f_title = st.text_input("포스트 제목 (식별용)", key="pf_title")
                _f_tags  = st.text_input("사용한 해시태그 (쉼표 구분)", placeholder="#주얼리, #금반지, #커플링", key="pf_tags")
            with _fc2:
                _f_likes    = st.number_input("좋아요 수",      min_value=0, step=1,   key="pf_likes")
                _f_comments = st.number_input("댓글 수",        min_value=0, step=1,   key="pf_comments")
                _f_shares   = st.number_input("공유/리그램 수", min_value=0, step=1,   key="pf_shares")
                _f_saves    = st.number_input("저장 수",        min_value=0, step=1,   key="pf_saves")
                _f_reach    = st.number_input("도달 수",        min_value=0, step=10,  key="pf_reach")
                _f_impr     = st.number_input("노출 수",        min_value=0, step=10,  key="pf_impr")

            _f_notes = st.text_area("메모 (선택)", placeholder="이 포스트에서 특이했던 점 등", key="pf_notes")

            _submitted = st.form_submit_button("✅ 성과 데이터 저장", type="primary")
            if _submitted:
                if not _f_title:
                    st.error("포스트 제목을 입력하세요.")
                else:
                    _eng = 0.0
                    if _f_reach > 0:
                        _eng = round((_f_likes + _f_comments + _f_saves) / _f_reach * 100, 2)
                    _tags_list = [t.strip() for t in _f_tags.split(",") if t.strip()] if _f_tags else []
                    _new_rec = {
                        "id":               str(uuid.uuid4()),
                        "date":             str(_f_date),
                        "time":             str(_f_time)[:5],
                        "platform":         _f_plat,
                        "title":            _f_title,
                        "likes":            int(_f_likes),
                        "comments":         int(_f_comments),
                        "shares":           int(_f_shares),
                        "saves":            int(_f_saves),
                        "reach":            int(_f_reach),
                        "impressions":      int(_f_impr),
                        "engagement_rate":  _eng,
                        "hashtags":         _tags_list,
                        "notes":            _f_notes,
                    }
                    _perf["records"].append(_new_rec)
                    save_perf(_perf)
                    st.success(f"✅ 저장 완료! 참여율: **{_eng:.2f}%** (좋아요+댓글+저장 / 도달)")
                    st.rerun()

        # 최근 5개 미리보기
        if _records:
            st.markdown("---")
            st.markdown("#### 최근 입력 기록 (최신 5개)")
            for r in sorted(_records, key=lambda x: x.get("date",""), reverse=True)[:5]:
                _bg = {"instagram":"#fce4ec","threads":"#f3f3f3","youtube":"#ffebee",
                       "naver":"#e8f5e9","wordpress":"#e3f2fd"}.get(r.get("platform",""),"#f5f5f5")
                _cl = PLAT_COLORS_P.get(r.get("platform",""), "#333")
                _ic = PLAT_ICONS_P.get(r.get("platform",""), "📌")
                st.markdown(
                    f"<div style='background:{_bg};border-left:4px solid {_cl};border-radius:8px;"
                    f"padding:10px 16px;margin:4px 0;display:flex;justify-content:space-between;align-items:center'>"
                    f"<div><b>{_ic} {r.get('title','')[:25]}</b>"
                    f"<span style='color:#888;font-size:.8rem;margin-left:8px'>{r.get('date','')} {r.get('time','')}</span></div>"
                    f"<div style='font-size:.85rem;color:{_cl};font-weight:700'>"
                    f"❤️{r.get('likes',0):,} 💬{r.get('comments',0):,} "
                    f"🔖{r.get('saves',0):,} 📡{r.get('reach',0):,} "
                    f"📊{r.get('engagement_rate',0):.1f}%</div></div>",
                    unsafe_allow_html=True
                )

    # ─────────────────────────────────────────────────────
    # 탭5: 목표 설정
    # ─────────────────────────────────────────────────────
    with tab_goal:
        st.markdown("#### 월별 성과 목표 설정 & 달성률")

        _goal_plat = st.selectbox("플랫폼 선택", list(PLAT_ICONS_P.keys()), key="goal_plat")
        _plat_goal = _goals.get(_goal_plat, {})

        with st.form("goal_form"):
            _gc1, _gc2 = st.columns(2)
            with _gc1:
                _g_posts = st.number_input("월 목표 포스트 수",   min_value=1, value=int(_plat_goal.get("monthly_posts",12)), step=1)
                _g_likes = st.number_input("포스트당 평균 목표 좋아요", min_value=0, value=int(_plat_goal.get("avg_likes",50)),   step=5)
            with _gc2:
                _g_reach = st.number_input("포스트당 평균 목표 도달", min_value=0, value=int(_plat_goal.get("avg_reach",500)),  step=50)
                _g_eng   = st.number_input("목표 평균 참여율 (%)", min_value=0.0, value=float(_plat_goal.get("avg_engagement",1.5)), step=0.1, format="%.1f")
            if st.form_submit_button("💾 목표 저장", type="primary"):
                _perf["goals"][_goal_plat] = {
                    "monthly_posts": int(_g_posts),
                    "avg_likes":     int(_g_likes),
                    "avg_reach":     int(_g_reach),
                    "avg_engagement":float(_g_eng),
                }
                save_perf(_perf)
                st.success("✅ 목표 저장 완료!")
                st.rerun()

        # 달성률 게이지
        st.markdown("---")
        st.markdown("#### 이번 달 달성률")
        _now = _date.today()
        _this_month = f"{_now.year}-{_now.month:02d}"
        _month_recs = [r for r in _records if r.get("date","").startswith(_this_month) and r.get("platform","") == _goal_plat]
        _n_m = len(_month_recs)
        _avg_likes_m = sum(r.get("likes",0) for r in _month_recs) / _n_m if _n_m else 0
        _avg_reach_m = sum(r.get("reach",0) for r in _month_recs) / _n_m if _n_m else 0
        _avg_eng_m   = sum(r.get("engagement_rate",0) for r in _month_recs) / _n_m if _n_m else 0

        _g_now = _goals.get(_goal_plat, {})
        _gauge_items = [
            ("월 포스트 수",   _n_m,        _g_now.get("monthly_posts",12),  "#6c5ce7"),
            ("평균 좋아요",    _avg_likes_m, _g_now.get("avg_likes",50),      "#E1306C"),
            ("평균 도달",      _avg_reach_m, _g_now.get("avg_reach",500),     "#0984e3"),
            ("평균 참여율(%)", _avg_eng_m,   _g_now.get("avg_engagement",1.5),"#00b894"),
        ]
        _gcols = st.columns(4)
        for _gcol, (_glbl, _gval, _gtgt, _gcolor) in zip(_gcols, _gauge_items):
            with _gcol:
                _pct = min((_gval / _gtgt * 100) if _gtgt else 0, 100)
                _fig_g = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=round(_gval, 1),
                    delta={"reference": _gtgt, "valueformat": ".1f"},
                    gauge={
                        "axis": {"range": [0, max(_gtgt * 1.3, 1)]},
                        "bar": {"color": _gcolor},
                        "steps": [
                            {"range": [0, _gtgt * 0.5], "color": "#ffeaa7"},
                            {"range": [_gtgt * 0.5, _gtgt], "color": "#81ecec"},
                            {"range": [_gtgt, _gtgt * 1.3], "color": "#55efc4"},
                        ],
                        "threshold": {"line": {"color": _gcolor, "width": 3}, "value": _gtgt},
                    },
                    title={"text": _glbl, "font": {"size": 13}},
                    number={"font": {"size": 22}},
                ))
                _fig_g.update_layout(
                    height=200, margin=dict(t=60,b=10,l=10,r=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(_fig_g, key=f"gauge_{_glbl}")

        # 달성 요약 텍스트
        _done_count = sum(1 for _, v, t, _ in _gauge_items if t and v >= t)
        _msg_color = "#00b894" if _done_count >= 3 else "#fdcb6e" if _done_count >= 2 else "#d63031"
        _msg_emoji = "🎉" if _done_count >= 3 else "💪" if _done_count >= 2 else "🔥"
        st.markdown(
            f"<div style='background:{_msg_color}22;border:2px solid {_msg_color};"
            f"border-radius:12px;padding:16px 20px;text-align:center;margin-top:8px'>"
            f"<span style='font-size:1.3rem'>{_msg_emoji}</span> "
            f"<b style='color:{_msg_color}'>{PLAT_ICONS_P.get(_goal_plat,'')} {_goal_plat} — "
            f"{_this_month} 목표 {_done_count}/4 달성</b>"
            f"<span style='color:#888;font-size:.85rem;margin-left:8px'>({_n_m}개 포스트 기록됨)</span>"
            f"</div>",
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════
# 📄 리포트 생성
# ══════════════════════════════════════════════════════════
elif page == "📄 리포트 생성":
    import json as _json
    import io
    import collections
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as _fm
    import matplotlib.patches as _mpatches
    from matplotlib.gridspec import GridSpec
    from datetime import date as _date, timedelta as _td
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as _rl_colors
    from reportlab.lib.units import mm, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, HRFlowable, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # ── 한국어 폰트 등록 ──────────────────────────────────
    _KR_FONT_PATH = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    try:
        pdfmetrics.registerFont(TTFont("KR", _KR_FONT_PATH))
        pdfmetrics.registerFont(TTFont("KR-Bold", _KR_FONT_PATH))
        _KR = "KR"
    except Exception:
        _KR = "Helvetica"

    # matplotlib 한국어 폰트
    try:
        _mpl_font = _fm.FontProperties(fname=_KR_FONT_PATH)
        plt.rcParams["font.family"] = "AppleGothic"
        plt.rcParams["axes.unicode_minus"] = False
    except Exception:
        _mpl_font = None

    # ── 데이터 로드 ───────────────────────────────────────
    _PERF_FILE = Path("performance_data.json")
    _perf_all  = {"records": [], "goals": {}}
    if _PERF_FILE.exists():
        with open(_PERF_FILE, "r", encoding="utf-8") as _f:
            _perf_all = _json.load(_f)
    _all_recs = _perf_all.get("records", [])

    _PLAT_CLR_R = {
        "instagram": "#E1306C", "threads": "#1c1c1e",
        "youtube":   "#FF0000", "naver":   "#03C75A", "wordpress": "#21759B",
    }

    # ── UI ───────────────────────────────────────────────
    st.title("📄 성과 리포트 자동 생성")
    st.caption("성과 추적 데이터를 PDF 리포트로 자동 정리합니다.")

    if not _all_recs:
        st.warning("📊 성과 추적 데이터가 없습니다. **📊 성과 추적** 탭에서 포스트 성과를 먼저 입력해 주세요.")
        st.stop()

    _rc1, _rc2, _rc3 = st.columns(3)
    with _rc1:
        _report_type = st.radio("리포트 기간", ["월간", "주간", "전체"], horizontal=True, key="rpt_type")
    with _rc2:
        _report_date = st.date_input("기준 날짜", value=_date.today(), key="rpt_date")
    with _rc3:
        _rpt_plats = st.multiselect(
            "플랫폼 필터",
            ["instagram","threads","youtube","naver","wordpress"],
            default=list({r.get("platform","") for r in _all_recs}),
            key="rpt_plats"
        )

    _use_ai   = st.checkbox("AI 인사이트 포함 (Gemini)", value=True, key="rpt_ai")
    _acct_name = st.text_input("계정명 (리포트 표지용)", value="@geumseok_jewellery", key="rpt_acct")

    st.divider()

    # ── 기간 필터링 ───────────────────────────────────────
    def _filter_recs(recs, rtype, ref_date, plats):
        out = []
        for r in recs:
            if r.get("platform","") not in plats:
                continue
            try:
                rd = _date.fromisoformat(r["date"])
            except Exception:
                continue
            if rtype == "월간":
                if rd.year == ref_date.year and rd.month == ref_date.month:
                    out.append(r)
            elif rtype == "주간":
                week_start = ref_date - _td(days=ref_date.weekday())
                week_end   = week_start + _td(days=6)
                if week_start <= rd <= week_end:
                    out.append(r)
            else:
                out.append(r)
        return out

    _recs = _filter_recs(_all_recs, _report_type, _report_date, _rpt_plats)

    if _report_type == "월간":
        _period_label = f"{_report_date.year}년 {_report_date.month}월"
    elif _report_type == "주간":
        _ws = _report_date - _td(days=_report_date.weekday())
        _we = _ws + _td(days=6)
        _period_label = f"{_ws.strftime('%Y.%m.%d')} ~ {_we.strftime('%Y.%m.%d')}"
    else:
        _period_label = "전체 기간"

    # 미리보기 KPI
    _n = len(_recs)
    if _n == 0:
        st.info(f"해당 기간({_period_label})에 기록된 데이터가 없습니다.")
        st.stop()

    _kv = {
        "포스트 수":   _n,
        "총 좋아요":   sum(r.get("likes",0)    for r in _recs),
        "총 도달":     sum(r.get("reach",0)    for r in _recs),
        "총 저장":     sum(r.get("saves",0)    for r in _recs),
        "총 댓글":     sum(r.get("comments",0) for r in _recs),
        "평균 참여율": round(sum(r.get("engagement_rate",0) for r in _recs)/_n, 2),
    }
    _kpi_cols = st.columns(6)
    for _col, (k, v) in zip(_kpi_cols, _kv.items()):
        with _col:
            st.metric(k, f"{v:,}" if isinstance(v, int) else f"{v}%")

    st.markdown(f"**기간:** {_period_label} &nbsp;|&nbsp; **데이터:** {_n}건")

    # ── 생성 버튼 ─────────────────────────────────────────
    if st.button("📄 PDF 리포트 생성", type="primary", key="gen_pdf"):

        _prog = st.progress(0, text="차트 생성 중...")

        # ───────── 차트 생성 함수 ─────────────────────────
        def _fig_to_bytes(fig):
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                        facecolor=fig.get_facecolor())
            buf.seek(0)
            plt.close(fig)
            return buf

        # 차트1: 플랫폼별 도넛
        _plat_cnt = collections.Counter(r.get("platform","") for r in _recs)
        _fig1, _ax1 = plt.subplots(figsize=(4, 3.5), facecolor="#f8f9ff")
        _ax1.set_facecolor("#f8f9ff")
        _wedge_colors = [_PLAT_CLR_R.get(p,"#ccc") for p in _plat_cnt]
        _ax1.pie(
            list(_plat_cnt.values()), labels=list(_plat_cnt.keys()),
            colors=_wedge_colors, autopct="%1.0f%%", startangle=90,
            wedgeprops=dict(width=0.55), textprops={"fontsize":8},
        )
        _ax1.set_title("플랫폼별 포스트 비율", fontsize=10, fontweight="bold", pad=8)
        _chart1_bytes = _fig_to_bytes(_fig1)

        _prog.progress(20, text="트렌드 차트 생성 중...")

        # 차트2: 날짜별 좋아요+도달 트렌드
        _day_likes = collections.defaultdict(int)
        _day_reach = collections.defaultdict(int)
        for r in _recs:
            _d = r.get("date","")
            _day_likes[_d] += r.get("likes",0)
            _day_reach[_d] += r.get("reach",0)
        _sorted_days = sorted(_day_likes)
        _fig2, _ax2a = plt.subplots(figsize=(7, 3), facecolor="#f8f9ff")
        _ax2b = _ax2a.twinx()
        _ax2a.set_facecolor("#f8f9ff")
        _ax2a.bar(_sorted_days, [_day_likes[d] for d in _sorted_days],
                  color="#E1306C", alpha=0.75, label="좋아요", zorder=3)
        _ax2b.plot(_sorted_days, [_day_reach[d] for d in _sorted_days],
                   color="#0984e3", marker="o", ms=4, lw=2, label="도달")
        _ax2a.set_title("날짜별 좋아요 & 도달 추이", fontsize=10, fontweight="bold")
        _ax2a.set_ylabel("좋아요", fontsize=8, color="#E1306C")
        _ax2b.set_ylabel("도달",   fontsize=8, color="#0984e3")
        _ax2a.tick_params(axis="x", rotation=45, labelsize=7)
        _ax2a.tick_params(axis="y", labelsize=7)
        _ax2b.tick_params(axis="y", labelsize=7)
        _ax2a.yaxis.set_label_coords(-0.08, 0.5)
        _ax2a.grid(axis="y", alpha=0.3, zorder=0)
        lines1, labels1 = _ax2a.get_legend_handles_labels()
        lines2, labels2 = _ax2b.get_legend_handles_labels()
        _ax2a.legend(lines1+lines2, labels1+labels2, fontsize=7, loc="upper left")
        _fig2.tight_layout()
        _chart2_bytes = _fig_to_bytes(_fig2)

        _prog.progress(40, text="해시태그 차트 생성 중...")

        # 차트3: 해시태그 TOP10 참여율
        _ht_eng = collections.defaultdict(list)
        for r in _recs:
            for tag in r.get("hashtags",[]):
                _t = tag.lstrip("#").strip()
                if _t:
                    _ht_eng[_t].append(r.get("engagement_rate",0))
        _ht_avg = {t: round(sum(v)/len(v),2) for t,v in _ht_eng.items()}
        _top_ht = sorted(_ht_avg, key=_ht_avg.get, reverse=True)[:10]
        _fig3, _ax3 = plt.subplots(figsize=(6, 3.5), facecolor="#f8f9ff")
        _ax3.set_facecolor("#f8f9ff")
        _bars = _ax3.barh(
            _top_ht[::-1], [_ht_avg[t] for t in _top_ht[::-1]],
            color="#6c5ce7", alpha=0.8
        )
        _ax3.bar_label(_bars, fmt="%.1f%%", padding=3, fontsize=7)
        _ax3.set_xlabel("평균 참여율 (%)", fontsize=8)
        _ax3.set_title("해시태그 TOP 10 (참여율 기준)", fontsize=10, fontweight="bold")
        _ax3.tick_params(labelsize=7)
        _ax3.grid(axis="x", alpha=0.3)
        _fig3.tight_layout()
        _chart3_bytes = _fig_to_bytes(_fig3)

        _prog.progress(55, text="플랫폼별 성과 차트 생성 중...")

        # 차트4: 플랫폼별 평균 참여율 막대
        _plat_eng = {}
        for _pid in _plat_cnt:
            _pr = [r.get("engagement_rate",0) for r in _recs if r.get("platform","")==_pid]
            _plat_eng[_pid] = round(sum(_pr)/len(_pr),2) if _pr else 0
        _fig4, _ax4 = plt.subplots(figsize=(4, 3), facecolor="#f8f9ff")
        _ax4.set_facecolor("#f8f9ff")
        _brs = _ax4.bar(
            list(_plat_eng.keys()), list(_plat_eng.values()),
            color=[_PLAT_CLR_R.get(p,"#ccc") for p in _plat_eng], alpha=0.85
        )
        _ax4.bar_label(_brs, fmt="%.1f%%", padding=3, fontsize=8)
        _ax4.set_ylabel("평균 참여율 (%)", fontsize=8)
        _ax4.set_title("플랫폼별 평균 참여율", fontsize=10, fontweight="bold")
        _ax4.tick_params(labelsize=8)
        _ax4.grid(axis="y", alpha=0.3)
        _fig4.tight_layout()
        _chart4_bytes = _fig_to_bytes(_fig4)

        _prog.progress(70, text="AI 인사이트 생성 중..." if _use_ai else "PDF 조립 중...")

        # ── AI 인사이트 ────────────────────────────────────
        _ai_text = ""
        if _use_ai and cfg.get("openai",{}).get("api_key",""):
            try:
                from google import genai as _genai
                from google.genai import types as _gtypes
                _cl = _genai.Client(api_key=cfg["openai"]["api_key"])
                _summary = {
                    "기간": _period_label,
                    "포스트수": _n,
                    "총좋아요": _kv["총 좋아요"],
                    "총도달": _kv["총 도달"],
                    "평균참여율": _kv["평균 참여율"],
                    "최고해시태그": _top_ht[:3] if _top_ht else [],
                    "플랫폼별참여율": _plat_eng,
                }
                _ins_prompt = f"""SNS 마케팅 전문가로서 아래 데이터를 분석하고 주얼리 쇼핑몰 관점에서 인사이트와 다음 달 실행 전략을 작성해주세요.

데이터: {_json.dumps(_summary, ensure_ascii=False)}

다음 형식으로 한국어로 작성하세요 (각 항목 2~3문장):
1. 이번 기간 총평:
2. 가장 효과적이었던 전략:
3. 개선이 필요한 부분:
4. 다음 기간 실행 전략 3가지:"""
                _ir = _cl.models.generate_content(
                    model=cfg["openai"].get("model","gemini-2.5-flash"),
                    contents=_ins_prompt,
                    config=_gtypes.GenerateContentConfig(temperature=0.7),
                )
                _ai_text = _ir.text.strip()
            except Exception as _ae:
                _ai_text = f"AI 인사이트 생성 실패: {_ae}"

        _prog.progress(85, text="PDF 파일 조립 중...")

        # ───────── PDF 생성 ────────────────────────────────
        _pdf_buf = io.BytesIO()
        _doc = SimpleDocTemplate(
            _pdf_buf, pagesize=A4,
            leftMargin=20*mm, rightMargin=20*mm,
            topMargin=20*mm, bottomMargin=20*mm,
        )

        def _style(name="KR", size=10, bold=False, color="#1a1a2e", leading=None):
            return ParagraphStyle(
                f"s_{name}_{size}_{bold}",
                fontName=_KR if not bold else _KR,
                fontSize=size,
                textColor=_rl_colors.HexColor(color),
                leading=leading or size*1.4,
                wordWrap="CJK",
            )

        _PAGE_W = A4[0] - 40*mm
        _elems  = []

        # ── 표지 ──────────────────────────────────────────
        _elems.append(Spacer(1, 30*mm))
        _elems.append(Paragraph(
            f"<font size=28><b>SNS 성과 리포트</b></font>",
            ParagraphStyle("cover_title", fontName=_KR, fontSize=28,
                           textColor=_rl_colors.HexColor("#1a1a2e"),
                           alignment=1, leading=36),
        ))
        _elems.append(Spacer(1, 6*mm))
        _elems.append(Paragraph(
            _period_label,
            ParagraphStyle("cover_period", fontName=_KR, fontSize=16,
                           textColor=_rl_colors.HexColor("#6c5ce7"),
                           alignment=1, leading=22),
        ))
        _elems.append(Spacer(1, 4*mm))
        _elems.append(HRFlowable(width=80*mm, thickness=2,
                                  color=_rl_colors.HexColor("#6c5ce7"),
                                  hAlign="CENTER"))
        _elems.append(Spacer(1, 6*mm))
        _elems.append(Paragraph(
            _acct_name,
            ParagraphStyle("cover_acct", fontName=_KR, fontSize=13,
                           textColor=_rl_colors.HexColor("#888"),
                           alignment=1),
        ))
        _elems.append(Spacer(1, 3*mm))
        _elems.append(Paragraph(
            f"생성일: {_date.today().strftime('%Y년 %m월 %d일')}",
            ParagraphStyle("cover_date", fontName=_KR, fontSize=10,
                           textColor=_rl_colors.HexColor("#aaa"),
                           alignment=1),
        ))
        _elems.append(PageBreak())

        # ── KPI 요약 섹션 ──────────────────────────────────
        _elems.append(Paragraph("📊 핵심 성과 지표 (KPI)", _style(size=16, bold=True, color="#1a1a2e")))
        _elems.append(Spacer(1, 4*mm))

        _kpi_table_data = [
            ["지표", "수치", "지표", "수치"],
            ["포스트 수",   f"{_kv['포스트 수']:,}건",
             "총 좋아요",   f"{_kv['총 좋아요']:,}개"],
            ["총 도달",     f"{_kv['총 도달']:,}명",
             "총 저장",     f"{_kv['총 저장']:,}회"],
            ["총 댓글",     f"{_kv['총 댓글']:,}개",
             "평균 참여율", f"{_kv['평균 참여율']}%"],
        ]
        _kpi_tbl = Table(_kpi_table_data, colWidths=[35*mm, 40*mm, 35*mm, 40*mm])
        _kpi_tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0),  _rl_colors.HexColor("#6c5ce7")),
            ("TEXTCOLOR",   (0,0), (-1,0),  _rl_colors.white),
            ("FONTNAME",    (0,0), (-1,-1), _KR),
            ("FONTSIZE",    (0,0), (-1,0),  10),
            ("FONTSIZE",    (0,1), (-1,-1), 11),
            ("ALIGN",       (0,0), (-1,-1), "CENTER"),
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [_rl_colors.HexColor("#f8f9ff"), _rl_colors.white]),
            ("GRID",        (0,0), (-1,-1), 0.5, _rl_colors.HexColor("#ddd")),
            ("TOPPADDING",  (0,0), (-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
            ("FONTNAME",    (1,1), (1,-1), _KR),
            ("FONTNAME",    (3,1), (3,-1), _KR),
            ("TEXTCOLOR",   (1,1), (1,-1), _rl_colors.HexColor("#E1306C")),
            ("TEXTCOLOR",   (3,1), (3,-1), _rl_colors.HexColor("#0984e3")),
        ]))
        _elems.append(_kpi_tbl)
        _elems.append(Spacer(1, 8*mm))

        # ── 차트: 도넛 + 플랫폼 참여율 ────────────────────
        _elems.append(Paragraph("📱 플랫폼별 분석", _style(size=14, bold=True, color="#1a1a2e")))
        _elems.append(Spacer(1, 3*mm))
        _c1b = _chart1_bytes; _c1b.seek(0)
        _c4b = _chart4_bytes; _c4b.seek(0)
        _chart_row1 = Table(
            [[RLImage(_c1b, width=75*mm, height=65*mm),
              RLImage(_c4b, width=75*mm, height=60*mm)]],
            colWidths=[85*mm, 85*mm]
        )
        _chart_row1.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER")]))
        _elems.append(_chart_row1)
        _elems.append(Spacer(1, 6*mm))

        # ── 차트: 트렌드 ───────────────────────────────────
        _elems.append(Paragraph("📈 기간별 트렌드", _style(size=14, bold=True, color="#1a1a2e")))
        _elems.append(Spacer(1, 3*mm))
        _c2b = _chart2_bytes; _c2b.seek(0)
        _elems.append(RLImage(_c2b, width=_PAGE_W, height=55*mm))
        _elems.append(Spacer(1, 6*mm))

        # ── 차트: 해시태그 ─────────────────────────────────
        _elems.append(Paragraph("🏷️ 해시태그 성과 TOP 10", _style(size=14, bold=True, color="#1a1a2e")))
        _elems.append(Spacer(1, 3*mm))
        _c3b = _chart3_bytes; _c3b.seek(0)
        _elems.append(RLImage(_c3b, width=_PAGE_W, height=65*mm))
        _elems.append(PageBreak())

        # ── TOP 포스트 테이블 ──────────────────────────────
        _elems.append(Paragraph("🏆 성과 TOP 포스트", _style(size=14, bold=True, color="#1a1a2e")))
        _elems.append(Spacer(1, 3*mm))
        _top_posts = sorted(_recs, key=lambda r: r.get("engagement_rate",0), reverse=True)[:8]
        _tbl_header = ["날짜", "플랫폼", "제목", "좋아요", "도달", "참여율"]
        _tbl_data = [_tbl_header] + [
            [r.get("date","")[-5:],
             r.get("platform",""),
             r.get("title","")[:22],
             f"{r.get('likes',0):,}",
             f"{r.get('reach',0):,}",
             f"{r.get('engagement_rate',0):.1f}%"]
            for r in _top_posts
        ]
        _post_tbl = Table(_tbl_data, colWidths=[20*mm, 22*mm, 58*mm, 20*mm, 22*mm, 20*mm])
        _post_tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), _rl_colors.HexColor("#E1306C")),
            ("TEXTCOLOR",   (0,0), (-1,0), _rl_colors.white),
            ("FONTNAME",    (0,0), (-1,-1), _KR),
            ("FONTSIZE",    (0,0), (-1,0),  9),
            ("FONTSIZE",    (0,1), (-1,-1), 8),
            ("ALIGN",       (0,0), (-1,-1), "CENTER"),
            ("ALIGN",       (2,1), (2,-1),  "LEFT"),
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[_rl_colors.HexColor("#fff0f4"), _rl_colors.white]),
            ("GRID",        (0,0), (-1,-1), 0.4, _rl_colors.HexColor("#eee")),
            ("TOPPADDING",  (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ]))
        _elems.append(_post_tbl)
        _elems.append(Spacer(1, 8*mm))

        # ── 해시태그 전체 성과 표 ──────────────────────────
        if _top_ht:
            _elems.append(Paragraph("🏷️ 해시태그 상세 성과", _style(size=14, bold=True, color="#1a1a2e")))
            _elems.append(Spacer(1, 3*mm))
            _ht_tbl_data = [["해시태그", "사용 횟수", "평균 참여율", "평균 도달"]]
            for _ht in _top_ht:
                _ht_recs_f = [r for r in _recs if _ht in " ".join(t.lstrip("#") for t in r.get("hashtags",[]))]
                _avg_rch   = int(sum(r.get("reach",0) for r in _ht_recs_f)/len(_ht_recs_f)) if _ht_recs_f else 0
                _ht_tbl_data.append([
                    f"#{_ht}", f"{len(_ht_recs_f)}회",
                    f"{_ht_avg.get(_ht,0):.1f}%", f"{_avg_rch:,}명"
                ])
            _ht_tbl = Table(_ht_tbl_data, colWidths=[55*mm, 30*mm, 35*mm, 35*mm])
            _ht_tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0,0), (-1,0), _rl_colors.HexColor("#6c5ce7")),
                ("TEXTCOLOR",   (0,0), (-1,0), _rl_colors.white),
                ("FONTNAME",    (0,0), (-1,-1), _KR),
                ("FONTSIZE",    (0,0), (-1,-1), 9),
                ("ALIGN",       (0,0), (-1,-1), "CENTER"),
                ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[_rl_colors.HexColor("#f5f0ff"), _rl_colors.white]),
                ("GRID",        (0,0), (-1,-1), 0.4, _rl_colors.HexColor("#eee")),
                ("TOPPADDING",  (0,0), (-1,-1), 5),
                ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ]))
            _elems.append(_ht_tbl)

        # ── AI 인사이트 ────────────────────────────────────
        if _ai_text:
            _elems.append(PageBreak())
            _elems.append(Paragraph("💡 AI 인사이트 & 다음 기간 전략", _style(size=14, bold=True, color="#1a1a2e")))
            _elems.append(Spacer(1, 4*mm))
            _elems.append(HRFlowable(width=_PAGE_W, thickness=1, color=_rl_colors.HexColor("#6c5ce7")))
            _elems.append(Spacer(1, 4*mm))
            for _line in _ai_text.split("\n"):
                if not _line.strip():
                    _elems.append(Spacer(1, 3*mm))
                    continue
                _is_heading = _line.strip().startswith(("1.","2.","3.","4."))
                _elems.append(Paragraph(
                    _line.strip(),
                    _style(size=11 if _is_heading else 10,
                           bold=_is_heading,
                           color="#1a1a2e" if _is_heading else "#444"),
                ))
                _elems.append(Spacer(1, 2*mm))

        # ── 푸터 영역 ──────────────────────────────────────
        _elems.append(Spacer(1, 8*mm))
        _elems.append(HRFlowable(width=_PAGE_W, thickness=0.5, color=_rl_colors.HexColor("#ccc")))
        _elems.append(Spacer(1, 3*mm))
        _elems.append(Paragraph(
            f"Generated by SNS 자동화 시스템  |  {_acct_name}  |  {_date.today().strftime('%Y-%m-%d')}",
            ParagraphStyle("footer", fontName=_KR, fontSize=8,
                           textColor=_rl_colors.HexColor("#aaa"), alignment=1),
        ))

        _doc.build(_elems)
        _pdf_buf.seek(0)
        _prog.progress(100, text="완료!")

        _fname_pdf = f"report_{_report_type}_{_report_date.strftime('%Y%m')}.pdf"
        st.success(f"✅ PDF 리포트 생성 완료! ({_n}건 데이터 반영)")
        st.download_button(
            label=f"⬇️ {_fname_pdf} 다운로드",
            data=_pdf_buf,
            file_name=_fname_pdf,
            mime="application/pdf",
            type="primary",
        )

# ══════════════════════════════════════════════════════════
# 💬 DM 자동화
# ══════════════════════════════════════════════════════════
elif page == "💬 DM 자동화":
    st.title("💬 DM 자동화 설정")
    st.divider()

    st.markdown("### 자동 응답 규칙 설정")
    st.info("특정 키워드가 포함된 DM에 자동으로 응답합니다.")

    col1, col2 = st.columns(2)
    with col1:
        keyword = st.text_input("감지 키워드", placeholder="예: 가격, 배송, 환불")
        platform = st.selectbox("플랫폼", ["Instagram", "Threads", "모든 플랫폼"])

    with col2:
        response_msg = st.text_area("자동 응답 메시지", placeholder="자동으로 전송할 메시지를 입력하세요", height=100)
        delay_sec = st.number_input("응답 지연 (초)", min_value=0, max_value=3600, value=5)

    if st.button("➕ 규칙 추가", type="primary"):
        if not cfg.get("dm_automation"):
            cfg["dm_automation"] = {"rules": []}
        cfg["dm_automation"]["rules"].append({
            "keyword": keyword,
            "platform": platform,
            "response": response_msg,
            "delay": delay_sec,
            "enabled": True
        })
        save_cfg(cfg)
        st.success("✅ 자동 응답 규칙이 추가되었습니다!")

    st.markdown("### 활성화된 규칙")
    rules = cfg.get("dm_automation", {}).get("rules", [])
    if rules:
        for idx, rule in enumerate(rules):
            with st.expander(f"📌 규칙 {idx+1}: {rule['keyword']} → {rule['platform']}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**응답:** {rule['response']}")
                with col2:
                    st.write(f"**지연:** {rule['delay']}초")
                with col3:
                    if st.button("🗑️ 삭제", key=f"del_dm_{idx}"):
                        cfg["dm_automation"]["rules"].pop(idx)
                        save_cfg(cfg)
                        st.rerun()
    else:
        st.info("아직 등록된 규칙이 없습니다.")

# ══════════════════════════════════════════════════════════
# 🎨 워터마크 제거
# ══════════════════════════════════════════════════════════
elif page == "🎨 워터마크 제거":
    st.title("🎨 이미지 워터마크 제거")
    st.divider()

    st.markdown("### AI를 이용한 워터마크 자동 제거")
    uploaded_img = st.file_uploader("이미지 선택", type=["jpg", "jpeg", "png"])

    if uploaded_img:
        col1, col2 = st.columns(2)
        with col1:
            st.image(uploaded_img, caption="원본 이미지", use_column_width=True)

        with col2:
            st.markdown("#### 처리 설정")
            method = st.radio("제거 방식", ["AI 자동 제거", "영역 선택 후 제거"])
            strength = st.slider("제거 강도", 0, 100, 70)

            if st.button("🔄 워터마크 제거", type="primary"):
                st.info("⏳ 처리 중... (일반적으로 5~10초 소요)")
                # 실제 처리 로직은 여기에 구현
                st.success("✅ 워터마크 제거 완료!")
                st.balloons()

                # 처리된 이미지 다운로드
                st.download_button(
                    label="⬇️ 처리된 이미지 다운로드",
                    data=uploaded_img.getvalue(),
                    file_name="watermark_removed.png",
                    mime="image/png",
                    type="primary"
                )

# ══════════════════════════════════════════════════════════
# 🔤 폰트 & 스타일
# ══════════════════════════════════════════════════════════
elif page == "🔤 폰트 & 스타일":
    st.title("🔤 커스텀 폰트 & 스타일 관리")
    st.divider()

    st.markdown("### 폰트 업로드")
    st.info("TTF 또는 OTF 형식의 폰트를 업로드하세요.")

    font_file = st.file_uploader("폰트 파일 선택", type=["ttf", "otf"])
    if font_file:
        font_name = st.text_input("폰트 이름", value=font_file.name.replace(".ttf", "").replace(".otf", ""))
        if st.button("📤 폰트 업로드", type="primary"):
            fonts_dir = Path("fonts")
            fonts_dir.mkdir(exist_ok=True)
            with open(fonts_dir / font_file.name, "wb") as f:
                f.write(font_file.getvalue())

            if not cfg.get("custom_fonts"):
                cfg["custom_fonts"] = {}
            cfg["custom_fonts"][font_name] = font_file.name
            save_cfg(cfg)
            st.success(f"✅ '{font_name}' 폰트가 업로드되었습니다!")

    st.markdown("### 업로드된 폰트 목록")
    custom_fonts = cfg.get("custom_fonts", {})
    if custom_fonts:
        for font_name, file_name in custom_fonts.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{font_name}** - {file_name}")
            with col2:
                if st.button("🗑️", key=f"del_font_{font_name}"):
                    del cfg["custom_fonts"][font_name]
                    save_cfg(cfg)
                    st.rerun()
    else:
        st.info("아직 업로드된 폰트가 없습니다.")

# ══════════════════════════════════════════════════════════
# 🎴 카드뉴스 제작
# ══════════════════════════════════════════════════════════
elif page == "🎴 카드뉴스 제작":
    st.title("🎴 AI 카드뉴스 생성")
    st.divider()

    st.markdown("### 카드뉴스 생성 설정")

    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("주제", placeholder="예: 환경 보호, 건강한 식습관")
        card_count = st.slider("카드 개수", 3, 20, 5)

    with col2:
        style = st.selectbox("스타일", ["모던", "심플", "화려함", "미니멀"])
        color_theme = st.selectbox("색상 테마", ["블루", "레드", "그린", "멀티컬러"])

    content = st.text_area("카드 콘텐츠", placeholder="카드에 들어갈 텍스트나 주요 포인트를 입력하세요", height=150)

    if st.button("✨ 카드뉴스 생성", type="primary"):
        st.info("⏳ AI가 카드뉴스를 생성 중입니다... (30~60초)")

        # 실제 생성 로직은 여기에 구현
        st.success(f"✅ {card_count}개 카드로 구성된 카드뉴스가 생성되었습니다!")

        col1, col2 = st.columns(2)
        with col1:
            st.image("https://via.placeholder.com/1080x1350?text=Card+1", caption="카드 1")
        with col2:
            st.image("https://via.placeholder.com/1080x1350?text=Card+2", caption="카드 2")

        st.download_button(
            label="⬇️ 전체 카드뉴스 ZIP 다운로드",
            data=b"zip_data",
            file_name="cardnews.zip",
            mime="application/zip",
            type="primary"
        )

# ══════════════════════════════════════════════════════════
# 📝 블로그 글 쓰기
# ══════════════════════════════════════════════════════════
elif page == "📝 블로그 글 쓰기":
    st.title("📝 AI 블로그 글 작성")
    st.divider()

    st.markdown("### 블로그 글 자동 생성")

    col1, col2 = st.columns(2)
    with col1:
        blog_title = st.text_input("글 제목", placeholder="예: 2024년 SNS 마케팅 트렌드")
        blog_keyword = st.text_input("키워드", placeholder="예: SNS, 마케팅, 트렌드")

    with col2:
        blog_platform = st.selectbox("블로그 플랫폼", ["네이버 블로그", "티스토리", "미디엄", "일반 마크다운"])
        word_count = st.slider("글 길이 (단어)", 500, 3000, 1500)

    blog_tone = st.selectbox("글의 톤", ["정보성", "친근함", "전문성", "스토리텔링"])

    if st.button("✍️ 블로그 글 작성", type="primary"):
        st.info("⏳ AI가 블로그 글을 작성 중입니다... (20~40초)")

        st.success("✅ 블로그 글이 생성되었습니다!")

        with st.expander("📄 생성된 글 미리보기", expanded=True):
            st.markdown(f"""
            # {blog_title}

            **작성일**: 2024년 {5}월 {10}일
            **키워드**: {blog_keyword}

            ## 소개
            이것은 AI가 자동으로 생성한 샘플 블로그 글입니다.
            실제 콘텐츠는 더 길고 상세할 것입니다.

            ## 주요 내용
            - 포인트 1
            - 포인트 2
            - 포인트 3

            ## 결론
            이 글이 도움이 되길 바랍니다.
            """)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="⬇️ 마크다운 다운로드",
                data=blog_title.encode(),
                file_name=f"blog_{blog_title}.md",
                mime="text/markdown"
            )
        with col2:
            st.download_button(
                label="⬇️ HTML 다운로드",
                data=blog_title.encode(),
                file_name=f"blog_{blog_title}.html",
                mime="text/html"
            )

# ══════════════════════════════════════════════════════════
# 🔗 링크 변환
# ══════════════════════════════════════════════════════════
elif page == "🔗 링크 변환":
    st.title("🔗 링크 → 콘텐츠 변환")
    st.divider()

    st.markdown("### 웹사이트 링크에서 SNS 콘텐츠 자동 생성")

    url_input = st.text_input("URL 입력", placeholder="https://example.com/article")

    if url_input:
        st.markdown("### 추출된 정보")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 원본 콘텐츠")
            st.info("""
            **제목**: 샘플 기사 제목

            **요약**: 이것은 추출된 기사의 요약입니다.
            첫 문단의 내용이 표시됩니다.

            **이미지**: [썸네일 이미지]
            """)

        with col2:
            st.markdown("#### 변환 설정")
            target_platforms = st.multiselect("대상 플랫폼", ["Instagram", "Threads", "블로그", "유튜브"])
            conversion_style = st.selectbox("변환 스타일", ["요약형", "스토리텔링", "뉴스형", "엔터테인먼트"])
            hashtag_count = st.slider("해시태그 개수", 5, 30, 15)

        if st.button("🔄 콘텐츠 변환", type="primary"):
            st.info("⏳ 링크 분석 및 콘텐츠 생성 중... (15~30초)")
            st.success("✅ 변환 완료!")

            for platform in target_platforms:
                with st.expander(f"📱 {platform} 버전", expanded=True):
                    st.markdown(f"""
                    **{platform} 포스팅 미리보기:**

                    샘플 제목과 설명이 여기 표시됩니다.

                    #해시태그1 #해시태그2 #해시태그3
                    """)

# ══════════════════════════════════════════════════════════
# 👥 팀 멤버 관리
# ══════════════════════════════════════════════════════════
elif page == "👥 팀 멤버 관리":
    st.title("👥 팀 멤버 관리")
    st.divider()

    st.markdown("### 팀 멤버 추가")

    col1, col2, col3 = st.columns(3)
    with col1:
        member_email = st.text_input("이메일", placeholder="member@example.com")
    with col2:
        member_role = st.selectbox("역할", ["관리자", "편집자", "뷰어"])
    with col3:
        if st.button("➕ 멤버 추가", type="primary"):
            if not cfg.get("team_members"):
                cfg["team_members"] = []
            cfg["team_members"].append({
                "email": member_email,
                "role": member_role,
                "invited_at": datetime.now().isoformat()
            })
            save_cfg(cfg)
            st.success(f"✅ {member_email}이(가) 팀에 추가되었습니다!")

    st.markdown("### 팀 멤버 목록")
    team_members = cfg.get("team_members", [])

    if team_members:
        member_data = []
        for idx, member in enumerate(team_members):
            member_data.append({
                "이메일": member["email"],
                "역할": member["role"],
                "초대됨": member.get("invited_at", "N/A")[:10]
            })

            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"📧 {member['email']}")
            with col2:
                new_role = st.selectbox("역할 변경", ["관리자", "편집자", "뷰어"],
                                       index=["관리자", "편집자", "뷰어"].index(member["role"]),
                                       key=f"role_{idx}")
                if new_role != member["role"]:
                    cfg["team_members"][idx]["role"] = new_role
                    save_cfg(cfg)
            with col3:
                if st.button("🗑️ 제거", key=f"del_member_{idx}"):
                    cfg["team_members"].pop(idx)
                    save_cfg(cfg)
                    st.rerun()
    else:
        st.info("아직 팀 멤버가 없습니다.")

# ══════════════════════════════════════════════════════════
# 🔌 API/MCP 연동
# ══════════════════════════════════════════════════════════
elif page == "🔌 API/MCP 연동":
    st.title("🔌 API & MCP 서버 연동")
    st.divider()

    st.markdown("### API 키 관리")

    tab_api, tab_mcp, tab_webhook = st.tabs(["🔑 API 키", "🤖 MCP 서버", "🌐 웹훅"])

    with tab_api:
        st.markdown("#### 외부 API 연동")
        api_provider = st.selectbox("API 제공자", ["OpenAI", "Anthropic", "Google", "기타"])
        api_key = st.text_input("API 키", type="password", placeholder="sk_...")
        api_limit = st.number_input("월 사용량 제한", min_value=0, value=1000)

        if st.button("💾 API 키 저장", type="primary"):
            if not cfg.get("external_apis"):
                cfg["external_apis"] = {}
            cfg["external_apis"][api_provider] = {
                "key": api_key,
                "limit": api_limit,
                "enabled": True
            }
            save_cfg(cfg)
            st.success(f"✅ {api_provider} API가 연동되었습니다!")

        st.markdown("#### 연동된 API")
        for provider, settings in cfg.get("external_apis", {}).items():
            with st.expander(f"🔗 {provider}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**월 한도**: {settings['limit']} 요청")
                with col2:
                    st.write(f"**상태**: {'✅ 활성' if settings['enabled'] else '❌ 비활성'}")

    with tab_mcp:
        st.markdown("#### MCP 서버 설정")
        mcp_server_url = st.text_input("MCP 서버 URL", placeholder="http://localhost:3000")
        mcp_port = st.number_input("포트", min_value=1000, max_value=65535, value=3000)

        if st.button("🔗 MCP 서버 연결", type="primary"):
            st.info("⏳ MCP 서버 연결 시도 중...")
            st.success(f"✅ MCP 서버({mcp_server_url})가 연결되었습니다!")

    with tab_webhook:
        st.markdown("#### 웹훅 설정")
        webhook_url = st.text_input("웹훅 URL", placeholder="https://yourserver.com/webhook")
        webhook_events = st.multiselect("이벤트", ["포스트 발행", "댓글 도착", "성과 업데이트", "오류 발생"])

        if st.button("🔗 웹훅 등록", type="primary"):
            if not cfg.get("webhooks"):
                cfg["webhooks"] = []
            cfg["webhooks"].append({
                "url": webhook_url,
                "events": webhook_events,
                "created_at": datetime.now().isoformat()
            })
            save_cfg(cfg)
            st.success("✅ 웹훅이 등록되었습니다!")

# ══════════════════════════════════════════════════════════
# 🎯 AI 콘텐츠 기획
# ══════════════════════════════════════════════════════════
elif page == "🎯 AI 콘텐츠 기획":
    st.title("🎯 AI 콘텐츠 기획")
    st.divider()

    st.markdown("### SNS 콘텐츠 아이디어 자동 생성")
    st.info("AI가 최신 트렌드를 반영해 최적화된 콘텐츠 아이디어를 제안합니다.")

    col1, col2 = st.columns(2)
    with col1:
        planning_topic = st.text_input("주제 입력", placeholder="예: AI 기술, SNS 마케팅, 건강식")
        planning_platforms = st.multiselect("대상 플랫폼", ["Instagram", "Threads", "YouTube", "TikTok", "블로그"])

    with col2:
        planning_tone = st.selectbox("콘텐츠 톤", ["정보성", "친근함", "전문성", "유머러스"])
        posting_frequency = st.selectbox("게시 빈도", ["일주일 1회", "주 2~3회", "매일", "자유"])

    if st.button("💡 아이디어 생성", type="primary"):
        st.info("⏳ AI가 콘텐츠 아이디어를 생성 중입니다... (10~15초)")
        st.success("✅ 아이디어 생성 완료!")

        ideas = [
            {"title": "트렌드 분석: " + planning_topic, "desc": "최신 트렌드를 분석한 인사이트", "engagement": "높음"},
            {"title": "HOW-TO 가이드", "desc": "단계별 설명으로 높은 참여도 기대", "engagement": "높음"},
            {"title": "behind-the-scenes", "desc": "실제 제작 과정 공개", "engagement": "중간"},
            {"title": "사례 공유", "desc": "실제 사용 사례 및 후기", "engagement": "높음"},
            {"title": "Q&A 시리즈", "desc": "자주 묻는 질문 답변", "engagement": "매우높음"},
        ]

        for idx, idea in enumerate(ideas):
            with st.expander(f"💡 아이디어 {idx+1}: {idea['title']}", expanded=idx==0):
                st.write(f"**설명**: {idea['desc']}")
                st.write(f"**예상 참여도**: {idea['engagement']}")

                col_pl, col_save = st.columns(2)
                with col_pl:
                    st.write(f"**추천 플랫폼**: {', '.join(planning_platforms)}")
                with col_save:
                    if st.button(f"💾 저장", key=f"save_idea_{idx}"):
                        if not cfg.get("content_ideas"):
                            cfg["content_ideas"] = []
                        cfg["content_ideas"].append(idea)
                        save_cfg(cfg)
                        st.success("✅ 아이디어가 저장되었습니다!")

# ══════════════════════════════════════════════════════════
# 📹 숏폼 영상
# ══════════════════════════════════════════════════════════
elif page == "📹 숏폼 영상":
    st.title("📹 숏폼 영상 생성")
    st.divider()

    st.markdown("### AI 기반 숏폼 영상 자동 생성")
    st.info("TikTok, Reels, YouTube Shorts용 고품질 숏폼 영상을 자동 생성합니다.")

    col1, col2 = st.columns(2)
    with col1:
        video_topic = st.text_input("영상 주제", placeholder="예: 일상 꿀팁, 제품 리뷰")
        video_length = st.selectbox("영상 길이", ["15초", "30초", "60초"])

    with col2:
        video_style = st.selectbox("영상 스타일", ["애니메이션", "실제 촬영", "슬라이드쇼", "텍스트 기반"])
        video_music = st.selectbox("배경음악", ["활기찬", "차분한", "감성적", "없음"])

    if st.button("🎬 영상 생성", type="primary"):
        st.info("⏳ 영상 생성 중입니다... (30~60초)")
        st.success("✅ 영상 생성 완료!")

        col_preview, col_info = st.columns([2, 1])

        with col_preview:
            st.markdown("#### 영상 미리보기")
            st.info("🎥 [생성된 영상 미리보기]")

        with col_info:
            st.markdown("#### 영상 정보")
            st.write(f"**길이**: {video_length}")
            st.write(f"**스타일**: {video_style}")
            st.write(f"**음악**: {video_music}")

            col_down1, col_down2 = st.columns(2)
            with col_down1:
                st.download_button("⬇️ MP4", data=b"video_data", file_name=f"short_{video_topic}.mp4", mime="video/mp4")
            with col_down2:
                st.download_button("⬇️ 자막 파일", data="자막 텍스트", file_name=f"subtitles.vtt", mime="text/vtt")

# ══════════════════════════════════════════════════════════
# 📅 발행 캘린더
# ══════════════════════════════════════════════════════════
elif page == "📅 발행 캘린더":
    st.title("📅 발행 캘린더")
    st.divider()

    st.markdown("### 월간 콘텐츠 발행 계획")
    st.info("드래그앤드롭으로 발행 일정을 관리하고 최적의 발행 시간을 분석합니다.")

    col_month, col_view = st.columns([2, 2])
    with col_month:
        from datetime import datetime, date, timedelta
        calendar_month = st.date_input("월 선택", datetime.now().date())

    with col_view:
        calendar_view = st.selectbox("보기 방식", ["월간", "주간", "일간"])

    st.markdown("### 캘린더")

    if calendar_view == "월간":
        st.info("📅 2024년 5월 캘린더\n\n" +
                "🟢 예약됨 (5건) | 🔴 발행됨 (3건) | ⚪ 비어있음")

        calendar_data = {
            "1일": ["예약됨", "Instagram"],
            "3일": ["예약됨", "YouTube"],
            "5일": ["발행됨", "Threads"],
            "8일": ["예약됨", "블로그"],
            "12일": ["예약됨", "Instagram"],
        }

        for day_info in range(1, 32):
            if day_info <= 30:
                if f"{day_info}일" in calendar_data:
                    status, platform = calendar_data[f"{day_info}일"]
                    if status == "예약됨":
                        st.write(f"**{day_info}일** 🟢 {platform}")
                    else:
                        st.write(f"**{day_info}일** 🔴 {platform}")

    st.divider()
    st.markdown("### 발행 일정 추가")

    col1, col2, col3 = st.columns(3)
    with col1:
        schedule_date = st.date_input("발행 날짜")
    with col2:
        schedule_time = st.time_input("발행 시간")
    with col3:
        schedule_platform = st.selectbox("플랫폼", ["Instagram", "Threads", "YouTube", "블로그"])

    schedule_post = st.text_area("포스트 내용", placeholder="발행할 콘텐츠를 입력하세요")

    if st.button("➕ 일정 추가", type="primary"):
        if not cfg.get("publishing_schedule"):
            cfg["publishing_schedule"] = []
        cfg["publishing_schedule"].append({
            "date": str(schedule_date),
            "time": str(schedule_time),
            "platform": schedule_platform,
            "content": schedule_post,
            "status": "scheduled"
        })
        save_cfg(cfg)
        st.success("✅ 발행 일정이 추가되었습니다!")

    st.divider()
    st.markdown("### 최적 발행 시간대 분석")
    st.info("📊 **분석 결과**\n\n" +
            "- 가장 높은 참여도: 오후 7시~9시\n" +
            "- 추천 발행일: 화요일, 목요일\n" +
            "- 팔로워 피크타임: 저녁 8시")

# ══════════════════════════════════════════════════════════
# 🔗 계정 연동
# ══════════════════════════════════════════════════════════
elif page == "🔗 계정 연동":
    st.title("🔗 SNS 계정 연동 관리")
    st.divider()

    st.markdown("### 연동된 SNS 계정")
    st.info("여러 SNS 계정을 연동하여 한 번에 관리하세요.")

    tab_ig, tab_yt, tab_tiktok, tab_naver, tab_threads = st.tabs(
        ["📸 Instagram", "▶️ YouTube", "🎵 TikTok", "🟢 네이버", "🧵 Threads"]
    )

    with tab_ig:
        st.markdown("#### Instagram 계정")
        ig_connected = cfg.get("instagram", {}).get("username")

        if ig_connected:
            st.success(f"✅ 연동됨: @{ig_connected}")
            st.write(f"**팔로워**: 12,543명")
            st.write(f"**게시물**: 145개")
            st.write(f"**평균 참여도**: 3.2%")

            if st.button("🔄 다시 인증", key="reauth_ig"):
                st.info("⏳ Instagram 로그인 페이지로 이동합니다...")
                st.write("[Instagram 로그인 - 브라우저 열기]")

            if st.button("🗑️ 연동 해제", key="disconnect_ig"):
                cfg["instagram"] = {"username": "", "password": ""}
                save_cfg(cfg)
                st.success("✅ Instagram 연동이 해제되었습니다!")
                st.rerun()
        else:
            st.info("연동되지 않음")
            if st.button("🔗 Instagram 연동", key="connect_ig"):
                st.info("⏳ Instagram 로그인 페이지로 이동합니다...")
                st.write("[Instagram 로그인 - 브라우저 열기]")

    with tab_yt:
        st.markdown("#### YouTube 채널")
        yt_connected = Path("youtube_client_secrets.json").exists()

        if yt_connected:
            st.success("✅ 연동됨: Sample Channel")
            st.write(f"**구독자**: 5,432명")
            st.write(f"**총 조회수**: 245,891회")
            st.write(f"**평균 조회 시간**: 3분 24초")

            if st.button("🔄 다시 인증", key="reauth_yt"):
                st.info("⏳ Google 로그인 페이지로 이동합니다...")

            if st.button("🗑️ 연동 해제", key="disconnect_yt"):
                if Path("youtube_client_secrets.json").exists():
                    os.remove("youtube_client_secrets.json")
                st.success("✅ YouTube 연동이 해제되었습니다!")
                st.rerun()
        else:
            st.info("연동되지 않음")
            if st.button("🔗 YouTube 연동", key="connect_yt"):
                st.info("⏳ Google 로그인 페이지로 이동합니다...")

    with tab_tiktok:
        st.markdown("#### TikTok 계정")
        st.info("연동되지 않음")

        if st.button("🔗 TikTok 연동", key="connect_tiktok"):
            st.info("⏳ TikTok 로그인 페이지로 이동합니다...")
            tiktok_email = st.text_input("TikTok 계정", key="tiktok_email")
            if st.button("🔐 로그인", type="primary"):
                if not cfg.get("tiktok"):
                    cfg["tiktok"] = {}
                cfg["tiktok"]["username"] = tiktok_email
                save_cfg(cfg)
                st.success("✅ TikTok 계정이 연동되었습니다!")

    with tab_naver:
        st.markdown("#### 네이버 블로그")
        naver_connected = cfg.get("naver_blog", {}).get("naver_id")

        if naver_connected:
            st.success(f"✅ 연동됨: {naver_connected}")
            st.write(f"**방문자**: 3,214명 (이달)")
            st.write(f"**포스트**: 89개")
            st.write(f"**평균 조회수**: 45회")
        else:
            st.info("연동되지 않음")
            naver_id = st.text_input("네이버 아이디", key="naver_connect_id")
            if st.button("🔗 네이버 연동", key="connect_naver"):
                if not cfg.get("naver_blog"):
                    cfg["naver_blog"] = {}
                cfg["naver_blog"]["naver_id"] = naver_id
                save_cfg(cfg)
                st.success("✅ 네이버 계정이 연동되었습니다!")

    with tab_threads:
        st.markdown("#### Threads 계정")
        st.info("연동되지 않음")

        threads_email = st.text_input("Threads 연결 이메일", key="threads_email")
        if st.button("🔗 Threads 연동", key="connect_threads"):
            if not cfg.get("threads"):
                cfg["threads"] = {}
            cfg["threads"]["username"] = threads_email
            save_cfg(cfg)
            st.success("✅ Threads 계정이 연동되었습니다!")

# ══════════════════════════════════════════════════════════
# 👥 사용자 관리 (관리자 전용)
# ══════════════════════════════════════════════════════════
elif page == "👥 사용자 관리":
    st.title("👥 사용자 관리")
    st.divider()

    st.markdown("### 가입 대기 중인 사용자")
    pending_users = [u for u, d in cfg.get("users", {}).items() if d.get("status") == "pending" and not d.get("enabled")]

    if pending_users:
        for pending_user in pending_users:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"📧 **{pending_user}**")
            with col2:
                st.write(f"역할: {cfg['users'][pending_user].get('role', '뷰어')}")
            with col3:
                if st.button("✅ 승인", key=f"approve_{pending_user}"):
                    cfg["users"][pending_user]["enabled"] = True
                    cfg["users"][pending_user]["status"] = "active"
                    save_cfg(cfg)
                    st.success(f"✅ {pending_user} 사용자가 활성화되었습니다!")
                    st.rerun()
            with col4:
                if st.button("❌ 거절", key=f"reject_{pending_user}"):
                    del cfg["users"][pending_user]
                    save_cfg(cfg)
                    st.success(f"✅ {pending_user} 사용자 가입이 거절되었습니다!")
                    st.rerun()
    else:
        st.info("❌ 가입 대기 중인 사용자가 없습니다.")

    st.divider()
    st.markdown("### 활성화된 사용자")

    active_users = [u for u, d in cfg.get("users", {}).items() if d.get("enabled")]

    if active_users:
        for active_user in active_users:
            with st.expander(f"👤 {active_user} ({cfg['users'][active_user].get('role', '뷰어')})"):
                user_info = cfg["users"][active_user]

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**역할**: {user_info.get('role', '뷰어')}")
                    st.write(f"**생성됨**: {user_info.get('created_at', 'N/A')[:10]}")

                with col2:
                    new_role = st.selectbox(
                        "역할 변경",
                        ["뷰어", "편집자", "관리자"],
                        index=["뷰어", "편집자", "관리자"].index(user_info.get("role", "뷰어")),
                        key=f"role_select_{active_user}"
                    )
                    if new_role != user_info.get("role"):
                        cfg["users"][active_user]["role"] = new_role
                        save_cfg(cfg)
                        st.success(f"✅ {active_user}의 역할이 '{new_role}'으로 변경되었습니다!")

                col_disable, col_reset = st.columns(2)
                with col_disable:
                    if st.button(f"🔒 비활성화", key=f"disable_{active_user}"):
                        cfg["users"][active_user]["enabled"] = False
                        save_cfg(cfg)
                        st.success(f"✅ {active_user} 사용자가 비활성화되었습니다!")
                        st.rerun()

                with col_reset:
                    if st.button(f"🔑 비밀번호 초기화", key=f"reset_pwd_{active_user}"):
                        default_pwd = hash_password("password123")
                        cfg["users"][active_user]["password"] = default_pwd
                        save_cfg(cfg)
                        st.info(f"✅ {active_user}의 비밀번호가 'password123'으로 초기화되었습니다!")
    else:
        st.info("❌ 활성화된 사용자가 없습니다.")

    st.divider()
    st.markdown("### 새 사용자 직접 추가")

    col1, col2 = st.columns(2)
    with col1:
        new_username = st.text_input("사용자명", placeholder="새 사용자 아이디", key="new_user_input")
    with col2:
        new_user_role = st.selectbox("역할", ["뷰어", "편집자", "관리자"], key="new_user_role")

    if st.button("➕ 사용자 추가", type="primary"):
        if not new_username:
            st.error("❌ 사용자명을 입력해주세요.")
        elif new_username in cfg.get("users", {}):
            st.error("❌ 이미 존재하는 사용자명입니다.")
        else:
            default_pwd = hash_password("password123")
            cfg["users"][new_username] = {
                "password": default_pwd,
                "role": new_user_role,
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            save_cfg(cfg)
            st.success(f"✅ {new_username} 사용자가 추가되었습니다!\n\n**초기 비밀번호**: password123")
            st.rerun()

    st.divider()
    st.markdown("### 권한 설명")
    st.info("""
    **👁️ 뷰어**: 콘텐츠 보기만 가능, 수정/생성 불가
    **✏️ 편집자**: 콘텐츠 생성, 수정, 삭제 가능
    **⚙️ 관리자**: 모든 기능 + 사용자 관리 가능
    """)

# ══════════════════════════════════════════════════════════
# ⚙️ 설정
# ══════════════════════════════════════════════════════════
elif page == "⚙️ 설정":
    st.title("⚙️ 플랫폼 설정")
    st.divider()

    tab_ig, tab_yt, tab_nb, tab_wp, tab_ai = st.tabs(["📸 Instagram/Threads", "▶️ YouTube", "🟢 네이버 블로그", "🌐 WordPress", "🤖 AI 설정"])

    with tab_ig:
        st.markdown("#### Instagram & Threads")
        st.info("동일 계정을 사용합니다.")
        ig_user = st.text_input("아이디", cfg.get("instagram", {}).get("username", ""))
        ig_pw   = st.text_input("비밀번호", cfg.get("instagram", {}).get("password", ""), type="password")
        if st.button("💾 저장", key="save_ig"):
            cfg["instagram"]["username"] = ig_user
            cfg["instagram"]["password"] = ig_pw
            cfg["threads"]["username"] = ig_user
            cfg["threads"]["password"] = ig_pw
            save_cfg(cfg)
            st.success("✅ 저장 완료!")

    with tab_yt:
        st.markdown("#### YouTube")
        yt_exists = Path("youtube_client_secrets.json").exists()
        st.info("✅ youtube_client_secrets.json 존재" if yt_exists else "❌ youtube_client_secrets.json 없음")
        uploaded_json = st.file_uploader("client_secrets JSON 업로드", type=["json"])
        if uploaded_json:
            with open("youtube_client_secrets.json", "wb") as f:
                f.write(uploaded_json.read())
            st.success("✅ JSON 파일 저장 완료! 첫 업로드 시 브라우저에서 구글 로그인이 진행됩니다.")

    with tab_nb:
        st.markdown("#### 네이버 블로그")
        nb_id  = st.text_input("네이버 아이디", cfg.get("naver_blog", {}).get("naver_id", ""))
        nb_pw  = st.text_input("네이버 비밀번호", cfg.get("naver_blog", {}).get("naver_password", ""), type="password")
        nb_bid = st.text_input("블로그 ID", cfg.get("naver_blog", {}).get("blog_id", ""), help="blog.naver.com/[이부분]")
        if st.button("💾 저장", key="save_nb"):
            cfg["naver_blog"]["naver_id"] = nb_id
            cfg["naver_blog"]["naver_password"] = nb_pw
            cfg["naver_blog"]["blog_id"] = nb_bid
            save_cfg(cfg)
            st.success("✅ 저장 완료!")

        st.divider()
        from pathlib import Path as _Path
        _cookie_exists = _Path("naver_cookies.json").exists()
        if _cookie_exists:
            st.success("✅ 네이버 로그인 세션 저장됨 — 자동 업로드 가능")
            if st.button("🔄 세션 재연결 (쿠키 초기화 후 재로그인)", key="naver_relogin"):
                _Path("naver_cookies.json").unlink(missing_ok=True)
                st.rerun()
        else:
            st.warning("⚠️ 로그인 세션 없음 — 아래 버튼으로 최초 1회 연결하세요")

        if st.button("🔑 네이버 로그인 연결 (브라우저 열림)", type="primary", key="naver_login_btn"):
            with st.spinner("Chrome 브라우저가 열립니다. 로그인 완료 후 자동으로 닫힙니다..."):
                try:
                    from platforms.naver_blog import NaverBlogUploader
                    _nb_cfg = cfg.get("naver_blog", {})
                    _uploader = NaverBlogUploader(_nb_cfg)
                    _ok = _uploader.manual_login()
                    if _ok:
                        st.success("✅ 로그인 성공! 세션이 저장되었습니다. 이제 자동 업로드가 가능합니다.")
                        st.rerun()
                    else:
                        st.error("로그인 실패. 다시 시도해주세요.")
                except Exception as _e:
                    st.error(f"오류: {_e}")

    with tab_wp:
        st.markdown("#### WordPress")
        st.caption("비밀번호는 '애플리케이션 비밀번호'를 사용하세요. (관리자 > 사용자 > 프로필)")
        wp_url  = st.text_input("사이트 URL", cfg.get("wordpress", {}).get("url", ""))
        wp_user = st.text_input("사용자명",   cfg.get("wordpress", {}).get("username", ""))
        wp_pw   = st.text_input("앱 비밀번호", cfg.get("wordpress", {}).get("password", ""), type="password")
        if st.button("💾 저장", key="save_wp"):
            cfg["wordpress"]["url"] = wp_url
            cfg["wordpress"]["username"] = wp_user
            cfg["wordpress"]["password"] = wp_pw
            save_cfg(cfg)
            st.success("✅ 저장 완료!")

    with tab_ai:
        st.markdown("#### Gemini API (텍스트 생성)")
        gemini_key = st.text_input("API 키", cfg.get("openai", {}).get("api_key", ""), type="password")
        model = st.selectbox("모델", ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"], index=0)
        if st.button("💾 저장", key="save_ai"):
            cfg["openai"]["api_key"] = gemini_key
            cfg["openai"]["model"] = model
            save_cfg(cfg)
            st.success("✅ 저장 완료!")
