# Student Performance Analytics

An interactive Python dashboard for exploring student math, reading and writing scores.

## Features
- Upload CSV or Excel data
- Data validation, type conversion, duplicate removal and missing-row handling
- KPI metrics for student count and average subject scores
- Interactive filters for gender, lunch, test preparation and race/ethnicity
- Subject score comparisons by gender and test preparation
- Score distributions and correlation heatmap
- Automatically generated descriptive observations
- Downloadable cleaned/filtered CSV

## Dataset
Use the StudentsPerformance dataset with these columns:

- `gender`
- `race/ethnicity`
- `parental level of education`
- `lunch`
- `test preparation course`
- `math score`
- `reading score`
- `writing score`

The dataset is not bundled. Upload your CSV/XLSX in the app sidebar, or put it at:
`data/StudentsPerformance.csv`

## Run on Windows

1. Install Python 3.10 or newer from https://www.python.org/downloads/
2. Extract this project ZIP.
3. Open the extracted folder.
4. Click the folder address bar in File Explorer, type `cmd`, and press Enter.
5. Run:

```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
streamlit run app.py
```

If `py` does not work, try `python` instead.

6. A browser tab should open with the dashboard.
7. Upload `StudentsPerformance.csv` using the sidebar.

## Run on macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```text
student_performance_ai_project/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── .gitkeep
```

## Important interpretation note
The dashboard reports descriptive comparisons and correlations. These do not establish causation. Discuss limitations and avoid claiming that test preparation or lunch category causes score differences.

## Suggested next improvements
- Add hypothesis tests and confidence intervals
- Add a reproducible exploratory data analysis notebook
- Add unit tests for data cleaning
- Deploy the Streamlit app
