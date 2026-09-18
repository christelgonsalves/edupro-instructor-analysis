"""
Script: 03_calculate_kpis.py
Purpose: Calculate the 5 required KPIs:
         Average Teacher Rating, Average Course Rating,
         Rating Consistency Index, Experience Impact Score,
         Enrollment Influence Ratio.
"""

import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
REPORT_PATH = Path("outputs/reports/03_kpi_report.txt")

report_lines = []

def log(msg):
    print(msg)
    report_lines.append(str(msg))

teachers = pd.read_csv(PROCESSED_DIR / "teachers.csv")
courses = pd.read_csv(PROCESSED_DIR / "courses.csv")
master = pd.read_csv(PROCESSED_DIR / "teacher_course_master.csv")
teacher_summary = pd.read_csv(PROCESSED_DIR / "teacher_summary.csv")

log("=" * 60)
log("PLATFORM-LEVEL KPIs")
log("=" * 60)

# KPI 1: Average Teacher Rating
avg_teacher_rating = teachers["TeacherRating"].mean()
log(f"1. Average Teacher Rating: {avg_teacher_rating:.3f} (out of 5)")

# KPI 2: Average Course Rating
avg_course_rating = courses["CourseRating"].mean()
log(f"2. Average Course Rating: {avg_course_rating:.3f} (out of 5)")

# KPI 4: Experience Impact Score (platform-level correlations)
exp_vs_teacher_rating_corr = teachers["YearsOfExperience"].corr(teachers["TeacherRating"])
exp_vs_course_rating_corr = master["YearsOfExperience"].corr(master["CourseRating"])
log(f"4. Experience Impact Score:")
log(f"   - Correlation(YearsOfExperience, TeacherRating): {exp_vs_teacher_rating_corr:.3f}")
log(f"   - Correlation(YearsOfExperience, CourseRating):  {exp_vs_course_rating_corr:.3f}")
log(f"   (Range is -1 to 1. Near 0 = no relationship. "
    f"Positive = more experience associates with higher ratings.)")

log("\n" + "=" * 60)
log("PER-TEACHER KPIs (for leaderboard)")
log("=" * 60)

# KPI 3: Rating Consistency Index (per teacher)
# Std dev of CourseRating across all courses each teacher delivers
consistency = (
    master.groupby("TeacherID")["CourseRating"]
    .agg(CourseRatingStd="std", CourseRatingMean="mean", CoursesCount="count")
    .reset_index()
)
# A teacher linked to only 1 course has NaN std -> treat as perfectly consistent (std=0)
consistency["CourseRatingStd"] = consistency["CourseRatingStd"].fillna(0)
consistency["RatingConsistencyIndex"] = 1 / (1 + consistency["CourseRatingStd"])

log(f"Rating Consistency Index calculated for {consistency.shape[0]} teachers")
log(f"Index range: {consistency['RatingConsistencyIndex'].min():.3f} to "
    f"{consistency['RatingConsistencyIndex'].max():.3f}")

# KPI 5: Enrollment Influence Ratio (per teacher)
platform_avg_enrollments_per_course = (
    teacher_summary["TotalEnrollments"].sum() / teacher_summary["DistinctCoursesTaught"].sum()
)
teacher_summary["AvgEnrollmentsPerCourse"] = (
    teacher_summary["TotalEnrollments"] / teacher_summary["DistinctCoursesTaught"]
)
teacher_summary["EnrollmentInfluenceRatio"] = (
    teacher_summary["AvgEnrollmentsPerCourse"] / platform_avg_enrollments_per_course
)

log(f"\nPlatform average enrollments per course: {platform_avg_enrollments_per_course:.2f}")
log(f"Enrollment Influence Ratio range: "
    f"{teacher_summary['EnrollmentInfluenceRatio'].min():.2f} to "
    f"{teacher_summary['EnrollmentInfluenceRatio'].max():.2f}")

# ---- Combine into one final teacher KPI table ----
teacher_kpis = teacher_summary.merge(
    consistency[["TeacherID", "RatingConsistencyIndex", "CourseRatingMean"]],
    on="TeacherID", how="left"
)

teacher_kpis_path = PROCESSED_DIR / "teacher_kpis.csv"
teacher_kpis.to_csv(teacher_kpis_path, index=False)
log(f"\nSaved per-teacher KPI table: {teacher_kpis_path}")

# ---- Save platform-level KPIs as a small summary CSV too ----
platform_kpis = pd.DataFrame([{
    "AverageTeacherRating": avg_teacher_rating,
    "AverageCourseRating": avg_course_rating,
    "Experience_vs_TeacherRating_Correlation": exp_vs_teacher_rating_corr,
    "Experience_vs_CourseRating_Correlation": exp_vs_course_rating_corr,
    "PlatformAvgEnrollmentsPerCourse": platform_avg_enrollments_per_course,
}])
platform_kpis_path = PROCESSED_DIR / "platform_kpis.csv"
platform_kpis.to_csv(platform_kpis_path, index=False)
log(f"Saved platform-level KPI table: {platform_kpis_path}")

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT_PATH, "w") as f:
    f.write("\n".join(report_lines))

log(f"\nReport saved to: {REPORT_PATH}")
log("\nDONE. Ready for Step 7: First real charts (EDA visualizations).")
# Bonus: TeacherRating vs CourseRating correlation (Key Question #3)
teacher_vs_course_rating_corr = master["TeacherRating"].corr(master["CourseRating"])
log(f"\nBonus - Correlation(TeacherRating, CourseRating): {teacher_vs_course_rating_corr:.3f}")