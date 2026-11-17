from pathlib import Path
import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="📊",
    layout="wide",
)

REQUIRED = [
    "gender",
    "race/ethnicity",
    "parental level of education",
    "lunch",
    "test preparation course",
    "math score",
    "reading score",
    "writing score",
]

DISPLAY = {
    "gender": "Gender",
    "race/ethnicity": "Race / ethnicity",
    "parental level of education": "Parental education",
    "lunch": "Lunch category",
    "test preparation course": "Test preparation",
    "math score": "Math score",
    "reading score": "Reading score",
    "writing score": "Writing score",
}

@st.cache_data
def load_data(file_bytes: bytes, filename: str) -> pd.DataFrame:
    suffix = Path(filename).suffix.lower()
    if suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1")
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df

def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(
            "These expected columns are missing: "
            + ", ".join(missing)
            + ". Please use the StudentsPerformance dataset with its standard column names."
        )

    for col in REQUIRED[:5]:
        df[col] = df[col].astype("string").str.strip()

    for col in REQUIRED[5:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=REQUIRED)
    for col in REQUIRED[5:]:
        df[col] = df[col].clip(0, 100)

    df = df.drop_duplicates().reset_index(drop=True)
    return df

st.title("📊 Student Performance Analytics")
st.caption("An interactive exploratory analysis of student academic performance.")

with st.sidebar:
    st.header("Load your dataset")
    uploaded = st.file_uploader(
        "Upload StudentsPerformance.csv or .xlsx",
        type=["csv", "xlsx", "xls"],
        help="Use the student performance dataset you previously opened in Excel."
    )

    default_path = Path("data/StudentsPerformance.csv")
    if uploaded is not None:
        raw = load_data(uploaded.getvalue(), uploaded.name)
        source_name = uploaded.name
    elif default_path.exists():
        raw = load_data(default_path.read_bytes(), default_path.name)
        source_name = default_path.name
    else:
        st.info("Upload your CSV or Excel dataset to start.")
        st.stop()

try:
    df = clean_data(raw)
except Exception as exc:
    st.error(f"Could not prepare this dataset: {exc}")
    st.stop()

st.sidebar.success(f"Loaded: {source_name}")
st.sidebar.caption(f"{len(df):,} rows after cleaning")

st.sidebar.header("Dashboard filters")
def filter_options(column, label):
    choices = sorted(df[column].dropna().astype(str).unique().tolist())
    return st.sidebar.multiselect(label, choices, default=choices)

gender_sel = filter_options("gender", "Gender")
lunch_sel = filter_options("lunch", "Lunch category")
prep_sel = filter_options("test preparation course", "Test preparation")
race_sel = filter_options("race/ethnicity", "Race / ethnicity")

filtered = df[
    df["gender"].astype(str).isin(gender_sel)
    & df["lunch"].astype(str).isin(lunch_sel)
    & df["test preparation course"].astype(str).isin(prep_sel)
    & df["race/ethnicity"].astype(str).isin(race_sel)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Select at least one option in each filter.")
    st.stop()

scores = ["math score", "reading score", "writing score"]
avg_math = filtered["math score"].mean()
avg_read = filtered["reading score"].mean()
avg_write = filtered["writing score"].mean()
overall_avg = filtered[scores].to_numpy().mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Students", f"{len(filtered):,}")
k2.metric("Average math", f"{avg_math:.2f}")
k3.metric("Average reading", f"{avg_read:.2f}")
k4.metric("Average writing", f"{avg_write:.2f}")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Average scores by gender")
    gender_scores = filtered.groupby("gender", as_index=False)[scores].mean()
    gender_long = gender_scores.melt(
        id_vars="gender", var_name="Subject", value_name="Average score"
    )
    gender_long["Subject"] = gender_long["Subject"].map({
        "math score": "Math", "reading score": "Reading", "writing score": "Writing"
    })
    fig = px.bar(
        gender_long, x="gender", y="Average score", color="Subject",
        barmode="group", text_auto=".1f",
        labels={"gender": "Gender"},
    )
    fig.update_layout(legend_title_text="", yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Test preparation and average scores")
    prep_scores = filtered.groupby("test preparation course", as_index=False)[scores].mean()
    prep_long = prep_scores.melt(
        id_vars="test preparation course", var_name="Subject", value_name="Average score"
    )
    prep_long["Subject"] = prep_long["Subject"].map({
        "math score": "Math", "reading score": "Reading", "writing score": "Writing"
    })
    fig = px.bar(
        prep_long, x="test preparation course", y="Average score",
        color="Subject", barmode="group", text_auto=".1f",
        labels={"test preparation course": "Test preparation"},
    )
    fig.update_layout(legend_title_text="", yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Score distributions")
    score_long = filtered[scores].melt(var_name="Subject", value_name="Score")
    score_long["Subject"] = score_long["Subject"].map({
        "math score": "Math", "reading score": "Reading", "writing score": "Writing"
    })
    fig = px.box(score_long, x="Subject", y="Score", color="Subject", points="outliers")
    fig.update_layout(showlegend=False, yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Score correlations")
    corr = filtered[scores].corr(numeric_only=True).rename(index={
        "math score": "Math", "reading score": "Reading", "writing score": "Writing"
    }, columns={
        "math score": "Math", "reading score": "Reading", "writing score": "Writing"
    })
    fig = px.imshow(
        corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu",
        aspect="auto"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Automatically generated observations")

subject_means = pd.Series({
    "Math": avg_math, "Reading": avg_read, "Writing": avg_write
})
highest = subject_means.idxmax()
lowest = subject_means.idxmin()
a, b = st.columns(2)
with a:
    st.write(f"• **Highest average subject:** {highest} ({subject_means[highest]:.2f}).")
    st.write(f"• **Lowest average subject:** {lowest} ({subject_means[lowest]:.2f}).")
with b:
    prep_means = filtered.groupby("test preparation course")[scores].mean()
    if {"completed", "none"}.issubset(set(prep_means.index.astype(str))):
        completed_avg = prep_means.loc["completed"].mean()
        none_avg = prep_means.loc["none"].mean()
        gap = completed_avg - none_avg
        direction = "higher" if gap > 0 else "lower" if gap < 0 else "the same"
        st.write(
            f"• **Preparation comparison:** students marked completed have an "
            f"average across the three subjects {abs(gap):.2f} points {direction} "
            f"than students marked none."
        )
    else:
        st.write("• Select both preparation categories to compare completed vs none.")

st.caption(
    "These are descriptive patterns in the selected data, not proof that one factor causes another."
)

with st.expander("View cleaned data"):
    st.dataframe(filtered.rename(columns=DISPLAY), use_container_width=True, hide_index=True)
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered, cleaned CSV",
        data=csv_bytes,
        file_name="student_performance_cleaned.csv",
        mime="text/csv",
    )

with st.expander("Data quality summary"):
    quality = pd.DataFrame({
        "Check": ["Rows in uploaded data", "Rows after cleaning", "Duplicates removed"],
        "Result": [len(raw), len(df), max(len(raw) - len(df), 0)],
    })
    st.dataframe(quality, hide_index=True, use_container_width=True)

st.markdown("---")
st.caption("Built with Python, Pandas, Plotly and Streamlit.")
