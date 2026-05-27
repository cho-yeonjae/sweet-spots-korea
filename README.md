# 🍰 Sweet Spots Korea
### An Interactive Dessert Cafe Map & Analytics Dashboard

> 국내 디저트 종류별 맛집을 지도와 차트로 탐색하는 인터랙티브 Streamlit 대시보드

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-purple?logo=plotly&logoColor=white)
![Folium](https://img.shields.io/badge/Folium-0.15+-green)
![License](https://img.shields.io/badge/License-MIT-pink)

---

## 📌 Project Overview

**Sweet Spots Korea** is a Streamlit-based interactive dashboard that visualizes Korea's dessert cafe culture through maps and data analytics.

The project categorizes cafes by dessert type — bingsu, hangwa, macaron, tart, and cake — allowing users to explore regional trends, ratings, prices, and popular signature items.

> *"Korea's dessert cafe scene is visually unique and culturally rich, but there is no public platform that maps cafes by dessert type and compares them interactively."*

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🗺️ **Interactive Map** | Folium map with color-coded markers by dessert type |
| 🔍 **Sidebar Filters** | Filter by city, type, min rating, and price level — all charts update live |
| ⭐ **Rating Bar Chart** | Average rating comparison across dessert types |
| 🥧 **Donut Chart** | Distribution of cafes by category |
| 💬 **Scatter Plot** | Reviews vs rating — find hidden gems! |
| 🌡️ **City Heatmap** | City × type rating heatmap |
| 🏅 **Ranking Chart** | Top 10 cafes by rating |
| 💎 **Hidden Gems** | High-rated cafes with low review counts |
| 📋 **Data Table** | Sortable table with CSV export |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/sweet-spots-korea.git
cd sweet-spots-korea
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501` 🎉

---

## 🗂️ Project Structure

```
sweet-spots-korea/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 📊 Data Sources

| Source | Usage |
|--------|-------|
| **Google Maps** | Ratings, review counts, coordinates |
| **Kakao Local API** | Cafe search, place information |
| **Naver Place** | Blog reviews and additional ratings |
| **Manual CSV** | 50–100 curated cafes with verified categories |

---

## 🎨 Design Concept

The dashboard uses a **dessert-inspired visual language**:
- Warm cream & berry color palette (`#FFF9F5`, `#3B1F2B`, `#C0525A`)
- DM Serif Display + DM Sans typography for an editorial cafe-menu feel
- Color-coded markers per dessert type for instant visual scanning
- "Hidden Gems" section for data-driven cafe discovery

---

## 🤖 AI Usage Statement

This project was built with AI assistance from **Claude (Anthropic)**:

- Scaffolding the Streamlit layout and component structure
- Generating Plotly and Folium visualization code
- Cleaning and structuring the CSV dataset
- Drafting README documentation
- Improving UI structure and styling

All AI-assisted components are documented as part of the development workflow.  
*(Course guideline: "You CAN and SHOULD use AI to help build your app!")*

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👩‍🎨 Author

**조연재** · 2023313872  
성균관대학교 미술학과  
Data Hub Project 2025
