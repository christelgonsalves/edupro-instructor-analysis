"""
Script: 07_expertise_analysis.py
Purpose: Analyze whether teaching within one's stated expertise produces
         better course outcomes than teaching outside it, and rank
         expertise areas by course quality delivered.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
FIGURES_DIR = Path("outputs/figures")
REPORT_PATH = Path("outputs/reports/07_expertise_report.txt")

report_lines = []

def log(msg):
    print(msg)
    report_lines.append(str(msg))

master = pd.read_csv(PROCESSED_DIR / "teacher_course_master.csv")

log("=" * 60)
log("IN-EXPERTISE vs OUT-OF-EXPERTISE ANALYSIS")
log("=" * 60)

master["InExpertise"] = master["Expertise"] == master["CourseCategory"]

match_rate = master["InExpertise"].mean()
log(f"Percentage of teaching engagements within stated expertise: {match_rate*100:.1f}%")

expertise_comparison = master.groupby("InExpertise")["CourseRating"].agg(
    ["mean", "std", "count"]
)
log(f"\nCourse Rating: In-Expertise vs Out-of-Expertise\n{expertise_comparison}")

diff = (
    expertise_comparison.loc[True, "mean"] - expertise_comparison.loc[False, "mean"]
    if True in expertise_comparison.index and False in expertise_comparison.index
    else None
)
if diff is not None:
    log(f"\nDifference (In-Expertise minus Out-of-Expertise): {diff:+.3f} rating points")

master.to_csv(PROCESSED_DIR / "teacher_course_master.csv", index=False)  # save with new column

log("\n" + "=" * 60)
log("EXPERTISE AREA RANKING (by avg CourseRating of courses taught)")
log("=" * 60)

expertise_ranking = master.groupby("Expertise").agg(
    AvgCourseRating=("CourseRating", "mean"),
    StdCourseRating=("CourseRating", "std"),
    AvgTeacherRating=("TeacherRating", "mean"),
    NumTeachingPairs=("CourseRating", "count"),
    NumDistinctTeachers=("TeacherID", "nunique"),
).sort_values("AvgCourseRating", ascending=False).reset_index()

log(f"\n{expertise_ranking.to_string(index=False)}")

expertise_ranking.to_csv(PROCESSED_DIR / "expertise_ranking.csv", index=False)
log("\nSaved: expertise_ranking.csv")

# ---- Chart 1: In-expertise vs out-of-expertise ----
plt.figure(figsize=(6, 5))
plot_data = expertise_comparison.reset_index()
plot_data["InExpertise"] = plot_data["InExpertise"].map({True: "In Expertise", False: "Out of Expertise"})
sns.barplot(
    data=plot_data, x="InExpertise", y="mean",
    hue="InExpertise", palette=["indianred", "seagreen"], legend=False
)
plt.title("Course Rating: In-Expertise vs Out-of-Expertise Teaching", fontsize=12, fontweight="bold")
plt.xlabel("")
plt.ylabel("Average Course Rating")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "07a_in_vs_out_expertise.png")
plt.close()
log("Saved chart: 07a_in_vs_out_expertise.png")

# ---- Chart 2: Expertise area ranking ----
plt.figure(figsize=(10, 6))
sns.barplot(
    data=expertise_ranking, x="AvgCourseRating", y="Expertise",
    hue="Expertise", palette="viridis", legend=False,
    order=expertise_ranking["Expertise"]
)
plt.title("Average Course Rating by Instructor Expertise Area", fontsize=13, fontweight="bold")
plt.xlabel("Average Course Rating")
plt.ylabel("Expertise Area")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "07b_expertise_ranking.png")
plt.close()
log("Saved chart: 07b_expertise_ranking.png")

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT_PATH, "w") as f:
    f.write("\n".join(report_lines))

log(f"\nReport saved to: {REPORT_PATH}")
log("\nDONE. Core EDA complete. Ready for Step 11: Streamlit dashboard.")