import pandas as pd
import joblib
from datetime import datetime
from pathlib import Path

# Resolve the pipeline path relative to this file
HERE = Path(__file__).parent
SRC = HERE.parent / "src"
PIPELINE_PATH = SRC / "fraud_detection_pipeline.joblib"

def parse_date(dt_str):
    s = str(dt_str).strip()
    fmts = [
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d %I:%M %p',
        '%Y-%m-%d %I:%M %p %Z',
        '%d-%m-%Y %H:%M',
        '%d-%m-%Y %I:%M %p',
        '%d-%m-%Y %I:%M %p %Z',
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # Fallback to pandas parser
    try:
        return pd.to_datetime(s, dayfirst=True).to_pydatetime()
    except Exception:
        return pd.NaT

def test(data_path: str):
    # Support .csc extension typo
    if data_path.lower().endswith('.csc'):
        data_path = data_path[:-4] + '.csv'
    # 1) Load model
    pipeline = joblib.load(PIPELINE_PATH)

    # 2) Read CSV
    df = pd.read_csv(data_path)

    # 3) Parse times and compute time_diff_hrs
    df['Time of incident'] = df['Time of incident'].map(parse_date)
    df['Time of claim']    = df['Time of claim'].map(parse_date)
    df['time_diff_hrs']    = (
        df['Time of claim'] - df['Time of incident']
    ).dt.total_seconds() / 3600

    # 4) Prepare features and impute
    feats = [
        'Policy status',
        'License',
        'Driver age',
        'drunk driving',
        'FIR filed?',
        'No. of previous claims',
        'time_diff_hrs'
    ]
    X_new = df[feats].copy()
    X_new['Policy status'].fillna('Unknown', inplace=True)
    X_new['License'].fillna('Unknown', inplace=True)
    X_new['drunk driving'].fillna('No', inplace=True)
    X_new['FIR filed?'].fillna('No', inplace=True)
    X_new['Driver age'].fillna(X_new['Driver age'].median(), inplace=True)
    X_new['No. of previous claims'].fillna(0, inplace=True)
    X_new['time_diff_hrs'].fillna(X_new['time_diff_hrs'].median(), inplace=True)

    # 5) Predict probabilities
    proba = pipeline.predict_proba(X_new)

    # 6) Build summary stats
    total = len(df)

    # auto-detect original claim column name
    orig_col = None
    for c in df.columns:
        if c.lower().startswith('original') and 'claim' in c.lower():
            orig_col = c
            break
    if orig_col is None:
        raise KeyError(
            f"Could not find original-claim column in {df.columns.tolist()}"
        )

    actual_g = (df[orig_col] == 'Genuine Claim').sum()
    pred_g   = (proba[:,1] >= proba[:,0]).sum()
    actual_f = total - actual_g
    pred_f   = total - pred_g
    # correct predictions
    preds    = ['Genuine Claim' if p[1]>=p[0] else 'Fraud Claim' for p in proba]
    correct  = (df[orig_col] == preds).sum()
    incorrect = total - correct
    accuracy = correct / total * 100

    # 7) Write the summary TXT next to the CSV
    data_path_obj = Path(data_path)
    summary_path  = data_path_obj.parent / f"{data_path_obj.stem}_Prediction_summary.txt"

    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"Total Records: {total}\n\n")
        f.write(f"Actual Genuine Claims: {actual_g}\n")
        f.write(f"Predicted Genuine Claims: {pred_g}\n\n")
        f.write(f"Actual Fraud Claims: {actual_f}\n")
        f.write(f"Predicted Fraud Claims: {pred_f}\n\n")
        f.write(f"Correctly Predicted: {correct}\n")
        f.write(f"Incorrectly Predicted: {incorrect}\n\n")
        f.write(f"Accuracy of the Model is: {accuracy:.2f}%\n")

    print("✅ Summary written to", summary_path)
