import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="דשבורד סקר חברתי - גרסה חזותית", layout="wide")

# RTL Styling
st.markdown(
    '''
    <link href="https://fonts.googleapis.com/css2?family=Assistant&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Assistant', sans-serif;
    }
    .stDataFrame table {
        direction: rtl !important;
        text-align: right !important;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    return pd.read_excel("סקר חברתי.xlsx")

df = load_data()

# עמודות קיימות
if "שנה" not in df.columns or "שם  הרשות" not in df.columns:
    st.error("יש לוודא שהקובץ כולל את העמודות 'שנה' ו-'שם  הרשות'")
    st.stop()

# אפשרות בחירת עד 3 משתנים מספריים
st.title("📊 בחירת מדדים להצגה")
numeric_cols = [col for col in df.select_dtypes(include='number').columns if col != "שנה"]

selected_metrics = st.multiselect("בחר עד 3 מדדים להצגה", options=numeric_cols, max_selections=3)

if not selected_metrics:
    st.info("בחר מדד אחד לפחות להצגה.")
else:
    for metric in selected_metrics:
        st.markdown(f"### 📈 {metric}")
        col1, col2 = st.columns([2, 1])

        with col1:
            # גרף קו מגמה לפי שנה
            line_df = df.groupby(["שנה"])[metric].mean().reset_index()
            fig = px.line(line_df, x="שנה", y=metric, markers=True, title=f"מגמת שינוי ב-{metric}")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # דירוג רשויות לפי הערך האחרון
            latest_year = df["שנה"].max()
            rank_df = df[df["שנה"] == latest_year][["שם  הרשות", metric]].dropna()
            rank_df = rank_df.groupby("שם  הרשות")[metric].mean().sort_values(ascending=False).reset_index()
            rank_df["צבע"] = ["🔵" if i < len(rank_df)/2 else "🔴" for i in range(len(rank_df))]

            rank_df_display = rank_df[["צבע", "שם  הרשות", metric]].rename(columns={
                "צבע": "", "שם  הרשות": "רשות", metric: "ציון"
            })
            st.dataframe(rank_df_display, use_container_width=True)

    st.success("הנתונים מוצגים לפי בחירתך. ניתן לשנות את המדדים בכל שלב.")

