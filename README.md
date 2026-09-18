# EduPro Instructor Performance & Course Quality Evaluation

Data-driven analysis of instructor effectiveness and course quality on EduPro, an online education platform.

## Key Questions
1. Which instructors consistently deliver high-quality courses?
2. Does experience translate to better ratings?
3. Are some categories more instructor-dependent than others?
4. How evenly is teaching performance distributed?

## Key Findings
- Course quality is largely **decoupled** from instructor characteristics (personal rating, experience, expertise match) — likely driven more by curriculum/content design.
- High-rated instructors drive significantly more enrollment (~4x low-rated tier), but this does **not** correspond to better course ratings — a business risk worth flagging.
- Experience builds personal teaching reputation (moderate correlation with TeacherRating) but has no meaningful effect on CourseRating.

## Project Structure
- `scripts/` — data pipeline: loading, KPI calculation, EDA, tier/expertise analysis
- `data/processed/` — cleaned and derived datasets
- `outputs/figures/`, `outputs/reports/` — charts and text reports
- `app/dashboard.py` — interactive Streamlit dashboard

## Running Locally