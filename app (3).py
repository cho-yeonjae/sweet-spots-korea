import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import os
import urllib.parse
from datetime import datetime

st.set_page_config(
    page_title="Sweet Spots Seoul 🍰",
    page_icon="🍰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.main { background-color: #FFF9F5; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
.hero-title { font-family:'DM Serif Display',serif; font-size:2.4rem; color:#3B1F2B; line-height:1.15; margin:0; }
.hero-sub { font-size:1rem; color:#9B7B87; margin-top:6px; font-weight:300; }
.metric-row { display:flex; gap:12px; margin:1.2rem 0; flex-wrap:wrap; }
.metric-card { background:white; border-radius:14px; padding:16px 20px; flex:1; min-width:130px; border:1px solid #F0E6E0; }
.metric-card .val { font-family:'DM Serif Display',serif; font-size:1.9rem; color:#C0525A; display:block; }
.metric-card .lbl { font-size:0.75rem; color:#9B7B87; font-weight:500; text-transform:uppercase; letter-spacing:0.05em; }
.cafe-card { background:white; border-radius:16px; border:1px solid #F0E6E0; overflow:hidden; margin-bottom:12px; transition:box-shadow 0.2s; }
.cafe-card:hover { box-shadow: 0 4px 20px rgba(192,82,90,0.15); }
.cafe-body { padding:12px 14px; }
.cafe-name { font-weight:600; font-size:0.95rem; color:#3B1F2B; margin-bottom:4px; }
.cafe-tag { display:inline-block; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:500; margin-bottom:6px; }
.cafe-sig { font-size:0.8rem; color:#9B7B87; }
.cafe-rating { font-size:0.85rem; color:#C0525A; font-weight:500; }
.naver-btn { display:inline-block; margin-top:8px; padding:5px 12px; background:#03C75A; color:white !important;
             border-radius:8px; font-size:0.75rem; font-weight:600; text-decoration:none !important; }
.naver-btn:hover { background:#02a84a; }
section[data-testid="stSidebar"] { background:#3B1F2B !important; }
section[data-testid="stSidebar"] * { color:#F5E8E0 !important; }
hr { border-color:#F0E6E0; margin:1.2rem 0; }
.footer { text-align:center; font-size:0.78rem; color:#C0A090; padding-top:1.5rem; }
.sns-card { background:white; border-radius:14px; padding:14px 16px; border:1px solid #F0E6E0; margin-bottom:10px; }
.sns-card:hover { box-shadow:0 3px 14px rgba(192,82,90,0.12); }
.sns-source { font-size:0.72rem; font-weight:600; padding:2px 8px; border-radius:12px; }
.comm-card { background:white; border-radius:14px; padding:16px; border:1px solid #F0E6E0; margin-bottom:10px; }
.comm-card:hover { box-shadow:0 3px 14px rgba(192,82,90,0.12); }
</style>
""", unsafe_allow_html=True)

# ── 상수 ─────────────────────────────────────────────────────────────────────
CATEGORY_MAP = {
    "카페": "카페", "베이커리": "베이커리",
    "카페/베이커리": "카페·베이커리", "베이커리/카페": "카페·베이커리",
    "카페/디저트": "카페·디저트", "베이커리/디저트": "베이커리·디저트",
    "디저트": "디저트", "카페/전통": "전통·카페",
}
TYPE_COLORS = {
    "카페": "#F4A460", "베이커리": "#E07B7B", "카페·베이커리": "#C0525A",
    "카페·디저트": "#C49DE0", "베이커리·디저트": "#E0C07B",
    "디저트": "#7BCEC0", "전통·카페": "#7BADE0",
}
TYPE_EMOJI = {
    "카페": "☕", "베이커리": "🥐", "카페·베이커리": "🥐",
    "카페·디저트": "🍰", "베이커리·디저트": "🎂",
    "디저트": "🍮", "전통·카페": "🍡",
}
DEFAULT_IMG = "https://images.unsplash.com/photo-1519915028121-7d3463d20b13?w=400&q=80"

# ── SNS 핫 피드 데이터 ────────────────────────────────────────────────────────
SNS_FEEDS = [
    {
        "source": "인스타그램", "source_color": "#E1306C", "icon": "📸",
        "title": "성수동 크루아상 맛집 총정리 🥐",
        "desc": "성수에서 크루아상 하나는 먹어야 찐 성수 탐방! 베통·어니언·소하염전 비교 후기",
        "url": "https://www.instagram.com/explore/tags/%EC%84%B1%EC%88%98%EB%B2%A0%EC%9D%B4%EC%BB%A4%EB%A6%AC/",
        "tag": "#성수베이커리 #크루아상맛집",
        "likes": "8,241"
    },
    {
        "source": "네이버 블로그", "source_color": "#03C75A", "icon": "📝",
        "title": "연남동 디저트 카페 10선 — 데이트 코스 추천",
        "desc": "연남동 골목을 걸으며 스콘, 케이크, 소금빵까지! 인증 사진과 함께하는 솔직 리뷰",
        "url": "https://search.naver.com/search.naver?query=%EC%97%B0%EB%82%A8%EB%8F%99+%EB%94%94%EC%A0%80%ED%8A%B8+%EC%B9%B4%ED%8E%98",
        "tag": "#연남동카페 #데이트코스",
        "likes": "5,103"
    },
    {
        "source": "네이버 카페", "source_color": "#03C75A", "icon": "☕",
        "title": "[강남 빵집 탐방] 압구정·청담 파티스리 Best 7",
        "desc": "강남 파티스리 순례기! 기욤부터 오뗄두스까지, 프렌치 디저트 전문점 비교 리뷰",
        "url": "https://cafe.naver.com/ArticleSearchList.nhn?search.query=%EA%B0%95%EB%82%A8+%EB%B9%B5%EC%A7%91",
        "tag": "#강남빵집 #파티스리",
        "likes": "3,782"
    },
    {
        "source": "인스타그램", "source_color": "#E1306C", "icon": "📸",
        "title": "홍대 소금빵 맛집 지도 🗺️",
        "desc": "소금빵 마니아들의 홍대 탐방 지도. 자연도소금빵·오월의종 비교 & 웨이팅 팁",
        "url": "https://www.instagram.com/explore/tags/%EC%86%8C%EA%B8%88%EB%B9%B5/",
        "tag": "#소금빵 #홍대맛집",
        "likes": "12,558"
    },
    {
        "source": "네이버 블로그", "source_color": "#03C75A", "icon": "📝",
        "title": "종로 북촌 한옥 카페 & 전통 디저트 코스",
        "desc": "약과·화과자·전통차까지, 북촌 한옥 골목을 따라 즐기는 전통 디저트 완벽 가이드",
        "url": "https://search.naver.com/search.naver?query=%EB%B6%81%EC%B4%8C+%EC%A0%84%ED%86%B5%EC%B9%B4%ED%8E%98",
        "tag": "#북촌카페 #전통디저트",
        "likes": "4,430"
    },
    {
        "source": "인스타그램", "source_color": "#E1306C", "icon": "📸",
        "title": "서울 케이크 맛집 2025 트렌드 🎂",
        "desc": "2025 서울 케이크 씬의 모든 것 — 피스타치오 무스, 당근케이크, 르빵 밤식빵까지",
        "url": "https://www.instagram.com/explore/tags/%EC%84%9C%EC%9A%B8%EC%BC%80%EC%9D%B4%ED%81%AC/",
        "tag": "#서울케이크 #케이크맛집",
        "likes": "9,871"
    },
    {
        "source": "네이버 카페", "source_color": "#03C75A", "icon": "☕",
        "title": "이태원·한남 브런치 카페 총정리",
        "desc": "외국인도 즐겨 찾는 한남동 베이커리 카페! 아티장베이커스·타르틴 솔직 리뷰",
        "url": "https://cafe.naver.com/ArticleSearchList.nhn?search.query=%ED%95%9C%EB%82%A8%EB%8F%99+%EC%B9%B4%ED%8E%98",
        "tag": "#한남동카페 #이태원맛집",
        "likes": "2,990"
    },
    {
        "source": "인스타그램", "source_color": "#E1306C", "icon": "📸",
        "title": "마카롱 덕후의 서울 마카롱 투어 🫐",
        "desc": "서울 마카롱 맛집 8곳 — 쫀득한 꼬끄, 진한 가나슈, 어디가 제일 맛있을까?",
        "url": "https://www.instagram.com/explore/tags/%EB%A7%88%EC%B9%B4%EB%A1%B1%EB%A7%9B%EC%A7%91/",
        "tag": "#마카롱투어 #서울마카롱",
        "likes": "6,204"
    },
]

# ── 커뮤니티 초기 게시글 ─────────────────────────────────────────────────────
DEFAULT_POSTS = [
    {
        "nickname": "빵순이🥐", "date": "2025-06-10",
        "title": "베통 성수 웨이팅 팁 공유해요!",
        "content": "주말 오전 8시 30분에 가면 대기 없이 바로 들어갈 수 있어요. 퀸아망은 11시면 품절되니 일찍 가세요!",
        "place": "베통 성수 플래그십", "likes": 24
    },
    {
        "nickname": "카페탐험가", "date": "2025-06-08",
        "title": "어니언 안국 vs 어니언 성수 차이점?",
        "content": "두 지점 다 가봤는데요, 안국점은 한옥 느낌이라 분위기가 훨씬 특별해요. 성수점은 공간이 넓어서 앉기 편하고. 빵 메뉴는 비슷한데 안국점엔 계절 메뉴가 더 다양한 것 같아요!",
        "place": "어니언 안국", "likes": 18
    },
    {
        "nickname": "디저트코스", "date": "2025-06-05",
        "title": "연남동 반나절 디저트 코스 추천 🗺️",
        "content": "① 카페 레이어드 (스콘) → ② 이뮤 베이크샵 (타르트) → ③ 자연도소금빵 (소금빵) 순서로 가면 완벽한 반나절! 전부 도보 10분 거리예요.",
        "place": "카페 레이어드 연남", "likes": 41
    },
    {
        "nickname": "북촌산책자", "date": "2025-06-01",
        "title": "태극당 모나카아이스크림 꼭 드세요",
        "content": "1946년부터 영업한 서울 최고령 빵집이에요. 3300원짜리 모나카아이스크림이 레전드입니다. 겉은 바삭, 속은 부드러운 우유맛. 레트로 인테리어도 포토존이에요 📷",
        "place": "태극당", "likes": 56
    },
    {
        "nickname": "강남빵러버", "date": "2025-05-28",
        "title": "기욤 신사점 — 프랑스 정통 크루아상 후기",
        "content": "진짜 파리에서 먹는 것 같은 크루아상이에요. 버터향이 진하고 결이 살아있어요. 비싸지만 후회 없는 맛! 오전에 구운 게 더 맛있으니 오픈 직후 방문 추천.",
        "place": "기욤 신사", "likes": 33
    },
]

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    candidates = [
        "seoul_dessert_spots.csv",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "seoul_dessert_spots.csv"),
        os.path.join(os.getcwd(), "seoul_dessert_spots.csv"),
    ]
    csv_path = next((p for p in candidates if os.path.exists(p)), None)
    if not csv_path:
        st.error("⚠️ seoul_dessert_spots.csv 파일을 찾을 수 없습니다. 현재 경로: " + os.getcwd())
        return pd.DataFrame(columns=["name","type","city","district","area","rating","reviews","price","lat","lon","signature","img","hours","phone","naver_url"])

    raw = pd.read_csv(csv_path, encoding="utf-8-sig")
    raw.columns = [c.strip().lstrip('\ufeff') for c in raw.columns]
    raw["type"] = raw["category"].map(CATEGORY_MAP).fillna("카페·베이커리")
    df = raw.rename(columns={
        "latitude": "lat", "longitude": "lon",
        "signature_menu": "signature", "neighborhood": "area", "gu": "district",
    })
    df["city"]    = "서울"
    df["reviews"] = (df["rating"] * 180 - 700).clip(lower=50).astype(int)
    df["price"]   = "보통"
    if "img" not in df.columns:
        df["img"] = DEFAULT_IMG
    else:
        df["img"] = df["img"].fillna(DEFAULT_IMG)
    if "naver_url" not in df.columns:
        df["naver_url"] = df["name"].apply(
            lambda n: f"https://map.naver.com/v5/search/{urllib.parse.quote(str(n))}"
        )
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(4.3)
    df["lat"]    = pd.to_numeric(df["lat"],    errors="coerce")
    df["lon"]    = pd.to_numeric(df["lon"],    errors="coerce")
    df = df.dropna(subset=["lat", "lon"])
    return df

# ── 세션 스테이트 (커뮤니티 게시글) ─────────────────────────────────────────
if "posts" not in st.session_state:
    st.session_state.posts = list(DEFAULT_POSTS)
if "post_likes" not in st.session_state:
    st.session_state.post_likes = {i: p["likes"] for i, p in enumerate(DEFAULT_POSTS)}

df = load_data()

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍰 Sweet Spots Seoul")
    st.markdown("---")
    st.markdown("### 🔍 필터")

    all_districts = sorted(df["district"].unique().tolist()) if "district" in df.columns else []
    sel_districts = st.multiselect("🗺️ 구(區) 선택", options=all_districts, default=all_districts)

    available_areas = sorted(df[df["district"].isin(sel_districts)]["area"].unique().tolist()) if sel_districts else []
    sel_areas = st.multiselect("📍 동네 선택", options=available_areas, default=available_areas)

    all_types = sorted(df["type"].unique().tolist())
    sel_types = st.multiselect("🍰 카테고리", options=all_types, default=all_types)

    min_rating = st.slider("⭐ 최소 평점", 4.0, 5.0, 4.3, 0.1)
    search_query = st.text_input("🔎 가게명 검색", placeholder="예: 어니언, 베통, 프릳츠...")

    st.markdown("---")
    st.markdown("**📊 데이터 출처**")
    st.caption("Google Maps · Naver Place · 블루리본\n기준: 2025년")
    st.caption("🎓 2023313872 조연재")

# ── 필터 ──────────────────────────────────────────────────────────────────────
mask = (
    df["district"].isin(sel_districts) &
    df["area"].isin(sel_areas) &
    df["type"].isin(sel_types) &
    (df["rating"] >= min_rating)
)
if search_query.strip():
    mask &= df["name"].str.contains(search_query.strip(), case=False, na=False)
filtered = df[mask].reset_index(drop=True)

# ── 헤더 ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:0.5rem'>
  <div class='hero-title'>Sweet Spots Seoul 🍰</div>
  <div class='hero-sub'>서울 디저트 맛집 인터랙티브 지도 · 베이커리 · 카페 · 빵집 500+</div>
</div>
""", unsafe_allow_html=True)

avg_r  = filtered["rating"].mean() if len(filtered) else 0
top_row = filtered.loc[filtered["rating"].idxmax()] if len(filtered) else None
n_dist  = filtered["district"].nunique() if "district" in filtered.columns else 0

st.markdown(f"""
<div class='metric-row'>
  <div class='metric-card'><span class='val'>{len(filtered)}</span><span class='lbl'>맛집 수</span></div>
  <div class='metric-card'><span class='val'>⭐ {avg_r:.2f}</span><span class='lbl'>평균 평점</span></div>
  <div class='metric-card'><span class='val' style='font-size:1.2rem'>{top_row['name'] if top_row is not None else '-'}</span><span class='lbl'>최고 평점</span></div>
  <div class='metric-card'><span class='val'>{n_dist}</span><span class='lbl'>구(區) 수</span></div>
  <div class='metric-card'><span class='val'>{len(st.session_state.posts)}</span><span class='lbl'>커뮤니티 글</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── 탭 ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ 지도 & 차트",
    "🖼️ 갤러리",
    "📱 SNS 핫 피드",
    "💬 맛집 커뮤니티",
    "📊 데이터 분석",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — 지도 & 차트
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_map, col_bar = st.columns([1.4, 1])

    with col_map:
        st.markdown("#### 📍 서울 맛집 지도")
        if len(filtered):
            m = folium.Map(location=[37.5500, 126.9800], zoom_start=11, tiles="CartoDB positron")
            for _, row in filtered.iterrows():
                color = TYPE_COLORS.get(row["type"], "#999")
                emoji = TYPE_EMOJI.get(row["type"], "🍰")
                naver = row.get("naver_url", f"https://map.naver.com/v5/search/{urllib.parse.quote(row['name'])}")
                hours_str = f"🕐 {row['hours']}" if pd.notna(row.get("hours","")) and str(row.get("hours","")) not in ["","nan"] else ""
                popup_html = (
                    f"<b>{row['name']}</b><br>"
                    f"{emoji} {row['type']}<br>"
                    f"⭐ {row['rating']}<br>"
                    f"📍 {row['area']}, {row['district']}<br>"
                    f"🍴 {row['signature']}<br>"
                    f"{hours_str}<br>"
                    f"<a href='{naver}' target='_blank' style='color:#03C75A;font-weight:600'>📌 네이버 지도 보기</a>"
                )
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=7, color=color, fill=True,
                    fill_color=color, fill_opacity=0.85,
                    popup=folium.Popup(popup_html, max_width=240),
                    tooltip=f"{emoji} {row['name']} ({row['district']})"
                ).add_to(m)
            st_folium(m, width=None, height=430, returned_objects=[])
        else:
            st.info("필터 조건에 맞는 맛집이 없습니다.")

    with col_bar:
        st.markdown("#### ⭐ 카테고리별 평균 평점")
        if len(filtered):
            avg_type = filtered.groupby("type")["rating"].mean().reset_index().sort_values("rating", ascending=True)
            fig = px.bar(avg_type, x="rating", y="type", orientation="h",
                         color="type", color_discrete_map=TYPE_COLORS,
                         text=avg_type["rating"].apply(lambda x: f"{x:.2f}"), height=210)
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(showlegend=False, xaxis_range=[4.0, 5.2], xaxis_title="", yaxis_title="",
                              margin=dict(l=0, r=30, t=10, b=10), plot_bgcolor="white", paper_bgcolor="white")
            fig.update_xaxes(gridcolor="#F5EDE8")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🗺️ 구별 맛집 수 (TOP 12)")
        if len(filtered):
            dist_cnt = filtered.groupby("district").size().reset_index(name="count").sort_values("count", ascending=False).head(12)
            fig2 = px.bar(dist_cnt, x="district", y="count", color="count", text="count", height=230,
                          color_continuous_scale=["#F5E8E0", "#C0525A", "#3B1F2B"])
            fig2.update_traces(textposition="outside", marker_line_width=0)
            fig2.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_title="", yaxis_title="수",
                               margin=dict(l=0, r=10, t=10, b=10), plot_bgcolor="white", paper_bgcolor="white")
            fig2.update_xaxes(tickangle=-40, gridcolor="#F5EDE8")
            fig2.update_yaxes(gridcolor="#F5EDE8")
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 🥧 카테고리 분포")
        if len(filtered):
            dist_df = filtered.groupby("type").size().reset_index(name="count")
            fig3 = px.pie(dist_df, names="type", values="count", color="type",
                          color_discrete_map=TYPE_COLORS, hole=0.5, height=280)
            fig3.update_traces(textinfo="label+percent", pull=[0.03]*len(dist_df),
                               marker=dict(line=dict(color="white", width=2)))
            fig3.update_layout(showlegend=False, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="white")
            st.plotly_chart(fig3, use_container_width=True)
    with col4:
        st.markdown("#### 💬 평점 분포")
        if len(filtered):
            fig4 = px.histogram(filtered, x="rating", nbins=8, color_discrete_sequence=["#C0525A"],
                                height=280, labels={"rating":"평점"})
            fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                               margin=dict(l=0,r=0,t=10,b=20), bargap=0.1)
            fig4.update_xaxes(gridcolor="#F5EDE8")
            fig4.update_yaxes(gridcolor="#F5EDE8", title="가게 수")
            st.plotly_chart(fig4, use_container_width=True)

    st.markdown("#### 🌡️ 구 × 카테고리 평점 히트맵")
    if len(filtered) >= 3:
        pivot = filtered.pivot_table(values="rating", index="district", columns="type", aggfunc="mean")
        fig5 = go.Figure(data=go.Heatmap(
            z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
            colorscale=[[0,"#F5E8E0"],[0.5,"#E07B7B"],[1,"#3B1F2B"]],
            text=[[f"{v:.2f}" if not pd.isna(v) else "-" for v in row] for row in pivot.values],
            texttemplate="%{text}", showscale=True,
            hovertemplate="%{y} · %{x}<br>평점: %{text}<extra></extra>"
        ))
        fig5.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=10), plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — 갤러리 (개별 이미지 + 네이버 링크)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"#### 🖼️ 서울 디저트 맛집 갤러리 &nbsp;<span style='font-size:0.85rem;color:#9B7B87;font-weight:400'>{len(filtered)}곳</span>", unsafe_allow_html=True)
    st.caption("카드를 클릭하면 네이버 지도로 연결돼요.")

    # 맛집 추가 버튼 (상단)
    with st.expander("➕ 내가 찾은 맛집 추가하기", expanded=False):
        with st.form("add_place_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            new_name  = c1.text_input("가게 이름 *", placeholder="예: 어니언 성수")
            new_cat   = c2.selectbox("카테고리 *", ["카페·베이커리","베이커리","카페","카페·디저트","베이커리·디저트","디저트","전통·카페"])
            c3, c4 = st.columns(2)
            new_dist  = c3.selectbox("구 *", sorted(df["district"].unique().tolist()))
            new_area  = c4.text_input("동네 *", placeholder="예: 성수동")
            new_addr  = st.text_input("주소 *", placeholder="예: 서울특별시 성동구 아차산로9길 8")
            c5, c6 = st.columns(2)
            new_sig   = c5.text_input("대표 메뉴", placeholder="예: 크루아상, 소금빵")
            new_hours = c6.text_input("영업시간", placeholder="예: 09:00-21:00")
            new_img   = st.text_input("이미지 URL (선택)", placeholder="https://...")
            new_note  = st.text_area("한 줄 소개 / 방문 후기", placeholder="이 맛집을 추천하는 이유를 적어주세요!", height=80)
            submitted = st.form_submit_button("✅ 맛집 등록하기", use_container_width=True)

            if submitted:
                if not new_name or not new_addr:
                    st.warning("가게 이름과 주소는 필수입니다.")
                else:
                    naver_link = f"https://map.naver.com/v5/search/{urllib.parse.quote(new_name + ' ' + new_dist)}"
                    new_row = {
                        "name": new_name, "type": new_cat, "district": new_dist,
                        "area": new_area, "address": new_addr,
                        "signature": new_sig, "hours": new_hours,
                        "rating": 4.5, "reviews": 0,
                        "lat": 37.5500, "lon": 126.9800,
                        "img": new_img if new_img else DEFAULT_IMG,
                        "naver_url": naver_link, "city": "서울", "price": "보통",
                    }
                    new_df = pd.DataFrame([new_row])
                    # session_state에 추가 (캐시 우회)
                    if "user_places" not in st.session_state:
                        st.session_state.user_places = []
                    st.session_state.user_places.append(new_row)
                    # 커뮤니티에도 자동 등록
                    st.session_state.posts.insert(0, {
                        "nickname": "맛집탐험가 🗺️", "date": datetime.now().strftime("%Y-%m-%d"),
                        "title": f"[새 맛집] {new_name} 등록했어요!",
                        "content": new_note if new_note else f"{new_addr}에 위치한 {new_cat} 맛집이에요. 대표메뉴: {new_sig}",
                        "place": new_name, "likes": 0
                    })
                    st.success(f"🎉 '{new_name}' 등록 완료! 커뮤니티에도 자동 공유됐어요.")
                    st.rerun()

    # 사용자 추가 맛집 먼저 표시
    display_rows = []
    if "user_places" in st.session_state and st.session_state.user_places:
        for p in st.session_state.user_places:
            display_rows.append(p)

    # 필터된 데이터
    for _, row in filtered.head(60).iterrows():
        display_rows.append(row.to_dict())

    if not display_rows:
        st.info("필터 조건에 맞는 맛집이 없습니다.")
    else:
        cols = st.columns(3)
        for i, row in enumerate(display_rows[:63]):
            with cols[i % 3]:
                color  = TYPE_COLORS.get(row.get("type",""), "#999")
                emoji  = TYPE_EMOJI.get(row.get("type",""), "🍰")
                naver  = row.get("naver_url") or f"https://map.naver.com/v5/search/{urllib.parse.quote(str(row.get('name','')))}"
                img    = row.get("img") or DEFAULT_IMG
                hours_str = str(row.get("hours",""))
                hours_info = f"🕐 {hours_str}" if hours_str and hours_str != "nan" else ""
                is_user = row.get("reviews") == 0
                user_badge = "<span style='background:#FFF0E0;color:#E07B7B;font-size:0.68rem;padding:1px 6px;border-radius:10px;margin-left:4px'>🆕 새 맛집</span>" if is_user else ""

                st.markdown(f"""
                <a href="{naver}" target="_blank" style="text-decoration:none;">
                  <div class='cafe-card'>
                    <img src='{img}' style='width:100%;height:150px;object-fit:cover;' alt='{row.get("name","")}'>
                    <div class='cafe-body'>
                      <div class='cafe-name'>{row.get("name","")}{user_badge}</div>
                      <span class='cafe-tag' style='background:{color}22;color:{color}'>{emoji} {row.get("type","")}</span>
                      <div class='cafe-rating'>⭐ {row.get("rating","-")}</div>
                      <div class='cafe-sig'>🍴 {row.get("signature","")}</div>
                      <div style='font-size:0.78rem;color:#C0A090;margin-top:4px'>
                        📍 {row.get("area","")}, {row.get("district","")}<br>{hours_info}
                      </div>
                    </div>
                  </div>
                </a>
                """, unsafe_allow_html=True)

        if len(filtered) > 60:
            st.caption(f"📌 상위 60곳만 표시 중 (전체 {len(filtered)}곳)")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SNS 핫 피드
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### 📱 SNS 핫 피드 — 지금 화제인 디저트 맛집")
    st.caption("인스타그램 · 네이버 블로그 · 네이버 카페에서 화제인 서울 디저트 콘텐츠를 모아봤어요.")

    # 플랫폼 필터
    platforms = st.multiselect(
        "플랫폼 선택", ["인스타그램", "네이버 블로그", "네이버 카페"],
        default=["인스타그램", "네이버 블로그", "네이버 카페"]
    )
    feeds_to_show = [f for f in SNS_FEEDS if f["source"] in platforms]

    if not feeds_to_show:
        st.info("선택된 플랫폼의 피드가 없습니다.")
    else:
        col_l, col_r = st.columns(2)
        for i, feed in enumerate(feeds_to_show):
            with (col_l if i % 2 == 0 else col_r):
                st.markdown(f"""
                <a href="{feed['url']}" target="_blank" style="text-decoration:none;color:inherit;">
                  <div class='sns-card'>
                    <div style='display:flex;align-items:center;gap:8px;margin-bottom:8px'>
                      <span style='font-size:1.3rem'>{feed['icon']}</span>
                      <span class='sns-source' style='background:{feed["source_color"]}18;color:{feed["source_color"]}'>{feed['source']}</span>
                      <span style='margin-left:auto;font-size:0.78rem;color:#C0A090'>❤️ {feed['likes']}</span>
                    </div>
                    <div style='font-weight:600;color:#3B1F2B;font-size:0.92rem;margin-bottom:5px'>{feed['title']}</div>
                    <div style='font-size:0.82rem;color:#7B6070;line-height:1.5'>{feed['desc']}</div>
                    <div style='margin-top:8px;font-size:0.75rem;color:#9B7B87'>{feed['tag']}</div>
                    <div style='margin-top:10px;font-size:0.78rem;color:#03C75A;font-weight:600'>🔗 바로가기 →</div>
                  </div>
                </a>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🔗 빠른 검색 링크")
    q_cols = st.columns(4)
    quick_links = [
        ("📸 인스타 #성수베이커리", "https://www.instagram.com/explore/tags/%EC%84%B1%EC%88%98%EB%B2%A0%EC%9D%B4%EC%BB%A4%EB%A6%AC/"),
        ("📝 네이버 서울카페 리뷰", "https://search.naver.com/search.naver?query=%EC%84%9C%EC%9A%B8+%EB%94%94%EC%A0%80%ED%8A%B8+%EC%B9%B4%ED%8E%98+%EC%B6%94%EC%B2%9C"),
        ("☕ 다이닝코드 서울빵집", "https://www.diningcode.com/list.dc?query=%EC%84%9C%EC%9A%B8+%EB%B2%A0%EC%9D%B4%EC%BB%A4%EB%A6%AC"),
        ("🏅 망고플레이트 카페", "https://www.mangoplate.com/search/%EC%84%9C%EC%9A%B8%20%EB%94%94%EC%A0%80%ED%8A%B8"),
    ]
    for col, (label, link) in zip(q_cols, quick_links):
        col.markdown(f"<a href='{link}' target='_blank' style='display:block;background:white;border:1px solid #F0E6E0;border-radius:10px;padding:10px;text-align:center;text-decoration:none;color:#3B1F2B;font-size:0.82rem;font-weight:500'>{label}</a>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — 커뮤니티
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### 💬 맛집 추천 커뮤니티")
    st.caption("서울 디저트 맛집 정보를 함께 나눠요! 방문 후기, 웨이팅 팁, 추천 코스를 공유해주세요 🍰")

    # 글 작성
    with st.expander("✏️ 글 쓰기", expanded=False):
        with st.form("community_form", clear_on_submit=True):
            cb1, cb2 = st.columns(2)
            c_nick  = cb1.text_input("닉네임 *", placeholder="예: 빵순이🥐")
            c_place = cb2.text_input("관련 맛집", placeholder="예: 어니언 성수")
            c_title = st.text_input("제목 *", placeholder="예: 베통 성수 웨이팅 팁 공유해요!")
            c_body  = st.text_area("내용 *", placeholder="방문 후기, 추천 메뉴, 꿀팁 등을 자유롭게 적어주세요!", height=120)
            post_btn = st.form_submit_button("📮 게시하기", use_container_width=True)
            if post_btn:
                if not c_nick or not c_title or not c_body:
                    st.warning("닉네임, 제목, 내용은 필수입니다.")
                else:
                    new_post = {
                        "nickname": c_nick,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "title": c_title,
                        "content": c_body,
                        "place": c_place,
                        "likes": 0,
                    }
                    st.session_state.posts.insert(0, new_post)
                    n = len(st.session_state.posts) - 1
                    st.session_state.post_likes[n] = 0
                    st.success("게시글이 등록됐어요! 🎉")
                    st.rerun()

    st.markdown("---")

    # 정렬
    sort_opt = st.radio("정렬", ["최신순", "좋아요순"], horizontal=True, label_visibility="collapsed")
    posts = list(enumerate(st.session_state.posts))
    if sort_opt == "좋아요순":
        posts = sorted(posts, key=lambda x: st.session_state.post_likes.get(x[0], x[1]["likes"]), reverse=True)

    for idx, (orig_i, post) in enumerate(posts):
        current_likes = st.session_state.post_likes.get(orig_i, post["likes"])
        with st.container():
            col_info, col_like = st.columns([6, 1])
            with col_info:
                place_tag = f"<span style='background:#FFF0F5;color:#C0525A;font-size:0.72rem;padding:2px 8px;border-radius:12px;margin-left:6px'>📍 {post['place']}</span>" if post.get("place") else ""
                # 맛집명 클릭시 네이버 연결
                place_link = ""
                if post.get("place"):
                    nurl = f"https://map.naver.com/v5/search/{urllib.parse.quote(post['place'])}"
                    place_link = f"<a href='{nurl}' target='_blank' style='color:#03C75A;font-size:0.72rem;margin-left:6px'>📌 네이버 지도</a>"
                st.markdown(f"""
                <div class='comm-card'>
                  <div style='display:flex;align-items:center;gap:6px;margin-bottom:6px'>
                    <span style='font-weight:600;color:#3B1F2B'>{post['nickname']}</span>
                    <span style='color:#C0A090;font-size:0.75rem'>{post['date']}</span>
                    {place_tag}{place_link}
                  </div>
                  <div style='font-weight:600;color:#3B1F2B;font-size:0.92rem;margin-bottom:6px'>{post['title']}</div>
                  <div style='font-size:0.85rem;color:#7B6070;line-height:1.6'>{post['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_like:
                st.write("")
                st.write("")
                if st.button(f"❤️ {current_likes}", key=f"like_{orig_i}_{idx}"):
                    st.session_state.post_likes[orig_i] = current_likes + 1
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — 데이터 분석
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("#### 🏅 평점 TOP 20 랭킹")
    if len(filtered):
        rank_df = filtered.sort_values("rating", ascending=False).head(20).reset_index(drop=True)
        fig6 = px.bar(rank_df, x="name", y="rating", color="type", color_discrete_map=TYPE_COLORS,
                      text=rank_df["rating"].apply(lambda x: f"{x:.1f}"), height=340,
                      hover_data={"district": True, "area": True, "signature": True})
        fig6.update_traces(textposition="outside", marker_line_width=0)
        fig6.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           margin=dict(l=0,r=0,t=10,b=90), yaxis_range=[4.0,5.4],
                           xaxis_tickangle=-40, showlegend=True, legend=dict(orientation="h",y=-0.55))
        fig6.update_yaxes(gridcolor="#F5EDE8")
        st.plotly_chart(fig6, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🗺️ 구별 평균 평점")
        if len(filtered):
            gu_avg = filtered.groupby("district")["rating"].mean().reset_index().sort_values("rating", ascending=True)
            fig7 = px.bar(gu_avg, x="rating", y="district", orientation="h", color="rating",
                          color_continuous_scale=["#F5E8E0","#C0525A","#3B1F2B"],
                          text=gu_avg["rating"].apply(lambda x: f"{x:.2f}"), height=400)
            fig7.update_traces(textposition="outside")
            fig7.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_range=[4.0,5.0],
                               xaxis_title="", yaxis_title="",
                               margin=dict(l=0,r=40,t=10,b=10), plot_bgcolor="white", paper_bgcolor="white")
            fig7.update_xaxes(gridcolor="#F5EDE8")
            st.plotly_chart(fig7, use_container_width=True)

    with col_b:
        st.markdown("#### 💎 숨은 맛집 (고평점)")
        if len(filtered):
            gems = filtered[filtered["rating"] >= 4.5].sort_values("rating", ascending=False).head(15)
            for _, g in gems.iterrows():
                c     = TYPE_COLORS.get(g["type"], "#999")
                emoji = TYPE_EMOJI.get(g["type"], "🍰")
                naver = g.get("naver_url", f"https://map.naver.com/v5/search/{urllib.parse.quote(str(g['name']))}")
                st.markdown(f"""
                <a href="{naver}" target="_blank" style="text-decoration:none;">
                  <div style='background:white;border-radius:12px;padding:10px 14px;margin-bottom:7px;
                              border-left:4px solid {c};border:1px solid #F0E6E0;'>
                    <b style='color:#3B1F2B'>{g['name']}</b>
                    <span style='background:{c}22;color:{c};border-radius:20px;padding:2px 8px;
                                 font-size:0.72rem;margin-left:6px;'>{emoji} {g['type']}</span>
                    <span style='float:right;color:#C0525A;font-weight:500'>⭐ {g['rating']}</span>
                    <div style='font-size:0.8rem;color:#9B7B87;margin-top:3px'>
                      {g['area']}, {g['district']} · {g['signature']}
                    </div>
                  </div>
                </a>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div class='footer'>
  🎓 성균관대학교 미술학과 · Data Hub Project 2025 · 2023313872 조연재<br>
  Built with Streamlit · Plotly · Folium &nbsp;|&nbsp; AI assisted by Claude (Anthropic)
</div>
""", unsafe_allow_html=True)
