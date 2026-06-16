import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import os

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
.cafe-card { background:white; border-radius:16px; padding:0; border:1px solid #F0E6E0; overflow:hidden; margin-bottom:12px; }
.cafe-body { padding:12px 14px; }
.cafe-name { font-weight:500; font-size:0.95rem; color:#3B1F2B; margin-bottom:4px; }
.cafe-tag { display:inline-block; padding:2px 8px; border-radius:20px; font-size:0.72rem; font-weight:500; margin-bottom:6px; }
.cafe-sig { font-size:0.8rem; color:#9B7B87; }
.cafe-rating { font-size:0.85rem; color:#C0525A; font-weight:500; }
section[data-testid="stSidebar"] { background:#3B1F2B !important; }
section[data-testid="stSidebar"] * { color:#F5E8E0 !important; }
hr { border-color:#F0E6E0; margin:1.2rem 0; }
.footer { text-align:center; font-size:0.78rem; color:#C0A090; padding-top:1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── 카테고리 매핑 ────────────────────────────────────────────────────────────
# CSV의 category 값을 앱 표시용 type으로 매핑
CATEGORY_MAP = {
    "카페":           "카페",
    "베이커리":       "베이커리",
    "카페/베이커리":  "카페·베이커리",
    "베이커리/카페":  "카페·베이커리",
    "카페/디저트":    "카페·디저트",
    "베이커리/디저트":"베이커리·디저트",
    "디저트":         "디저트",
    "카페/전통":      "전통·카페",
}

TYPE_COLORS = {
    "카페":           "#F4A460",
    "베이커리":       "#E07B7B",
    "카페·베이커리":  "#C0525A",
    "카페·디저트":    "#C49DE0",
    "베이커리·디저트":"#E0C07B",
    "디저트":         "#7BCEC0",
    "전통·카페":      "#7BADE0",
}

TYPE_EMOJI = {
    "카페":           "☕",
    "베이커리":       "🥐",
    "카페·베이커리":  "🥐",
    "카페·디저트":    "🍰",
    "베이커리·디저트":"🎂",
    "디저트":         "🍮",
    "전통·카페":      "🍡",
}

# 구별 대표 동네 이미지 (Unsplash)
AREA_IMAGES = {
    "성동구": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&q=80",
    "마포구": "https://images.unsplash.com/photo-1586444248902-2f64eddc8df5?w=400&q=80",
    "강남구": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&q=80",
    "용산구": "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400&q=80",
    "종로구": "https://images.unsplash.com/photo-1611270629569-8b357cb88da9?w=400&q=80",
    "중구":   "https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=400&q=80",
}
DEFAULT_IMG = "https://images.unsplash.com/photo-1519915028121-7d3463d20b13?w=400&q=80"

# ── 데이터 로드 ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # CSV 파일 경로: 앱과 같은 디렉토리에 seoul_dessert_spots.csv 배치
    csv_path = os.path.join(os.path.dirname(__file__), "seoul_dessert_spots.csv")

    if os.path.exists(csv_path):
        raw = pd.read_csv(csv_path, encoding="utf-8-sig")

        # 컬럼 이름 정규화
        raw.columns = [c.strip().lstrip('\ufeff') for c in raw.columns]

        # 타입 매핑
        raw["type"] = raw["category"].map(CATEGORY_MAP).fillna("카페·베이커리")

        # 앱 기존 컬럼명에 맞게 rename
        df = raw.rename(columns={
            "latitude":       "lat",
            "longitude":      "lon",
            "signature_menu": "signature",
            "neighborhood":   "area",
            "gu":             "district",
        })

        # 추가 컬럼 생성 (앱에서 필요한 항목)
        df["city"]    = "서울"
        df["reviews"] = (df["rating"] * 180 - 700).clip(lower=50).astype(int)  # 평점 기반 추정 리뷰수
        df["price"]   = "보통"  # 기본값; 추후 CSV에 price 컬럼 추가 가능
        df["img"]     = df["district"].map(AREA_IMAGES).fillna(DEFAULT_IMG)

        # 결측치 처리
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(4.3)
        df["lat"]    = pd.to_numeric(df["lat"],    errors="coerce")
        df["lon"]    = pd.to_numeric(df["lon"],    errors="coerce")
        df = df.dropna(subset=["lat", "lon"])

        return df

    else:
        # CSV 없을 때 샘플 데이터 fallback
        st.warning("⚠️ seoul_dessert_spots.csv 파일을 앱과 같은 폴더에 넣어주세요.")
        return pd.DataFrame(columns=["name","type","city","district","area","rating","reviews","price","lat","lon","signature","img","hours","phone"])


df = load_data()

# ── 사이드바 ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍰 Sweet Spots Seoul")
    st.markdown("---")
    st.markdown("### 🔍 필터")

    # 구(district) 필터 — 기존 city 필터를 서울 구 단위로 교체
    all_districts = sorted(df["district"].unique().tolist()) if "district" in df.columns else []
    sel_districts = st.multiselect("🗺️ 구(區) 선택", options=all_districts, default=all_districts,
                                   help="원하는 구를 선택하세요")

    # 동네(area) 필터 — 선택된 구에 속하는 동네만 표시
    available_areas = sorted(
        df[df["district"].isin(sel_districts)]["area"].unique().tolist()
    ) if sel_districts else []
    sel_areas = st.multiselect("📍 동네 선택", options=available_areas, default=available_areas)

    # 카테고리 필터
    all_types = sorted(df["type"].unique().tolist())
    sel_types = st.multiselect("🍰 카테고리", options=all_types, default=all_types)

    # 평점 필터
    min_rating = st.slider("⭐ 최소 평점", 4.0, 5.0, 4.3, 0.1)

    # 영업시간 검색
    search_query = st.text_input("🔎 가게명 검색", placeholder="예: 어니언, 베통, 프릳츠...")

    st.markdown("---")
    st.markdown("**📊 데이터 출처**")
    st.caption("Google Maps · Naver Place · 블루리본\n기준: 2025년")
    st.caption("🎓 2023313872 조연재")

# ── 필터 적용 ────────────────────────────────────────────────────────────────
mask = (
    df["district"].isin(sel_districts) &
    df["area"].isin(sel_areas) &
    df["type"].isin(sel_types) &
    (df["rating"] >= min_rating)
)
if search_query.strip():
    mask &= df["name"].str.contains(search_query.strip(), case=False, na=False)

filtered = df[mask].reset_index(drop=True)

# ── 헤더 ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:0.5rem'>
  <div class='hero-title'>Sweet Spots Seoul 🍰</div>
  <div class='hero-sub'>서울 디저트 맛집 인터랙티브 지도 · 베이커리 · 카페 · 빵집 500+</div>
</div>
""", unsafe_allow_html=True)

# ── 메트릭 ────────────────────────────────────────────────────────────────
avg_r   = filtered["rating"].mean() if len(filtered) else 0
top_row = filtered.loc[filtered["rating"].idxmax()] if len(filtered) else None
total_r = filtered["reviews"].sum()
n_dist  = filtered["district"].nunique() if "district" in filtered.columns else 0

st.markdown(f"""
<div class='metric-row'>
  <div class='metric-card'><span class='val'>{len(filtered)}</span><span class='lbl'>맛집 수</span></div>
  <div class='metric-card'><span class='val'>⭐ {avg_r:.2f}</span><span class='lbl'>평균 평점</span></div>
  <div class='metric-card'><span class='val' style='font-size:1.2rem'>{top_row['name'] if top_row is not None else '-'}</span><span class='lbl'>최고 평점</span></div>
  <div class='metric-card'><span class='val'>{n_dist}</span><span class='lbl'>구(區) 수</span></div>
  <div class='metric-card'><span class='val'>{total_r:,}</span><span class='lbl'>추정 총 리뷰</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── 탭 ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 지도 & 차트", "🖼️ 카페 갤러리", "📊 데이터 분석", "📋 전체 리스트"])

# ── TAB 1: 지도 & 차트 ─────────────────────────────────────────────────────
with tab1:
    col_map, col_bar = st.columns([1.4, 1])

    with col_map:
        st.markdown("#### 📍 서울 맛집 지도")
        if len(filtered):
            center_lat = filtered["lat"].mean()
            center_lon = filtered["lon"].mean()
            # 서울 중심 고정 + 적절한 줌
            m = folium.Map(location=[37.5500, 126.9800], zoom_start=11, tiles="CartoDB positron")

            for _, row in filtered.iterrows():
                color = TYPE_COLORS.get(row["type"], "#999")
                emoji = TYPE_EMOJI.get(row["type"], "🍰")
                hours_str = f"🕐 {row['hours']}" if pd.notna(row.get('hours', '')) and row.get('hours', '') else ""
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=7,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.85,
                    popup=folium.Popup(
                        f"<b>{row['name']}</b><br>"
                        f"{emoji} {row['type']}<br>"
                        f"⭐ {row['rating']}<br>"
                        f"📍 {row['area']}, {row['district']}<br>"
                        f"🍴 {row['signature']}<br>"
                        f"{hours_str}",
                        max_width=240
                    ),
                    tooltip=f"{emoji} {row['name']} ({row['district']})"
                ).add_to(m)
            st_folium(m, width=None, height=430, returned_objects=[])
        else:
            st.info("필터 조건에 맞는 맛집이 없습니다.")

    with col_bar:
        st.markdown("#### ⭐ 카테고리별 평균 평점")
        if len(filtered):
            avg_type = (
                filtered.groupby("type")["rating"]
                .mean().reset_index()
                .sort_values("rating", ascending=True)
            )
            fig = px.bar(
                avg_type, x="rating", y="type", orientation="h",
                color="type", color_discrete_map=TYPE_COLORS,
                text=avg_type["rating"].apply(lambda x: f"{x:.2f}"),
                height=210
            )
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(
                showlegend=False, xaxis_range=[4.0, 5.2],
                xaxis_title="", yaxis_title="",
                margin=dict(l=0, r=30, t=10, b=10),
                plot_bgcolor="white", paper_bgcolor="white"
            )
            fig.update_xaxes(gridcolor="#F5EDE8")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🗺️ 구별 맛집 수")
        if len(filtered):
            dist_cnt = (
                filtered.groupby("district").size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
                .head(15)
            )
            fig2 = px.bar(
                dist_cnt, x="district", y="count",
                color="count", text="count", height=220,
                color_continuous_scale=["#F5E8E0", "#C0525A", "#3B1F2B"]
            )
            fig2.update_traces(textposition="outside", marker_line_width=0)
            fig2.update_layout(
                showlegend=False, coloraxis_showscale=False,
                xaxis_title="", yaxis_title="수",
                margin=dict(l=0, r=10, t=10, b=10),
                plot_bgcolor="white", paper_bgcolor="white"
            )
            fig2.update_xaxes(tickangle=-40, gridcolor="#F5EDE8")
            fig2.update_yaxes(gridcolor="#F5EDE8")
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 🥧 카테고리 분포")
        if len(filtered):
            dist_df = filtered.groupby("type").size().reset_index(name="count")
            fig3 = px.pie(
                dist_df, names="type", values="count",
                color="type", color_discrete_map=TYPE_COLORS,
                hole=0.5, height=280
            )
            fig3.update_traces(
                textinfo="label+percent",
                pull=[0.03] * len(dist_df),
                marker=dict(line=dict(color="white", width=2))
            )
            fig3.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="white"
            )
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("#### 💬 평점 분포")
        if len(filtered):
            fig4 = px.histogram(
                filtered, x="rating", nbins=8,
                color_discrete_sequence=["#C0525A"],
                height=280,
                labels={"rating": "평점", "count": "가게 수"}
            )
            fig4.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=0, r=0, t=10, b=20),
                bargap=0.1
            )
            fig4.update_xaxes(gridcolor="#F5EDE8")
            fig4.update_yaxes(gridcolor="#F5EDE8", title="가게 수")
            st.plotly_chart(fig4, use_container_width=True)

    # 구 × 카테고리 히트맵
    st.markdown("#### 🌡️ 구 × 카테고리 평점 히트맵")
    if len(filtered) >= 3:
        pivot = filtered.pivot_table(
            values="rating", index="district", columns="type", aggfunc="mean"
        )
        fig5 = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0, "#F5E8E0"], [0.5, "#E07B7B"], [1, "#3B1F2B"]],
            text=[[f"{v:.2f}" if not pd.isna(v) else "-" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            showscale=True,
            hovertemplate="%{y} · %{x}<br>평점: %{text}<extra></extra>"
        ))
        fig5.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(fig5, use_container_width=True)

# ── TAB 2: 카페 갤러리 ─────────────────────────────────────────────────────
with tab2:
    st.markdown("#### 🖼️ 서울 디저트 맛집 갤러리")
    st.caption(f"총 {len(filtered)}곳 | 필터를 조정하면 결과가 바뀌어요.")

    if len(filtered) == 0:
        st.info("필터 조건에 맞는 맛집이 없습니다.")
    else:
        # 최대 60개만 표시 (성능)
        display_df = filtered.head(60)
        cols = st.columns(3)
        for i, (_, row) in enumerate(display_df.iterrows()):
            with cols[i % 3]:
                color  = TYPE_COLORS.get(row["type"], "#999")
                emoji  = TYPE_EMOJI.get(row["type"], "🍰")
                hours_info = f"🕐 {row['hours']}" if pd.notna(row.get('hours', '')) and str(row.get('hours', '')) not in ['', 'nan'] else ""
                st.markdown(f"""
                <div class='cafe-card'>
                  <img src='{row['img']}' style='width:100%;height:150px;object-fit:cover;' alt='{row['name']}'>
                  <div class='cafe-body'>
                    <div class='cafe-name'>{row['name']}</div>
                    <span class='cafe-tag' style='background:{color}22;color:{color}'>{emoji} {row['type']}</span>
                    <div class='cafe-rating'>⭐ {row['rating']}</div>
                    <div class='cafe-sig'>🍴 {row['signature']}</div>
                    <div style='font-size:0.78rem;color:#C0A090;margin-top:4px'>
                      📍 {row['area']}, {row['district']}<br>{hours_info}
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        if len(filtered) > 60:
            st.caption(f"📌 상위 60곳만 표시 중 (전체 {len(filtered)}곳은 '전체 리스트' 탭에서 확인)")

# ── TAB 3: 데이터 분석 ─────────────────────────────────────────────────────
with tab3:
    st.markdown("#### 🏅 평점 TOP 20 랭킹")
    if len(filtered):
        rank_df = filtered.sort_values("rating", ascending=False).head(20).reset_index(drop=True)
        fig6 = px.bar(
            rank_df, x="name", y="rating", color="type",
            color_discrete_map=TYPE_COLORS,
            text=rank_df["rating"].apply(lambda x: f"{x:.1f}"),
            height=340,
            hover_data={"district": True, "area": True, "signature": True}
        )
        fig6.update_traces(textposition="outside", marker_line_width=0)
        fig6.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0, r=0, t=10, b=90),
            yaxis_range=[4.0, 5.4],
            xaxis_tickangle=-40,
            showlegend=True,
            legend=dict(orientation="h", y=-0.55)
        )
        fig6.update_yaxes(gridcolor="#F5EDE8")
        st.plotly_chart(fig6, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🗺️ 구별 평균 평점")
        if len(filtered):
            gu_avg = (
                filtered.groupby("district")["rating"]
                .mean().reset_index()
                .sort_values("rating", ascending=True)
            )
            fig7 = px.bar(
                gu_avg, x="rating", y="district", orientation="h",
                color="rating",
                color_continuous_scale=["#F5E8E0", "#C0525A", "#3B1F2B"],
                text=gu_avg["rating"].apply(lambda x: f"{x:.2f}"),
                height=400
            )
            fig7.update_traces(textposition="outside")
            fig7.update_layout(
                showlegend=False, coloraxis_showscale=False,
                xaxis_range=[4.0, 5.0],
                xaxis_title="", yaxis_title="",
                margin=dict(l=0, r=40, t=10, b=10),
                plot_bgcolor="white", paper_bgcolor="white"
            )
            fig7.update_xaxes(gridcolor="#F5EDE8")
            st.plotly_chart(fig7, use_container_width=True)

    with col_b:
        st.markdown("#### 💎 숨은 맛집 발견 (고평점 · 소규모)")
        if len(filtered):
            # 평점 높고 이름이 잘 알려지지 않은 곳 (리뷰 적은 것으로 추정)
            gems = (
                filtered[filtered["rating"] >= 4.5]
                .sort_values("rating", ascending=False)
                .head(15)
            )
            for _, g in gems.iterrows():
                c     = TYPE_COLORS.get(g["type"], "#999")
                emoji = TYPE_EMOJI.get(g["type"], "🍰")
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:10px 14px;margin-bottom:7px;
                            border-left:4px solid {c};border:1px solid #F0E6E0;'>
                  <b style='color:#3B1F2B'>{g['name']}</b>
                  <span style='background:{c}22;color:{c};border-radius:20px;padding:2px 8px;
                               font-size:0.72rem;margin-left:6px;'>{emoji} {g['type']}</span>
                  <span style='float:right;color:#C0525A;font-weight:500'>⭐ {g['rating']}</span>
                  <div style='font-size:0.8rem;color:#9B7B87;margin-top:3px'>
                    {g['area']}, {g['district']} · {g['signature']}
                  </div>
                </div>""", unsafe_allow_html=True)

# ── TAB 4: 전체 리스트 ────────────────────────────────────────────────────
with tab4:
    st.markdown(f"#### 📋 전체 맛집 리스트 ({len(filtered)}곳)")

    # 컬럼 선택
    show_cols = ["name", "type", "district", "area", "rating", "signature", "hours", "phone"]
    available_cols = [c for c in show_cols if c in filtered.columns]
    show_df = filtered[available_cols].rename(columns={
        "name":      "가게명",
        "type":      "카테고리",
        "district":  "구",
        "area":      "동네",
        "rating":    "평점",
        "signature": "대표메뉴",
        "hours":     "영업시간",
        "phone":     "전화번호",
    })
    st.dataframe(show_df, use_container_width=True, hide_index=True)

    # 다운로드
    csv_out = show_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ 필터 결과 CSV 다운로드",
        data=csv_out,
        file_name="sweet_spots_seoul_filtered.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("""
<div class='footer'>
  🎓 성균관대학교 미술학과 · Data Hub Project 2025 · 2023313872 조연재<br>
  Built with Streamlit · Plotly · Folium &nbsp;|&nbsp; AI assisted by Claude (Anthropic)
</div>
""", unsafe_allow_html=True)
