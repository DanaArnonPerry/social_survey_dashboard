import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="דשבורד סקר חברתי", layout="wide")

st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    return pd.read_excel("סקר חברתי.xlsx")

def render_bar_table(df, label_col, value_col):
    max_val = df[value_col].max()
    df = df.sort_values(value_col, ascending=False).reset_index(drop=True)
    table_html = "<div style='width:100%'>"
    medals = ['🥇', '🥈', '🥉']

    for i, row in df.iterrows():
        label = row[label_col]
        val = row[value_col]
        percent = int((val / max_val) * 100)

        if i == 0:
            icon = medals[0]
            bar_color = "#FFD700"
        elif i == 1:
            icon = medals[1]
            bar_color = "#C0C0C0"
        elif i == 2:
            icon = medals[2]
            bar_color = "#cd7f32"
        elif i >= len(df) - 3:
            icon = "🔻"
            bar_color = "#FF4B4B"
        else:
            icon = f"{i+1}"
            bar_color = "#1f77b4"

        table_html += f"""
            <div style='margin:6px 0'>
                <strong>{icon} {label}</strong>
                <div style='background:#eee; width:100%; height:20px; position:relative; border-radius:4px; overflow:hidden'>
                    <div style='width:{percent}%; background:{bar_color}; height:100%;'></div>
                    <div style='position:absolute; right:8px; top:0; height:100%; line-height:20px; font-size:13px; color:#000;'>{val:.0f}</div>
                </div>
            </div>
        """
    table_html += "</div>"
    st.markdown(table_html, unsafe_allow_html=True)

df = load_data()

if "שנה" not in df.columns or "שם  הרשות" not in df.columns:
    st.error("יש לוודא שהקובץ כולל את העמודות 'שנה' ו-'שם  הרשות'")
    st.stop()

numeric_cols = [col for col in df.select_dtypes(include='number').columns if col != "שנה"]

tab1, tab2 = st.tabs(["📊 סקירה כללית", "🏆 השוואת ערים"])

with tab1:
    st.header("✨ סקירה כללית על סקר חברתי")
    latest_year = df["שנה"].max()
    prev_year = sorted(df["שנה"].unique())[-2] if len(df["שנה"].unique()) > 1 else None

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 ממוצעים לפי שנה אחרונה")
        mean_latest = df[df["שנה"] == latest_year][numeric_cols].mean().sort_values(ascending=False)
        st.dataframe(mean_latest.round(1))

    with col2:
        if prev_year:
            st.subheader(f"📊 שינוי בין {prev_year} ל-{latest_year}")
            prev = df[df["שנה"] == prev_year][numeric_cols].mean()
            change = ((mean_latest - prev) / prev * 100).round(1)
            change_df = pd.DataFrame({"אחוז שינוי": change}).sort_values("אחוז שינוי", ascending=False)
            st.dataframe(change_df)

    st.subheader("🥧 גרף עוגה לדוגמה")
    example_col = numeric_cols[0]
    pie_data = df[df["שנה"] == latest_year].groupby("שם  הרשות")[example_col].mean().reset_index()
    fig = px.pie(pie_data, names="שם  הרשות", values=example_col, title=f"פילוח לפי {example_col}")
    st.plotly_chart(fig)

with tab2:
    st.title("🏆 השוואת ערים לפי מדדים")
    selected_metrics = st.multiselect("בחר עד 3 מדדים להצגה", options=numeric_cols, max_selections=3)

    if not selected_metrics:
        st.info("בחר מדד אחד לפחות להצגה.")
    else:
        for metric in selected_metrics:
            st.markdown(f"### 📈 {metric}")
            col1, col2 = st.columns([2, 1])

            with col1:
                line_df = df.groupby(["שנה"], as_index=False)[metric].mean()
                fig = px.line(line_df, x="שנה", y=metric, markers=True, title=f"מגמת שינוי ב-{metric}")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                rank_df = df[df["שנה"] == latest_year][["שם  הרשות", metric]].dropna()
                rank_df = rank_df.groupby("שם  הרשות")[metric].mean().sort_values(ascending=False).reset_index()
                rank_df.columns = ["רשות", "ציון"]
                render_bar_table(rank_df, label_col="רשות", value_col="ציון")

        st.success("הנתונים מוצגים לפי בחירתך.")
