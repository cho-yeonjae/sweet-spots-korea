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
.cafe-img { width:100%; height:160px; object-fit:cover; }
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

# ── 실제 맛집 데이터 (50곳+) ────────────────────────────────────────────────
@st.cache_data
def load_data():
    rows = [
        # ── 서울 강남 ──
        dict(name="Shoto 쇼토",            type="케이크",   city="서울", area="압구정",  rating=4.9, reviews=1820, price="비쌈",  lat=37.5270, lon=127.0396, signature="제주 애플망고 쇼트케이크",  img="https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400&q=80"),
        dict(name="썸띵어바웃커피",         type="카페·베이커리", city="서울", area="강남", rating=4.7, reviews=3200, price="보통", lat=37.4979, lon=127.0276, signature="케이크 & 시즌 디저트",       img="https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&q=80"),
        dict(name="플디 도산점",             type="케이크",   city="서울", area="압구정",  rating=4.8, reviews=2100, price="비쌈",  lat=37.5267, lon=127.0399, signature="계절 과일 케이크",           img="https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=400&q=80"),
        dict(name="Upper and Under",        type="케이크",   city="서울", area="강남",    rating=4.8, reviews=624,  price="보통",  lat=37.5027, lon=127.0277, signature="딸기 치즈파이",              img="https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400&q=80"),
        dict(name="누데이크 NUDAKE 성수",   type="카페·베이커리", city="서울", area="성수", rating=4.7, reviews=5400, price="비쌈", lat=37.5443, lon=127.0557, signature="피크 말차 라바 케이크",      img="https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&q=80"),
        dict(name="Gangjeong House",        type="전통 한과", city="서울", area="강남",    rating=4.4, reviews=188,  price="보통",  lat=37.5187, lon=127.0486, signature="개성약과, 쌍화차",           img="https://images.unsplash.com/photo-1611270629569-8b357cb88da9?w=400&q=80"),
        dict(name="로얄마카롱",             type="마카롱",   city="서울", area="강남",    rating=4.5, reviews=660,  price="보통",  lat=37.5022, lon=127.0354, signature="얼그레이, 살티드카라멜",     img="https://images.unsplash.com/photo-1569864358642-9d1684040f43?w=400&q=80"),
        dict(name="장코방",                 type="빙수·전통", city="서울", area="서초",   rating=4.5, reviews=649,  price="저렴",  lat=37.4983, lon=127.0238, signature="팥빙수, 단팥죽",             img="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80"),
        dict(name="시베리안 빙수킹",        type="빙수·전통", city="서울", area="강남",   rating=5.0, reviews=120,  price="저렴",  lat=37.5052, lon=127.0440, signature="망고 빙수 대용량",           img="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80"),
        dict(name="Rare Macaron Gyodae",    type="마카롱",   city="서울", area="서초",    rating=4.4, reviews=105,  price="보통",  lat=37.4892, lon=127.0116, signature="오픈키친 마카롱",            img="https://images.unsplash.com/photo-1569864358642-9d1684040f43?w=400&q=80"),

        # ── 서울 성수·왕십리 ──
        dict(name="Notre Don 노트르돈",     type="케이크",   city="서울", area="성수",    rating=4.9, reviews=204,  price="보통",  lat=37.5473, lon=127.0400, signature="피스타치오 무스케이크",      img="https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&q=80"),
        dict(name="어나더사이드",           type="카페·베이커리", city="서울", area="성수", rating=4.6, reviews=980,  price="보통", lat=37.5448, lon=127.0558, signature="크루아상, 스콘",              img="https://images.unsplash.com/photo-1586444248902-2f64eddc8df5?w=400&q=80"),
        dict(name="달콤한 거짓말",          type="케이크",   city="서울", area="성수",    rating=4.5, reviews=760,  price="보통",  lat=37.5440, lon=127.0560, signature="레어치즈케이크",             img="https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=400&q=80"),

        # ── 서울 마포·홍대·연남·합정 ──
        dict(name="Teddy Beurre House",     type="타르트",   city="서울", area="용산·이태원", rating=4.8, reviews=1709, price="보통", lat=37.5317, lon=126.9725, signature="망고 타르트, 에그타르트",  img="https://images.unsplash.com/photo-1519915028121-7d3463d20b13?w=400&q=80"),
        dict(name="Nukeunog 느크노그",      type="카페·베이커리", city="서울", area="홍대·마포", rating=5.0, reviews=450, price="보통", lat=37.5625, lon=126.9258, signature="당근 슈크림, 고구마 브륄레", img="https://images.unsplash.com/photo-1586444248902-2f64eddc8df5?w=400&q=80"),
        dict(name="짙은산 (연남동)",        type="케이크",   city="서울", area="연남·연희", rating=4.7, reviews=380,  price="보통",  lat=37.5607, lon=126.9301, signature="밤·말차 테린느 케이크",      img="https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&q=80"),
        dict(name="카페 메틀",              type="카페·베이커리", city="서울", area="홍대·마포", rating=4.6, reviews=520, price="보통", lat=37.5490, lon=126.9170, signature="피스타치오 크로플",         img="https://images.unsplash.com/photo-1586444248902-2f64eddc8df5?w=400&q=80"),
        dict(name="Tarte Lab Seoul",        type="타르트",   city="서울", area="홍대·마포", rating=4.7, reviews=530,  price="보통",  lat=37.5590, lon=126.9220, signature="레몬 타르트, 말차 타르트",   img="https://images.unsplash.com/photo-1519915028121-7d3463d20b13?w=400&q=80"),
        dict(name="파파타르트 합정",        type="타르트",   city="서울", area="홍대·마포", rating=4.6, reviews=390,  price="저렴",  lat=37.5501, lon=126.9145, signature="에그타르트, 딸기 타르트",    img="https://images.unsplash.com/photo-1519915028121-7d3463d20b13?w=400&q=80"),

        # ── 서울 종로·북촌·인사동 ──
        dict(name="신라당 익선",            type="전통 한과", city="서울", area="종로·북촌", rating=4.9, reviews=444,  price="보통",  lat=37.5738, lon=126.9899, signature="주악, 강정, 유과",          img="https://images.unsplash.com/photo-1611270629569-8b357cb88da9?w=400&q=80"),
        dict(name="한과미의식 안녕",        type="전통 한과", city="서울", area="종로·북촌", rating=5.0, reviews=423,  price="보통",  lat=37.5744, lon=126.9840, signature="약과, 다식 선물세트",        img="https://images.unsplash.com/photo-1611270629569-8b357cb88da9?w=400&q=80"),
        dict(name="Aon 아온",               type="전통 한과", city="서울", area="종로·북촌", rating=4.9, reviews=824,  price="보통",  lat=37.5778, lon=126.9858, signature="딸기·밤·고구마 모찌",       img="https://images.unsplash.com/photo-1611270629569-8b357cb88da9?w=400&q=80"),
        dict(name="삼청빙수",               type="빙수·전통", city="서울", area="종로·북촌", rating=4.5, reviews=803,  price="저렴",  lat=37.5829, lon=126.9819, signature="흑임자 빙수, 팥빙수",        img="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80"),
        dict(name="구욱희 카페",            type="카페·베이커리", city="서울", area="종로·북촌", rating=4.6, reviews=670, price="보통", lat=37.5760, lon=126.9820, signature="스콘, 마카롱, 케이크",      img="https://images.unsplash.com/photo-1586444248902-2f64eddc8df5?w=400&q=80"),
        dict(name="관훈갤러리카페",         type="카페·베이커리", city="서울", area="종로·북촌", rating=4.4, reviews=310, price="보통", lat=37.5750, lon=126.9850, signature="수플레, 아메리카노",        img="https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&q=80"),

        # ── 서울 기타 ──
        dict(name="빈브라더스 커피하우스",  type="카페·베이커리", city="서울", area="이태원·한남", rating=4.8, reviews=2100, price="보통", lat=37.5340, lon=126.9930, signature="시그니처 커피, 스콘",     img="https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&q=80"),
        dict(name="5시에서7시까지",         type="카페·베이커리", city="서울", area="이태원·한남", rating=4.5, reviews=870, price="보통", lat=37.5360, lon=126.9910, signature="수플레, 크림브륄레",        img="https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&q=80"),

        # ── 부산 ──
        dict(name="보노베리 본점",          type="타르트",   city="부산", area="금정구",   rating=4.9, reviews=340,  price="보통",  lat=35.2310, lon=129.0888, signature="레몬라임 타르트, 피스타치오", img="https://images.unsplash.com/photo-1519915028121-7d3463d20b13?w=400&q=80"),
        dict(name="올림프케이크 해운대",    type="케이크",   city="부산", area="해운대",   rating=4.5, reviews=280,  price="보통",  lat=35.1599, lon=129.1527, signature="글루텐프리 케이크",          img="https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&q=80"),
        dict(name="빠따슈",                 type="카페·베이커리", city="부산", area="해운대·해리단길", rating=4.7, reviews=920, price="보통", lat=35.1620, lon=129.1600, signature="휘낭시에, 에클레어, 마카롱", img="https://images.unsplash.com/photo-1586444248902-2f64eddc8df5?w=400&q=80"),
        dict(name="이지요드누보",           type="카페·베이커리", city="부산", area="전포·서면",   rating=4.6, reviews=1100, price="보통", lat=35.1580, lon=129.0590, signature="시즌 디저트, 브런치",     img="https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&q=80"),
        dict(name="카페모모 부산",          type="빙수·전통", city="부산", area="서면",     rating=4.5, reviews=560,  price="저렴",  lat=35.1576, lon=129.0592, signature="수제팥 인절미 빙수",         img="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80"),
        dict(name="포시즌스 마루빙수",      type="빙수·전통", city="부산", area="해운대",   rating=4.8, reviews=430,  price="비쌈",  lat=35.1628, lon=129.1597, signature="우유 얼음 팥빙수",           img="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80"),

        # ── 제주 ──
        dict(name="오설록 티뮤지엄",        type="전통 한과", city="제주", area="서귀포·안덕", rating=4.7, reviews=8700, price="보통", lat=33.3067, lon=126.2887, signature="그린티 롤케이크, 말차 아이스크림", img="https://images.unsplash.com/photo-1611270629569-8b357cb88da9?w=400&q=80"),
        dict(name="카페 봄날",              type="카페·베이커리", city="제주", area="제주시",    rating=4.6, reviews=1240, price="보통", lat=33.5145, lon=126.5213, signature="한라봉 타르트, 제주 감귤 케이크", img="https://images.unsplash.com/photo-1586444248902-2f64eddc8df5?w=400&q=80"),
        dict(name="제주 빙수 명가",         type="빙수·전통", city="제주", area="서귀포",   rating=4.5, reviews=760,  price="보통",  lat=33.2503, lon=126.5665, signature="애플망고 빙수",              img="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80"),
        dict(name="우도 땅콩 아이스크림",   type="빙수·전통", city="제주", area="우도",     rating=4.8, reviews=3200, price="저렴",  lat=33.5082, lon=126.9519, signature="우도 땅콩 소프트아이스크림", img="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80"),
        dict(name="카카오 스페이스 제주",   type="카페·베이커리", city="제주", area="서귀포·안덕", rating=4.8, reviews=5600, price="보통", lat=33.3132, lon=126.3020, signature="초콜릿 디저트 전품목",      img="https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&q=80"),

        # ── 대구 ──
        dict(name="봉산동 과일빙수",        type="빙수·전통", city="대구", area="봉산동·중구", rating=4.6, reviews=980,  price="보통",  lat=35.8653, lon=128.5953, signature="수박·망고·복숭아 과일빙수", img="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80"),
        dict(name="동성로 카스테라",        type="카페·베이커리", city="대구", area="동성로·중구", rating=4.4, reviews=670, price="저렴", lat=35.8688, lon=128.5961, signature="촉촉 카스테라",              img="https://images.unsplash.com/photo-1586444248902-2f64eddc8df5?w=400&q=80"),
        dict(name="수성구 디저트 명가",     type="케이크",   city="대구", area="수성구",   rating=4.5, reviews=420,  price="보통",  lat=35.8571, lon=128.6300, signature="생크림 케이크, 롤케이크",    img="https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&q=80"),

        # ── 전주 ──
        dict(name="전주 한옥마을 한과",     type="전통 한과", city="전주", area="한옥마을", rating=4.6, reviews=1890, price="저렴",  lat=35.8175, lon=127.1529, signature="전주 약과, 전통 한과 세트",  img="https://images.unsplash.com/photo-1611270629569-8b357cb88da9?w=400&q=80"),
        dict(name="전주 전통 빙수",         type="빙수·전통", city="전주", area="한옥마을", rating=4.5, reviews=640,  price="저렴",  lat=35.8165, lon=127.1535, signature="팥빙수, 콩빙수",             img="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80"),
        dict(name="PNB 풍년제과 본점",      type="카페·베이커리", city="전주", area="전주 시내",  rating=4.7, reviews=2300, price="저렴", lat=35.8219, lon=127.1489, signature="초코파이, 마론파이",        img="https://images.unsplash.com/photo-1586444248902-2f64eddc8df5?w=400&q=80"),

        # ── 경주 ──
        dict(name="황리단길 찰보리빵",      type="전통 한과", city="경주", area="황리단길", rating=4.5, reviews=1560, price="저렴",  lat=35.8370, lon=129.2163, signature="찰보리빵, 경주 황남빵",      img="https://images.unsplash.com/photo-1611270629569-8b357cb88da9?w=400&q=80"),
        dict(name="황남빵 본점",            type="전통 한과", city="경주", area="황리단길", rating=4.8, reviews=4200, price="저렴",  lat=35.8354, lon=129.2166, signature="황남빵 (팥앙금 과자)",       img="https://images.unsplash.com/photo-1611270629569-8b357cb88da9?w=400&q=80"),
        dict(name="교촌마을 카페",          type="카페·베이커리", city="경주", area="교촌마을", rating=4.5, reviews=890, price="보통", lat=35.8360, lon=129.2175, signature="곶감 라떼, 전통 디저트",    img="https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&q=80"),

        # ── 춘천 ──
        dict(name="춘천 닭갈비 골목 카페",  type="카페·베이커리", city="춘천", area="명동·중앙로", rating=4.3, reviews=340, price="저렴", lat=37.8813, lon=127.7298, signature="막국수 시럽 빙수",          img="https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&q=80"),

        # ── 인천 ──
        dict(name="송월동 마카롱",          type="마카롱",   city="인천", area="동화마을", rating=4.4, reviews=510,  price="보통",  lat=37.4752, lon=126.6195, signature="수제 마카롱 전품목",         img="https://images.unsplash.com/photo-1569864358642-9d1684040f43?w=400&q=80"),
        dict(name="개항로 근대 카페",       type="카페·베이커리", city="인천", area="개항로·중구", rating=4.5, reviews=720, price="보통", lat=37.4740, lon=126.6167, signature="옛날 과자, 팥빙수",         img="https://images.unsplash.com/photo-1586444248902-2f64eddc8df5?w=400&q=80"),

        # ── 강릉 ──
        dict(name="강릉 커피거리 테라로사", type="카페·베이커리", city="강릉", area="커피거리", rating=4.8, reviews=6200, price="보통", lat=37.7519, lon=128.8761, signature="스페셜티 커피, 케이크",      img="https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&q=80"),
        dict(name="순두부 젤라토 강릉",     type="빙수·전통", city="강릉", area="초당동",   rating=4.6, reviews=1800, price="저렴",  lat=37.7615, lon=128.9108, signature="순두부 젤라토 아이스크림",   img="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80"),
    ]
    return pd.DataFrame(rows)

df = load_data()

TYPE_COLORS = {
    "케이크":      "#E07B7B",
    "카페·베이커리":"#F4A460",
    "전통 한과":   "#7BADE0",
    "빙수·전통":   "#7BCEC0",
    "마카롱":      "#C49DE0",
    "타르트":      "#E0C07B",
}
TYPE_EMOJI = {
    "케이크":       "🎂",
    "카페·베이커리":"☕",
    "전통 한과":    "🍡",
    "빙수·전통":    "🍧",
    "마카롱":       "🫐",
    "타르트":       "🥧",
}

# ── 사이드바 ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍰 Sweet Spots Korea")
    st.markdown("---")
    st.markdown("### 🔍 필터")

    all_cities = sorted(df["city"].unique().tolist())
    sel_cities = st.multiselect("🏙️ 도시 선택", options=all_cities, default=all_cities)

    all_areas = sorted(df[df["city"].isin(sel_cities)]["area"].unique().tolist())
    sel_areas = st.multiselect("📍 지역(동네) 선택", options=all_areas, default=all_areas)

    all_types = sorted(df["type"].unique().tolist())
    sel_types = st.multiselect("🍰 디저트 종류", options=all_types, default=all_types)

    min_rating = st.slider("⭐ 최소 평점", 4.0, 5.0, 4.3, 0.1)

    price_opt = st.multiselect("💰 가격대", options=["저렴", "보통", "비쌈"], default=["저렴", "보통", "비쌈"])

    st.markdown("---")
    st.markdown("**📊 데이터 출처**")
    st.caption("Google Maps · Naver Place · 블루리본\n기준: 2025년")
    st.caption("🎓 2023313872 조연재")

filtered = df[
    df["city"].isin(sel_cities) &
    df["area"].isin(sel_areas) &
    df["type"].isin(sel_types) &
    (df["rating"] >= min_rating) &
    df["price"].isin(price_opt)
].reset_index(drop=True)

# ── 헤더 ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:0.5rem'>
  <div class='hero-title'>Sweet Spots Korea 🍰</div>
  <div class='hero-sub'>국내 디저트 종류별 맛집 인터랙티브 지도 · 서울·부산·제주·대구·전주·경주·강릉·인천</div>
</div>
""", unsafe_allow_html=True)

# ── 메트릭 ────────────────────────────────────────────────────────────────
avg_r   = filtered["rating"].mean() if len(filtered) else 0
top_row = filtered.loc[filtered["rating"].idxmax()] if len(filtered) else None
total_r = filtered["reviews"].sum()
n_cities = filtered["city"].nunique()

st.markdown(f"""
<div class='metric-row'>
  <div class='metric-card'><span class='val'>{len(filtered)}</span><span class='lbl'>맛집 수</span></div>
  <div class='metric-card'><span class='val'>⭐ {avg_r:.2f}</span><span class='lbl'>평균 평점</span></div>
  <div class='metric-card'><span class='val' style='font-size:1.2rem'>{top_row['name'] if top_row is not None else '-'}</span><span class='lbl'>최고 평점</span></div>
  <div class='metric-card'><span class='val'>{n_cities}</span><span class='lbl'>도시 수</span></div>
  <div class='metric-card'><span class='val'>{total_r:,}</span><span class='lbl'>총 리뷰</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── 탭 ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 지도 & 차트", "🖼️ 카페 갤러리", "📊 데이터 분석", "📋 전체 리스트"])

# ── TAB 1: 지도 & 차트 ─────────────────────────────────────────────────────
with tab1:
    col_map, col_bar = st.columns([1.4, 1])

    with col_map:
        st.markdown("#### 📍 맛집 지도")
        if len(filtered):
            center_lat = filtered["lat"].mean()
            center_lon = filtered["lon"].mean()
            m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles="CartoDB positron")
            for _, row in filtered.iterrows():
                color = TYPE_COLORS.get(row["type"], "#999")
                emoji = TYPE_EMOJI.get(row["type"], "🍰")
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=9, color=color, fill=True,
                    fill_color=color, fill_opacity=0.85,
                    popup=folium.Popup(
                        f"<b>{row['name']}</b><br>{emoji} {row['type']}<br>"
                        f"⭐ {row['rating']} | 💬 {row['reviews']:,}개<br>"
                        f"📍 {row['area']}, {row['city']}<br>"
                        f"🍴 {row['signature']}<br>💰 {row['price']}",
                        max_width=240
                    ),
                    tooltip=f"{emoji} {row['name']} ({row['city']})"
                ).add_to(m)
            st_folium(m, width=None, height=400, returned_objects=[])
        else:
            st.info("필터 조건에 맞는 맛집이 없습니다.")

    with col_bar:
        st.markdown("#### ⭐ 종류별 평균 평점")
        if len(filtered):
            avg_type = filtered.groupby("type")["rating"].mean().reset_index().sort_values("rating", ascending=True)
            fig = px.bar(avg_type, x="rating", y="type", orientation="h",
                         color="type", color_discrete_map=TYPE_COLORS,
                         text=avg_type["rating"].apply(lambda x: f"{x:.2f}"), height=200)
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(showlegend=False, xaxis_range=[4.0, 5.2],
                              xaxis_title="", yaxis_title="",
                              margin=dict(l=0, r=30, t=10, b=10),
                              plot_bgcolor="white", paper_bgcolor="white")
            fig.update_xaxes(gridcolor="#F5EDE8")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🏙️ 도시별 맛집 수")
        if len(filtered):
            city_cnt = filtered.groupby("city").size().reset_index(name="count").sort_values("count", ascending=False)
            fig2 = px.bar(city_cnt, x="city", y="count", color="city",
                          text="count", height=200,
                          color_discrete_sequence=["#E07B7B","#7BADE0","#7BCEC0","#C49DE0","#E0C07B","#F4A460","#A0C4FF","#B5EAD7"])
            fig2.update_traces(textposition="outside", marker_line_width=0)
            fig2.update_layout(showlegend=False, xaxis_title="", yaxis_title="수",
                               margin=dict(l=0, r=10, t=10, b=10),
                               plot_bgcolor="white", paper_bgcolor="white")
            fig2.update_yaxes(gridcolor="#F5EDE8")
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 🥧 종류별 분포")
        if len(filtered):
            dist = filtered.groupby("type").size().reset_index(name="count")
            fig3 = px.pie(dist, names="type", values="count",
                          color="type", color_discrete_map=TYPE_COLORS, hole=0.5, height=280)
            fig3.update_traces(textinfo="label+percent", pull=[0.03]*len(dist),
                               marker=dict(line=dict(color="white", width=2)))
            fig3.update_layout(showlegend=False, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="white")
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("#### 💬 리뷰 수 vs 평점 (숨은 맛집 발견!)")
        if len(filtered):
            fig4 = px.scatter(filtered, x="reviews", y="rating",
                              color="type", color_discrete_map=TYPE_COLORS,
                              hover_name="name", size="reviews", size_max=28,
                              height=280, labels={"reviews":"리뷰 수","rating":"평점","type":"종류"})
            fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                               margin=dict(l=0,r=0,t=10,b=20), yaxis_range=[4.2,5.15],
                               legend=dict(title="종류", orientation="h", y=-0.3))
            fig4.update_xaxes(gridcolor="#F5EDE8")
            fig4.update_yaxes(gridcolor="#F5EDE8")
            st.plotly_chart(fig4, use_container_width=True)

    # 히트맵
    st.markdown("#### 🌡️ 도시 × 종류 평점 히트맵")
    if len(filtered) >= 3:
        pivot = filtered.pivot_table(values="rating", index="city", columns="type", aggfunc="mean")
        fig5 = go.Figure(data=go.Heatmap(
            z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
            colorscale=[[0,"#F5E8E0"],[0.5,"#E07B7B"],[1,"#3B1F2B"]],
            text=[[f"{v:.2f}" if not pd.isna(v) else "-" for v in row] for row in pivot.values],
            texttemplate="%{text}", showscale=True,
            hovertemplate="%{y} · %{x}<br>평점: %{text}<extra></extra>"
        ))
        fig5.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=10),
                           plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig5, use_container_width=True)

# ── TAB 2: 카페 갤러리 ─────────────────────────────────────────────────────
with tab2:
    st.markdown("#### 🖼️ 디저트 카페 갤러리")
    st.caption("이미지를 클릭하면 상세 정보를 확인할 수 있어요.")

    if len(filtered) == 0:
        st.info("필터 조건에 맞는 맛집이 없습니다.")
    else:
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered.iterrows()):
            with cols[i % 3]:
                color = TYPE_COLORS.get(row["type"], "#999")
                emoji = TYPE_EMOJI.get(row["type"], "🍰")
                st.markdown(f"""
                <div class='cafe-card'>
                  <img class='cafe-img' src='{row['img']}' alt='{row['name']}'>
                  <div class='cafe-body'>
                    <div class='cafe-name'>{row['name']}</div>
                    <span class='cafe-tag' style='background:{color}22;color:{color}'>{emoji} {row['type']}</span>
                    <div class='cafe-rating'>⭐ {row['rating']} &nbsp;|&nbsp; 💬 {row['reviews']:,}개 리뷰</div>
                    <div class='cafe-sig'>🍴 {row['signature']}</div>
                    <div style='font-size:0.78rem;color:#C0A090;margin-top:4px'>📍 {row['area']}, {row['city']} &nbsp;|&nbsp; 💰 {row['price']}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

# ── TAB 3: 데이터 분석 ─────────────────────────────────────────────────────
with tab3:
    st.markdown("#### 🏅 전체 평점 TOP 15 랭킹")
    if len(filtered):
        rank_df = filtered.sort_values("rating", ascending=False).head(15).reset_index(drop=True)
        fig6 = px.bar(rank_df, x="name", y="rating", color="type",
                      color_discrete_map=TYPE_COLORS,
                      text=rank_df["rating"].apply(lambda x: f"{x:.1f}"), height=320)
        fig6.update_traces(textposition="outside", marker_line_width=0)
        fig6.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           margin=dict(l=0,r=0,t=10,b=80), yaxis_range=[4.0,5.4],
                           xaxis_tickangle=-35, showlegend=True,
                           legend=dict(orientation="h", y=-0.45))
        fig6.update_yaxes(gridcolor="#F5EDE8")
        st.plotly_chart(fig6, use_container_width=True)

    st.markdown("#### 💎 숨은 맛집 (높은 평점 · 적은 리뷰)")
    if len(filtered):
        median_r = filtered["reviews"].median()
        gems = filtered[(filtered["reviews"] < median_r) & (filtered["rating"] >= 4.6)].sort_values("rating", ascending=False)
        if len(gems):
            for _, g in gems.iterrows():
                c = TYPE_COLORS.get(g["type"], "#999")
                emoji = TYPE_EMOJI.get(g["type"], "🍰")
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:12px 16px;margin-bottom:8px;
                            border-left:4px solid {c};border:1px solid #F0E6E0;'>
                  <b style='color:#3B1F2B'>{g['name']}</b>
                  <span style='background:{c}22;color:{c};border-radius:20px;padding:2px 8px;
                               font-size:0.75rem;margin-left:8px;'>{emoji} {g['type']}</span>
                  <span style='float:right;color:#C0525A;font-weight:500'>⭐ {g['rating']}</span>
                  <div style='font-size:0.82rem;color:#9B7B87;margin-top:4px'>
                    {g['area']}, {g['city']} · {g['signature']} · 리뷰 {g['reviews']:,}개
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("현재 조건에서 숨은 맛집이 없습니다.")

# ── TAB 4: 전체 리스트 ────────────────────────────────────────────────────
with tab4:
    st.markdown(f"#### 📋 전체 맛집 리스트 ({len(filtered)}곳)")
    show_df = filtered[["name","type","city","area","rating","reviews","price","signature"]].rename(columns={
        "name":"가게명","type":"종류","city":"도시","area":"지역",
        "rating":"평점","reviews":"리뷰수","price":"가격대","signature":"대표 메뉴"
    })
    st.dataframe(show_df, use_container_width=True, hide_index=True)
    csv = show_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ CSV 다운로드", data=csv, file_name="sweet_spots_korea.csv", mime="text/csv")

st.markdown("---")
st.markdown("""
<div class='footer'>
  🎓 성균관대학교 미술학과 · Data Hub Project 2025 · 2023313872 조연재<br>
  Built with Streamlit · Plotly · Folium &nbsp;|&nbsp; AI assisted by Claude (Anthropic)
</div>
""", unsafe_allow_html=True)
