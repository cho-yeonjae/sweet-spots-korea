import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Sweet Spots Korea 🍰",
    page_icon="🍰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background-color: #FFF9F5; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* Header */
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: #3B1F2B;
    line-height: 1.15;
    margin: 0;
}
.hero-sub {
    font-size: 1rem;
    color: #9B7B87;
    margin-top: 6px;
    font-weight: 300;
}

/* Metric cards */
.metric-row { display: flex; gap: 12px; margin: 1.2rem 0; flex-wrap: wrap; }
.metric-card {
    background: white;
    border-radius: 14px;
    padding: 16px 20px;
    flex: 1;
    min-width: 130px;
    border: 1px solid #F0E6E0;
    box-shadow: 0 2px 8px rgba(59,31,43,0.06);
}
.metric-card .val {
    font-family: 'DM Serif Display', serif;
    font-size: 1.9rem;
    color: #C0525A;
    display: block;
}
.metric-card .lbl {
    font-size: 0.75rem;
    color: #9B7B87;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Type badge */
.type-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    margin: 2px;
}

/* Section header */
.section-hd {
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    color: #3B1F2B;
    margin: 0 0 0.6rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #3B1F2B !important;
}
section[data-testid="stSidebar"] * { color: #F5E8E0 !important; }
section[data-testid="stSidebar"] .stSlider > div > div > div { background: #C0525A !important; }

/* Divider */
hr { border-color: #F0E6E0; margin: 1.2rem 0; }

/* Footer */
.footer { text-align: center; font-size: 0.78rem; color: #C0A090; padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    rows = [
        # 케이크·카페
        dict(name="Upper and Under",       type="케이크·카페", city="서울", area="강남",   rating=4.8, reviews=624,  price="보통",  lat=37.5027, lon=127.0277, signature="딸기 치즈파이"),
        dict(name="Notre Don",             type="케이크·카페", city="서울", area="성동",   rating=4.9, reviews=204,  price="보통",  lat=37.5473, lon=127.0400, signature="피스타치오 무스케이크"),
        dict(name="Teddy Beurre House",    type="케이크·카페", city="서울", area="용산",   rating=4.8, reviews=1709, price="보통",  lat=37.5317, lon=126.9725, signature="망고 타르트"),
        dict(name="Nukeunog",              type="케이크·카페", city="서울", area="마포",   rating=5.0, reviews=450,  price="보통",  lat=37.5625, lon=126.9258, signature="당근 슈크림"),
        dict(name="보노베리 본점",         type="케이크·카페", city="부산", area="금정구", rating=4.9, reviews=340,  price="보통",  lat=35.2310, lon=129.0888, signature="레몬라임 타르트"),
        dict(name="올림프케이크 해운대",   type="케이크·카페", city="부산", area="해운대", rating=4.5, reviews=280,  price="보통",  lat=35.1599, lon=129.1527, signature="글루텐프리 케이크"),
        # 전통 한과
        dict(name="신라당 익선",           type="전통 한과",   city="서울", area="종로",   rating=4.9, reviews=444,  price="보통",  lat=37.5738, lon=126.9899, signature="주악, 강정"),
        dict(name="한과미의식 안녕",       type="전통 한과",   city="서울", area="종로",   rating=5.0, reviews=423,  price="보통",  lat=37.5744, lon=126.9840, signature="약과, 다식 선물세트"),
        dict(name="Gangjeong House",       type="전통 한과",   city="서울", area="강남",   rating=4.4, reviews=188,  price="보통",  lat=37.5187, lon=127.0486, signature="개성약과, 쌍화차"),
        dict(name="Aon 아온",              type="전통 한과",   city="서울", area="종로",   rating=4.9, reviews=824,  price="보통",  lat=37.5778, lon=126.9858, signature="딸기·밤·고구마 모찌"),
        # 빙수
        dict(name="삼청빙수",              type="빙수",        city="서울", area="종로",   rating=4.5, reviews=803,  price="저렴",  lat=37.5829, lon=126.9819, signature="흑임자 빙수"),
        dict(name="장코방",                type="빙수",        city="서울", area="서초",   rating=4.5, reviews=649,  price="저렴",  lat=37.4983, lon=127.0238, signature="팥빙수, 단팥죽"),
        dict(name="시베리안 빙수킹",       type="빙수",        city="서울", area="강남",   rating=5.0, reviews=120,  price="저렴",  lat=37.5052, lon=127.0440, signature="망고 빙수 대용량"),
        # 마카롱
        dict(name="로얄마카롱",            type="마카롱",      city="서울", area="강남",   rating=4.5, reviews=660,  price="보통",  lat=37.5022, lon=127.0354, signature="얼그레이, 살티드카라멜"),
        dict(name="Rare Macaron Gyodae",   type="마카롱",      city="서울", area="서초",   rating=4.4, reviews=105,  price="보통",  lat=37.4892, lon=127.0116, signature="오픈키친 마카롱"),
        # 타르트
        dict(name="Tarte Lab Seoul",       type="타르트",      city="서울", area="마포",   rating=4.7, reviews=530,  price="보통",  lat=37.5590, lon=126.9220, signature="레몬 타르트, 말차 타르트"),
        dict(name="파파타르트 합정",       type="타르트",      city="서울", area="마포",   rating=4.6, reviews=390,  price="저렴",  lat=37.5501, lon=126.9145, signature="에그타르트, 딸기 타르트"),
    ]
    return pd.DataFrame(rows)

df = load_data()

TYPE_COLORS = {
    "케이크·카페": "#E07B7B",
    "전통 한과":   "#7BADE0",
    "빙수":        "#7BCEC0",
    "마카롱":      "#C49DE0",
    "타르트":      "#E0C07B",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍰 Sweet Spots Korea")
    st.markdown("---")
    st.markdown("### 필터")

    sel_types = st.multiselect(
        "디저트 종류",
        options=df["type"].unique().tolist(),
        default=df["type"].unique().tolist()
    )
    sel_cities = st.multiselect(
        "도시",
        options=df["city"].unique().tolist(),
        default=df["city"].unique().tolist()
    )
    min_rating = st.slider("최소 평점", 4.0, 5.0, 4.3, 0.1)
    price_opt  = st.multiselect(
        "가격대",
        options=["저렴", "보통", "비쌈"],
        default=["저렴", "보통", "비쌈"]
    )
    st.markdown("---")
    st.markdown("**데이터 출처**")
    st.caption("Google Maps · Naver Place\n기준: 2025년")
    st.caption("📌 PRD: 2023313872 조연재")

filtered = df[
    df["type"].isin(sel_types) &
    df["city"].isin(sel_cities) &
    (df["rating"] >= min_rating) &
    df["price"].isin(price_opt)
].reset_index(drop=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:0.5rem'>
  <div class='hero-title'>Sweet Spots Korea 🍰</div>
  <div class='hero-sub'>국내 디저트 종류별 맛집 인터랙티브 지도 · Interactive Dessert Cafe Map & Analytics</div>
</div>
""", unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────────────────
avg_r   = filtered["rating"].mean() if len(filtered) else 0
top_row = filtered.loc[filtered["rating"].idxmax()] if len(filtered) else None
total_r = filtered["reviews"].sum()

st.markdown(f"""
<div class='metric-row'>
  <div class='metric-card'><span class='val'>{len(filtered)}</span><span class='lbl'>맛집 수</span></div>
  <div class='metric-card'><span class='val'>⭐ {avg_r:.2f}</span><span class='lbl'>평균 평점</span></div>
  <div class='metric-card'><span class='val' style='font-size:1.3rem'>{top_row['name'] if top_row is not None else '-'}</span><span class='lbl'>최고 평점 맛집</span></div>
  <div class='metric-card'><span class='val'>{total_r:,}</span><span class='lbl'>총 리뷰 수</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Row 1: Map + Bar ──────────────────────────────────────────────────────────
col_map, col_bar = st.columns([1.4, 1])

with col_map:
    st.markdown("<div class='section-hd'>📍 맛집 지도</div>", unsafe_allow_html=True)

    m = folium.Map(
        location=[36.8, 127.8],
        zoom_start=7,
        tiles="CartoDB positron",
        prefer_canvas=True
    )

    for _, row in filtered.iterrows():
        color = TYPE_COLORS.get(row["type"], "#999")
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=9,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(
                f"""<b>{row['name']}</b><br>
                종류: {row['type']}<br>
                평점: ⭐ {row['rating']}<br>
                대표 메뉴: {row['signature']}<br>
                가격대: {row['price']}""",
                max_width=220
            ),
            tooltip=f"{row['name']} ({row['type']})"
        ).add_to(m)

    st_folium(m, width=None, height=380, returned_objects=[])

with col_bar:
    st.markdown("<div class='section-hd'>⭐ 종류별 평균 평점</div>", unsafe_allow_html=True)
    if len(filtered):
        avg_type = (
            filtered.groupby("type")["rating"]
            .mean().reset_index()
            .sort_values("rating", ascending=True)
        )
        fig_bar = px.bar(
            avg_type, x="rating", y="type", orientation="h",
            color="type",
            color_discrete_map=TYPE_COLORS,
            text=avg_type["rating"].apply(lambda x: f"{x:.2f}"),
            height=360,
        )
        fig_bar.update_traces(textposition="outside", marker_line_width=0)
        fig_bar.update_layout(
            showlegend=False,
            xaxis_range=[4.0, 5.2],
            xaxis_title="평균 평점",
            yaxis_title="",
            margin=dict(l=0, r=30, t=10, b=20),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="DM Sans, sans-serif", size=12),
        )
        fig_bar.update_xaxes(gridcolor="#F5EDE8", showline=False)
        fig_bar.update_yaxes(showline=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("필터 결과가 없습니다.")

st.markdown("---")

# ── Row 2: Donut + Scatter ────────────────────────────────────────────────────
col_donut, col_scatter = st.columns(2)

with col_donut:
    st.markdown("<div class='section-hd'>🥧 종류별 분포</div>", unsafe_allow_html=True)
    if len(filtered):
        dist = filtered.groupby("type").size().reset_index(name="count")
        fig_pie = px.pie(
            dist, names="type", values="count",
            color="type", color_discrete_map=TYPE_COLORS,
            hole=0.52, height=300,
        )
        fig_pie.update_traces(
            textinfo="label+percent",
            pull=[0.03] * len(dist),
            marker=dict(line=dict(color="white", width=2))
        )
        fig_pie.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="white",
            font=dict(family="DM Sans, sans-serif", size=12),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with col_scatter:
    st.markdown("<div class='section-hd'>💬 리뷰 수 vs 평점 (숨은 맛집 발견!)</div>", unsafe_allow_html=True)
    if len(filtered):
        fig_sc = px.scatter(
            filtered, x="reviews", y="rating",
            color="type", color_discrete_map=TYPE_COLORS,
            hover_name="name",
            size="reviews", size_max=28,
            height=300,
            labels={"reviews": "리뷰 수", "rating": "평점", "type": "종류"},
        )
        fig_sc.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0, r=0, t=10, b=20),
            yaxis_range=[4.2, 5.15],
            legend=dict(title="종류", orientation="h", y=-0.25),
            font=dict(family="DM Sans, sans-serif", size=12),
        )
        fig_sc.update_xaxes(gridcolor="#F5EDE8")
        fig_sc.update_yaxes(gridcolor="#F5EDE8")
        st.plotly_chart(fig_sc, use_container_width=True)

st.markdown("---")

# ── Row 3: Heatmap + Ranking bar ─────────────────────────────────────────────
col_heat, col_rank = st.columns(2)

with col_heat:
    st.markdown("<div class='section-hd'>🗺️ 도시 × 종류 평점 히트맵</div>", unsafe_allow_html=True)
    if len(filtered) >= 2:
        pivot = filtered.pivot_table(values="rating", index="city", columns="type", aggfunc="mean")
        fig_heat = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0,"#F5E8E0"],[0.5,"#E07B7B"],[1,"#3B1F2B"]],
            text=[[f"{v:.2f}" if not pd.isna(v) else "-" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            showscale=False,
            hovertemplate="%{y} · %{x}<br>평점: %{text}<extra></extra>"
        ))
        fig_heat.update_layout(
            height=260,
            margin=dict(l=0, r=0, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="DM Sans, sans-serif", size=12),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

with col_rank:
    st.markdown("<div class='section-hd'>🏅 전체 평점 랭킹</div>", unsafe_allow_html=True)
    if len(filtered):
        rank_df = filtered.sort_values("rating", ascending=False).head(10).reset_index(drop=True)
        fig_rank = px.bar(
            rank_df, x="name", y="rating",
            color="type", color_discrete_map=TYPE_COLORS,
            text=rank_df["rating"].apply(lambda x: f"{x:.1f}"),
            height=260,
            labels={"name": "", "rating": "평점", "type": "종류"},
        )
        fig_rank.update_traces(textposition="outside", marker_line_width=0)
        fig_rank.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0, r=0, t=10, b=60),
            yaxis_range=[4.0, 5.3],
            xaxis_tickangle=-35,
            showlegend=False,
            font=dict(family="DM Sans, sans-serif", size=11),
        )
        fig_rank.update_yaxes(gridcolor="#F5EDE8")
        st.plotly_chart(fig_rank, use_container_width=True)

st.markdown("---")

# ── Hidden Gems ───────────────────────────────────────────────────────────────
st.markdown("<div class='section-hd'>💎 숨은 맛집 (Hidden Gems) — 높은 평점, 적은 리뷰</div>", unsafe_allow_html=True)
if len(filtered):
    median_reviews = filtered["reviews"].median()
    gems = filtered[(filtered["reviews"] < median_reviews) & (filtered["rating"] >= 4.7)].sort_values("rating", ascending=False)
    if len(gems):
        for _, g in gems.iterrows():
            c = TYPE_COLORS.get(g["type"], "#999")
            st.markdown(f"""
            <div style='background:white;border-radius:12px;padding:12px 16px;margin-bottom:8px;
                        border-left:4px solid {c};border:1px solid #F0E6E0;'>
              <b style='color:#3B1F2B'>{g['name']}</b>
              <span style='background:{c}22;color:{c};border-radius:20px;padding:2px 8px;
                           font-size:0.75rem;margin-left:8px;'>{g['type']}</span>
              <span style='float:right;color:#C0525A;font-weight:500'>⭐ {g['rating']}</span>
              <div style='font-size:0.82rem;color:#9B7B87;margin-top:4px'>
                {g['area']}, {g['city']} · {g['signature']} · 리뷰 {g['reviews']:,}개
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("현재 필터 조건에서 숨은 맛집이 없습니다.")

st.markdown("---")

# ── Data Table + CSV Export ───────────────────────────────────────────────────
st.markdown("<div class='section-hd'>📋 전체 데이터 테이블</div>", unsafe_allow_html=True)
show_df = filtered[["name","type","city","area","rating","reviews","price","signature"]].rename(columns={
    "name":"가게명","type":"종류","city":"도시","area":"지역",
    "rating":"평점","reviews":"리뷰수","price":"가격대","signature":"대표 메뉴"
})
st.dataframe(show_df, use_container_width=True, hide_index=True)

csv = show_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="⬇️ CSV로 다운로드",
    data=csv,
    file_name="sweet_spots_korea.csv",
    mime="text/csv"
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<div class='footer'>
  🎓 성균관대학교 미술학과 · Data Hub Project 2025 · 2023313872 조연재<br>
  Built with Streamlit · Plotly · Folium · Google Maps Data<br>
  AI assisted by Claude (Anthropic)
</div>
""", unsafe_allow_html=True)
