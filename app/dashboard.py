import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ---------- Page setup ----------
st.set_page_config(page_title="EduPro Instructor Analytics", layout="wide")
sns.set_style("whitegrid")

# ---------- Load data ----------
DATA_DIR = Path("data/processed")

@st.cache_data
def load_data():
    master = pd.read_csv(DATA_DIR / "teacher_course_master.csv")
    teacher_kpis = pd.read_csv(DATA_DIR / "teacher_kpis.csv")
    return master, teacher_kpis

master, teacher_kpis = load_data()

st.title("EduPro Instructor Performance & Course Quality Dashboard")
st.caption("Data-driven evaluation of instructor effectiveness and course quality on EduPro")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

expertise_options = sorted(master["Expertise"].unique())
selected_expertise = st.sidebar.multiselect(
    "Instructor Expertise", options=expertise_options, default=expertise_options
)

category_options = sorted(master["CourseCategory"].unique())
selected_categories = st.sidebar.multiselect(
    "Course Category", options=category_options, default=category_options
)

level_options = sorted(master["CourseLevel"].unique())
selected_levels = st.sidebar.multiselect(
    "Course Level", options=level_options, default=level_options
)

rating_range = st.sidebar.slider(
    "Teacher Rating Range",
    min_value=float(master["TeacherRating"].min()),
    max_value=float(master["TeacherRating"].max()),
    value=(float(master["TeacherRating"].min()), float(master["TeacherRating"].max())),
    step=0.1
)

# ---------- Apply filters ----------
filtered = master[
    (master["Expertise"].isin(selected_expertise)) &
    (master["CourseCategory"].isin(selected_categories)) &
    (master["CourseLevel"].isin(selected_levels)) &
    (master["TeacherRating"].between(rating_range[0], rating_range[1]))
]

if filtered.empty:
    st.warning("No data matches the current filters. Try widening your selection.")
    st.stop()

# ---------- KPI summary cards ----------
st.subheader("Platform Snapshot (based on current filters)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Teacher Rating", f"{filtered['TeacherRating'].mean():.2f}")
col2.metric("Avg Course Rating", f"{filtered['CourseRating'].mean():.2f}")
col3.metric("Total Enrollments", f"{filtered['Enrollments'].sum():,}")
col4.metric("Distinct Instructors", f"{filtered['TeacherID'].nunique()}")

st.divider()

# ---------- Instructor Leaderboard ----------
st.subheader("Instructor Performance Leaderboard")

leaderboard = (
    filtered.groupby(["TeacherID", "TeacherName", "Expertise"])
    .agg(
        TeacherRating=("TeacherRating", "first"),
        AvgCourseRating=("CourseRating", "mean"),
        TotalEnrollments=("Enrollments", "sum"),
        CoursesTaught=("CourseID", "nunique"),
    )
    .reset_index()
    .sort_values("TeacherRating", ascending=False)
)

st.dataframe(leaderboard, use_container_width=True, hide_index=True)

st.divider()

# ---------- Experience vs Rating scatter ----------
st.subheader("Experience vs Rating")

col_a, col_b = st.columns(2)

with col_a:
    fig, ax = plt.subplots(figsize=(5, 4))
    teacher_subset = teacher_kpis[teacher_kpis["TeacherID"].isin(filtered["TeacherID"])]
    sns.regplot(data=teacher_subset, x="YearsOfExperience", y="TeacherRating",
                scatter_kws={"alpha": 0.6}, line_kws={"color": "darkorange"}, ax=ax)
    ax.set_title("Experience vs Teacher Rating")
    st.pyplot(fig)

with col_b:
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    sns.regplot(data=filtered, x="YearsOfExperience", y="CourseRating",
                scatter_kws={"alpha": 0.3, "color": "seagreen"}, line_kws={"color": "darkorange"}, ax=ax2)
    ax2.set_title("Experience vs Course Rating")
    st.pyplot(fig2)

st.divider()

# ---------- Course Quality Heatmap ----------
st.subheader("Course Quality Heatmap (Category x Level)")

heatmap_data = filtered.pivot_table(
    index="CourseCategory", columns="CourseLevel", values="CourseRating", aggfunc="mean"
)
fig3, ax3 = plt.subplots(figsize=(8, 6))
sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="YlGnBu", ax=ax3)
ax3.set_title("Average Course Rating by Category and Level")
st.pyplot(fig3)

st.divider()

# ---------- Expertise-wise performance comparison ----------
st.subheader("Expertise-wise Performance Comparison")

expertise_perf = (
    filtered.groupby("Expertise")
    .agg(AvgCourseRating=("CourseRating", "mean"), NumPairs=("CourseRating", "count"))
    .reset_index()
    .sort_values("AvgCourseRating", ascending=False)
)

fig4, ax4 = plt.subplots(figsize=(8, 5))
sns.barplot(data=expertise_perf, x="AvgCourseRating", y="Expertise",
            hue="Expertise", palette="viridis", legend=False, ax=ax4)
ax4.set_title("Average Course Rating by Expertise")
st.pyplot(fig4)

st.caption("Note: Small sample sizes (few distinct teachers) in some expertise areas "
           "should be interpreted with caution.")