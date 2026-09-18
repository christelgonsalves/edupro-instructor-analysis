"""
Script: 05_category_instructor_dependency.py
Purpose: For each course category, measure how strongly TeacherRating
         correlates with CourseRating - i.e. how "instructor-dependent"
         that category's quality is.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
FIGURES_DIR = Path("outputs/figures")
REPORT_PATH = Path("outputs/reports/05_category_dependency_report.txt")

report_lines = []

def log(msg):
    print(msg)
    report_lines.append(str(msg))

master = pd.read_csv(PROCESSED_DIR / "teacher_course_master.csv")

log("=" * 60)
log("CATEGORY-LEVEL INSTRUCTOR DEPENDENCY ANALYSIS")
log("=" * 60)

results = []
for category, group in master.groupby("CourseCategory"):
    n_pairs = len(group)
    n_courses = group["CourseID"].nunique()
    n_teachers = group["TeacherID"].nunique()
    max_possible_pairs = n_courses * n_teachers
    fully_crossed = (n_pairs == max_possible_pairs)

    if fully_crossed:
        # Every teacher in this category teaches every course in it.
        # TeacherRating and CourseRating are mathematically orthogonal here -
        # correlation is undefined/meaningless by construction, not "zero relationship".
        corr = None
    else:
        corr = group["TeacherRating"].corr(group["CourseRating"])

    results.append({
        "CourseCategory": category,
        "TeacherCourseCorrelation": corr,
        "NumTeacherCoursePairs": n_pairs,
        "FullyCrossedDesign": fully_crossed
    })

dependency_df = pd.DataFrame(results).sort_values(
    "TeacherCourseCorrelation", ascending=False, na_position="last"
).reset_index(drop=True)

log("\nCategories ranked by Teacher-Course Rating correlation "
    "(higher = more instructor-dependent):\n")
log(dependency_df.to_string(index=False))

# Flag categories with small sample sizes so we don't over-interpret them
low_sample = dependency_df[dependency_df["NumTeacherCoursePairs"] < 30]
if not low_sample.empty:
    log(f"\nCAUTION: These categories have fewer than 30 teacher-course pairs, "
        f"so their correlation estimates are less reliable:")
    log(low_sample[["CourseCategory", "NumTeacherCoursePairs"]].to_string(index=False))

# Save results table
dependency_path = PROCESSED_DIR / "category_instructor_dependency.csv"
dependency_df.to_csv(dependency_path, index=False)
log(f"\nSaved: {dependency_path}")

# ---- Chart: bar chart of correlation by category ----
plt.figure(figsize=(10, 6))
colors = ["seagreen" if x >= 0 else "indianred" for x in dependency_df["TeacherCourseCorrelation"]]
sns.barplot(
    data=dependency_df, x="TeacherCourseCorrelation", y="CourseCategory",
    hue="CourseCategory", palette=colors, legend=False
)
plt.title("How Instructor-Dependent Is Each Category?\n(Correlation between Teacher Rating and Course Rating)",
          fontsize=13, fontweight="bold")
plt.xlabel("Correlation (Teacher Rating vs Course Rating)")
plt.ylabel("Course Category")
plt.axvline(0, color="black", linewidth=0.8)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "05_category_instructor_dependency.png")
plt.close()
log("Saved chart: 05_category_instructor_dependency.png")

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT_PATH, "w") as f:
    f.write("\n".join(report_lines))

log(f"\nReport saved to: {REPORT_PATH}")
log("\nDONE. Ready for Step 9: Instructor tiers vs enrollment analysis.")