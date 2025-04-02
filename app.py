import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="דשבורד סקר חברתי", layout="wide")

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
    .stDownloadButton, .stButton {
        float: right;
    }
    </style>
    ''',
    unsafe_allow_html=True
)
(page_title="דשבורד סקר חברתי", layout="wide")
st.title("📊 דשבורד סקר חברתי")

@st.cache_data
def load_data():
    return pd.read_excel("סקר חברתי.xlsx")

df = load_data()

if "רשות מקומית" not in df.columns or "שנה" not in df.columns:
    st.error("יש לוודא שהקובץ כולל עמודות 'רשות מקומית' ו-'שנה'")
else:
    with st.sidebar:
        st.header("🎛️ מסננים")
        selected_cities = st.multiselect("בחר רשויות מקומיות", options=sorted(df["רשות מקומית"].dropna().unique()))
        selected_years = st.multiselect("בחר שנים", options=sorted(df["שנה"].dropna().unique()))
        search_term = st.text_input("🔍 חיפוש בטקסט")

    filtered_df = df.copy()
    if selected_cities:
        filtered_df = filtered_df[filtered_df["רשות מקומית"].isin(selected_cities)]
    if selected_years:
        filtered_df = filtered_df[filtered_df["שנה"].isin(selected_years)]
    if search_term:
        filtered_df = filtered_df[filtered_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)]

    st.subheader("📄 טבלת נתונים")
    st.dataframe(filtered_df, use_container_width=True)

    numeric_cols = filtered_df.select_dtypes(include='number').columns.tolist()
    if numeric_cols:
        st.subheader("📈 גרף משתנה מספרי")
        selected_column = st.selectbox("בחר משתנה לגרף", numeric_cols)
        chart_data = filtered_df.groupby("רשות מקומית")[selected_column].mean().sort_values(ascending=False)
        st.bar_chart(chart_data)

        st.subheader("📉 גרף מגמה לאורך זמן")
        line_var = st.selectbox("בחר משתנה למגמה", numeric_cols, key="line_chart")
        line_df = filtered_df.groupby(["שנה", "רשות מקומית"])[line_var].mean().reset_index()
        pivot_df = line_df.pivot(index="שנה", columns="רשות מקומית", values=line_var)
        st.line_chart(pivot_df)

        st.subheader("🏅 דירוג הרשויות")
        latest_year = filtered_df["שנה"].max()
        rank_df = filtered_df[filtered_df["שנה"] == latest_year]
        rank_summary = rank_df.groupby("רשות מקומית")[selected_column].mean().sort_values(ascending=False)
        st.dataframe(rank_summary.reset_index(), use_container_width=True)

        st.subheader("📊 אחוז שינוי משנה קודמת")
        change_var = st.selectbox("בחר משתנה לשינוי", numeric_cols, key="change")
        year_sorted = sorted(filtered_df["שנה"].dropna().unique())
        if len(year_sorted) >= 2:
            last, prev = year_sorted[-1], year_sorted[-2]
            df_last = filtered_df[filtered_df["שנה"] == last].groupby("רשות מקומית")[change_var].mean()
            df_prev = filtered_df[filtered_df["שנה"] == prev].groupby("רשות מקומית")[change_var].mean()
            change_df = pd.DataFrame({"שנה קודמת": df_prev, "שנה נוכחית": df_last}).dropna()
            change_df["אחוז שינוי"] = ((change_df["שנה נוכחית"] - change_df["שנה קודמת"]) / change_df["שנה קודמת"]) * 100

            def color_change(val):
                if val > 0:
                    return 'color: green'
                elif val < 0:
                    return 'color: red'
                return ''

            styled_df = change_df.reset_index().style.format({"אחוז שינוי": "{:.2f}%"}).applymap(color_change, subset=["אחוז שינוי"])
            st.dataframe(styled_df, use_container_width=True)

        st.subheader("🥧 גרף עוגה לפי קטגוריה")
        cat_cols = filtered_df.select_dtypes(include='object').columns.tolist()
        if cat_cols:
            cat_col = st.selectbox("בחר קטגוריה", cat_cols)
            pie_data = filtered_df[cat_col].value_counts().reset_index()
            pie_data.columns = [cat_col, "כמות"]
            fig = px.pie(pie_data, names=cat_col, values="כמות", title=f"פילוח לפי {cat_col}")
            st.plotly_chart(fig)

    # הורדה כקובץ אקסל
    st.subheader("📥 הורדת נתונים")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name="נתונים מסוננים")
    st.download_button("📤 הורד כ-Excel", data=buffer.getvalue(), file_name="סקר_חברתי_מסונן.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
