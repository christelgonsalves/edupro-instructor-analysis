"""
Script: 01_load_and_validate.py
Purpose: Load raw EduPro data, validate its integrity, and save clean CSVs
         for downstream analysis scripts.
"""

import pandas as pd
from pathlib import Path

# ---- Paths (relative to project root) ----
RAW_FILE = Path("data/raw/EduPro_Online_Platform.xlsx")
PROCESSED_DIR = Path("data/processed")
REPORT_PATH = Path("outputs/reports/01_validation_report.txt")

report_lines = []

def log(msg):
    """Print to console AND collect for the report file."""
    print(msg)
    report_lines.append(str(msg))

log("=" * 60)
log("STEP 1: LOADING RAW DATA")
log("=" * 60)

xl = pd.ExcelFile(RAW_FILE)
log(f"Sheets found: {xl.sheet_names}")

teachers = xl.parse("Teachers")
courses = xl.parse("Courses")
transactions = xl.parse("Transactions")
users = xl.parse("Users")

tables = {
    "Teachers": teachers,
    "Courses": courses,
    "Transactions": transactions,
    "Users": users,
}

log("\n" + "=" * 60)
log("STEP 2: BASIC HEALTH CHECK PER TABLE")
log("=" * 60)

for name, df in tables.items():
    log(f"\n--- {name} ---")
    log(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    log(f"Columns: {list(df.columns)}")
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    log(f"Total missing values: {total_nulls}")
    if total_nulls > 0:
        log(f"Nulls by column:\n{null_counts[null_counts > 0]}")

log("\n" + "=" * 60)
log("STEP 3: PRIMARY KEY UNIQUENESS CHECK")
log("=" * 60)

for name, df, key in [
    ("Teachers", teachers, "TeacherID"),
    ("Courses", courses, "CourseID"),
    ("Users", users, "UserID"),
    ("Transactions", transactions, "TransactionID"),
]:
    n_total = len(df)
    n_unique = df[key].nunique()
    status = "OK - all unique" if n_total == n_unique else "PROBLEM - duplicates found!"
    log(f"{name}.{key}: {n_unique} unique out of {n_total} rows -> {status}")

log("\n" + "=" * 60)
log("STEP 4: REFERENTIAL INTEGRITY CHECK")
log("=" * 60)

teacher_ids_valid = transactions["TeacherID"].isin(teachers["TeacherID"]).all()
course_ids_valid = transactions["CourseID"].isin(courses["CourseID"]).all()
user_ids_valid = transactions["UserID"].isin(users["UserID"]).all()

log(f"All Transaction.TeacherID values exist in Teachers: {teacher_ids_valid}")
log(f"All Transaction.CourseID values exist in Courses: {course_ids_valid}")
log(f"All Transaction.UserID values exist in Users: {user_ids_valid}")

log("\n" + "=" * 60)
log("STEP 5: TEACHER-COURSE RELATIONSHIP STRUCTURE")
log("=" * 60)

teachers_per_course = transactions.groupby("CourseID")["TeacherID"].nunique()
courses_per_teacher = transactions.groupby("TeacherID")["CourseID"].nunique()

log(f"Distinct teachers linked per course - min: {teachers_per_course.min()}, "
    f"max: {teachers_per_course.max()}, mean: {teachers_per_course.mean():.2f}")
log(f"Distinct courses linked per teacher - min: {courses_per_teacher.min()}, "
    f"max: {courses_per_teacher.max()}, mean: {courses_per_teacher.mean():.2f}")
log("\nNote: This confirms a many-to-many relationship between Teachers and "
    "Courses via Transactions. Analysis of teaching quality will use DISTINCT "
    "(TeacherID, CourseID) pairs to avoid double-counting, while raw "
    "Transactions will be used only for counting enrollments.")

log("\n" + "=" * 60)
log("STEP 6: SAVING CLEAN CSVs TO data/processed/")
log("=" * 60)

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

teachers.to_csv(PROCESSED_DIR / "teachers.csv", index=False)
courses.to_csv(PROCESSED_DIR / "courses.csv", index=False)
transactions.to_csv(PROCESSED_DIR / "transactions.csv", index=False)
users.to_csv(PROCESSED_DIR / "users.csv", index=False)

log("Saved: teachers.csv, courses.csv, transactions.csv, users.csv")

# ---- Write report file ----
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT_PATH, "w") as f:
    f.write("\n".join(report_lines))

log(f"\nValidation report saved to: {REPORT_PATH}")
log("\nDONE. Ready for Step 2: Building the analysis-ready merged dataset.")