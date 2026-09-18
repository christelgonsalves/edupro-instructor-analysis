"""
Script: 06_instructor_tiers.py
Purpose: Bucket teachers into High/Mid/Low rating tiers and compare
         enrollment and course rating outcomes across tiers.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
FIGURES_DIR = Path("outputs/figures")
REPORT_PATH = Path("outputs/reports/06_instructor_tiers_report.txt")

report_lines = []

def log(msg):
    print(msg)
    report_lines.append(str(msg))

teacher_kpis = pd.read_csv(PROCESSED_DIR / "teacher_kpis.csv")
master = pd.read_csv(PROCESSED_DIR / "teacher_course_master.csv")

log("=" * 60)
log("BUCKETING TEACHERS INTO RATING TIERS")
log("=" * 60)

# qcut splits into 3 equal-sized groups based on TeacherRating value ranking
teacher_kpis["RatingTier"] = pd.qcut(
    teacher_kpis["TeacherRating"], q=3, labels=["Low", "Mid", "High"]
)

tier_counts = teacher_kpis["RatingTier"].value_counts().reindex(["Low", "Mid", "High"])
log(f"Teachers per tier:\n{tier_counts}")

# Show the rating boundaries used, for transparency
tier_ranges = teacher_kpis.groupby("RatingTier", observed=True)["TeacherRating"].agg(["min", "max"])
log(f"\nRating range per tier:\n{tier_ranges}")

log("\n" + "=" * 60)
log("ENROLLMENT COMPARISON ACROSS TIERS")
log("=" * 60)

enrollment_by_tier = teacher_kpis.groupby("RatingTier", observed=True).agg(
    AvgEnrollmentsPerCourse=("AvgEnrollmentsPerCourse", "mean"),
    AvgEnrollmentInfluenceRatio=("EnrollmentInfluenceRatio", "mean"),
    NumTeachers=("TeacherID", "count")
)
log(f"\n{enrollment_by_tier}")

log("\n" + "=" * 60)
log("COURSE RATING COMPARISON ACROSS TIERS")
log("=" * 60)

# Bring RatingTier into the master (teacher-course) table for course-rating comparison
master_with_tier = master.merge(
    teacher_kpis[["TeacherID", "RatingTier"]], on="TeacherID", how="left"
)
course_rating_by_tier = master_with_tier.groupby("RatingTier", observed=True)["CourseRating"].agg(
    ["mean", "std", "count"]
)
log(f"\n{course_rating_by_tier}")

# Save results
enrollment_by_tier.to_csv(PROCESSED_DIR / "enrollment_by_tier.csv")
course_rating_by_tier.to_csv(PROCESSED_DIR / "course_rating_by_tier.csv")
teacher_kpis.to_csv(PROCESSED_DIR / "teacher_kpis.csv", index=False)  # now includes RatingTier
log("\nSaved: enrollment_by_tier.csv, course_rating_by_tier.csv")
log("Updated teacher_kpis.csv to include RatingTier column")

# ---- Chart: Enrollment by tier ----
plt.figure(figsize=(7, 5))
sns.barplot(
    data=teacher_kpis, x="RatingTier", y="AvgEnrollmentsPerCourse",
    order=["Low", "Mid", "High"], hue="RatingTier", palette="Blues", legend=False
)
plt.title("Average Enrollments per Course by Instructor Rating Tier", fontsize=13, fontweight="bold")
plt.xlabel("Instructor Rating Tier")
plt.ylabel("Avg Enrollments per Course")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "06_enrollments_by_tier.png")
plt.close()
log("Saved chart: 06_enrollments_by_tier.png")

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT_PATH, "w") as f:
    f.write("\n".join(report_lines))

log(f"\nReport saved to: {REPORT_PATH}")
log("\nDONE. Ready for Step 10: Expertise-based analysis.")