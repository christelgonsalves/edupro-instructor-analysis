"""
Script: 04_eda_charts.py
Purpose: Generate foundational EDA charts answering Key Questions 1-3.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
FIGURES_DIR = Path("outputs/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Consistent visual style for all charts in this project
sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 120

teachers = pd.read_csv(PROCESSED_DIR / "teachers.csv")
master = pd.read_csv(PROCESSED_DIR / "teacher_course_master.csv")

print("Data loaded. Generating charts...")

# ---- Chart 1: Instructor Rating Distribution ----
plt.figure(figsize=(8, 5))
sns.histplot(teachers["TeacherRating"], bins=15, kde=True, color="steelblue")
plt.title("Distribution of Instructor Ratings", fontsize=14, fontweight="bold")
plt.xlabel("Teacher Rating (out of 5)")
plt.ylabel("Number of Teachers")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "01_instructor_rating_distribution.png")
plt.close()
print("Saved: 01_instructor_rating_distribution.png")

# ---- Chart 2: Experience vs Teacher Rating ----
plt.figure(figsize=(8, 5))
sns.regplot(
    data=teachers, x="YearsOfExperience", y="TeacherRating",
    scatter_kws={"alpha": 0.6, "color": "steelblue"},
    line_kws={"color": "darkorange"}
)
plt.title("Experience vs Teacher Rating (r = 0.598)", fontsize=14, fontweight="bold")
plt.xlabel("Years of Experience")
plt.ylabel("Teacher Rating (out of 5)")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "02_experience_vs_teacher_rating.png")
plt.close()
print("Saved: 02_experience_vs_teacher_rating.png")

# ---- Chart 3: Experience vs Course Rating ----
plt.figure(figsize=(8, 5))
sns.regplot(
    data=master, x="YearsOfExperience", y="CourseRating",
    scatter_kws={"alpha": 0.3, "color": "seagreen"},
    line_kws={"color": "darkorange"}
)
plt.title("Experience vs Course Rating (r = -0.013)", fontsize=14, fontweight="bold")
plt.xlabel("Years of Experience")
plt.ylabel("Course Rating (out of 5)")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "03_experience_vs_course_rating.png")
plt.close()
print("Saved: 03_experience_vs_course_rating.png")

# ---- Chart 4: Course Rating by Category ----
plt.figure(figsize=(10, 6))
category_order = (
    master.groupby("CourseCategory")["CourseRating"]
    .median()
    .sort_values(ascending=False)
    .index
)
sns.boxplot(
    data=master, x="CourseRating", y="CourseCategory",
    order=category_order, hue="CourseCategory", palette="viridis", legend=False
)
plt.title("Course Rating Distribution by Category", fontsize=14, fontweight="bold")
plt.xlabel("Course Rating (out of 5)")
plt.ylabel("Course Category")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "04_course_rating_by_category.png")
plt.close()
print("Saved: 04_course_rating_by_category.png")

print("\nDONE. All 4 charts saved to outputs/figures/")