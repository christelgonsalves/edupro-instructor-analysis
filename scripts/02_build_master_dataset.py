"""
Script: 02_build_master_dataset.py
Purpose: Build the analysis-ready master dataset by combining Teachers,
         Courses, and Transactions - using DISTINCT (TeacherID, CourseID)
         pairs to avoid double-counting, as decided in Step 4.
"""

import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
REPORT_PATH = Path("outputs/reports/02_master_dataset_report.txt")

report_lines = []

def log(msg):
    print(msg)
    report_lines.append(str(msg))

log("=" * 60)
log("LOADING CLEAN CSVs")
log("=" * 60)

teachers = pd.read_csv(PROCESSED_DIR / "teachers.csv")
courses = pd.read_csv(PROCESSED_DIR / "courses.csv")
transactions = pd.read_csv(PROCESSED_DIR / "transactions.csv")

log(f"Teachers: {teachers.shape}, Courses: {courses.shape}, Transactions: {transactions.shape}")

log("\n" + "=" * 60)
log("STEP 1: COUNT ENROLLMENTS PER (TeacherID, CourseID) PAIR")
log("=" * 60)

# Each transaction = 1 enrollment. Count enrollments per teacher-course pairing.
engagement_counts = (
    transactions
    .groupby(["TeacherID", "CourseID"])
    .size()
    .reset_index(name="Enrollments")
)

log(f"Distinct (TeacherID, CourseID) pairs found: {engagement_counts.shape[0]}")
log(f"Enrollment count per pair - min: {engagement_counts['Enrollments'].min()}, "
    f"max: {engagement_counts['Enrollments'].max()}, "
    f"mean: {engagement_counts['Enrollments'].mean():.2f}")

log("\n" + "=" * 60)
log("STEP 2: BUILD MASTER TEACHING-ENGAGEMENT TABLE")
log("=" * 60)

# Merge in teacher details, then course details
master = engagement_counts.merge(teachers, on="TeacherID", how="left")
master = master.merge(courses, on="CourseID", how="left")

log(f"Master table shape: {master.shape}")
log(f"Master table columns: {list(master.columns)}")

# Sanity check: no nulls should appear after merge (would indicate a broken join)
null_after_merge = master.isnull().sum().sum()
log(f"Total nulls after merge (should be 0): {null_after_merge}")

master_path = PROCESSED_DIR / "teacher_course_master.csv"
master.to_csv(master_path, index=False)
log(f"Saved: {master_path}")

log("\n" + "=" * 60)
log("STEP 3: BUILD TEACHER-LEVEL SUMMARY TABLE")
log("=" * 60)

teacher_summary = (
    master.groupby("TeacherID")
    .agg(
        TeacherName=("TeacherName", "first"),
        Age=("Age_x", "first") if "Age_x" in master.columns else ("Age", "first"),
        Gender=("Gender_x", "first") if "Gender_x" in master.columns else ("Gender", "first"),
        Expertise=("Expertise", "first"),
        YearsOfExperience=("YearsOfExperience", "first"),
        TeacherRating=("TeacherRating", "first"),
        DistinctCoursesTaught=("CourseID", "nunique"),
        TotalEnrollments=("Enrollments", "sum"),
    )
    .reset_index()
)

log(f"Teacher summary shape: {teacher_summary.shape}")
teacher_summary_path = PROCESSED_DIR / "teacher_summary.csv"
teacher_summary.to_csv(teacher_summary_path, index=False)
log(f"Saved: {teacher_summary_path}")

log("\n" + "=" * 60)
log("STEP 4: BUILD COURSE-LEVEL SUMMARY TABLE")
log("=" * 60)

course_summary = (
    master.groupby("CourseID")
    .agg(
        CourseName=("CourseName", "first"),
        CourseCategory=("CourseCategory", "first"),
        CourseLevel=("CourseLevel", "first"),
        CourseRating=("CourseRating", "first"),
        DistinctTeachers=("TeacherID", "nunique"),
        TotalEnrollments=("Enrollments", "sum"),
    )
    .reset_index()
)

log(f"Course summary shape: {course_summary.shape}")
course_summary_path = PROCESSED_DIR / "course_summary.csv"
course_summary.to_csv(course_summary_path, index=False)
log(f"Saved: {course_summary_path}")

# ---- Write report ----
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT_PATH, "w") as f:
    f.write("\n".join(report_lines))

log(f"\nReport saved to: {REPORT_PATH}")
log("\nDONE. Ready for Step 6: KPI calculations.")