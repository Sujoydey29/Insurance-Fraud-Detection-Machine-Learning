import pandas as pd
import pathlib
import joblib
from datetime import datetime
import time
import os

# Paths
PIPELINE_PATH    = 'fraud_detection_pipeline.joblib'
DATA_PATH_2      = '../data/Testing_10000_dataset.csv'
DATA_PATH_1      = '../data/Testing_30000_dataset.csv'
OUTPUT_CSV_PATH  = '../data/'

def parse_date(dt_str):
    """
    Try parsing as YYYY-MM-DD HH:MM, then DD-MM-YYYY HH:MM,
    then fall back to pandas' default (dayfirst=True).
    """
    s = str(dt_str).strip()
    for fmt in ("%Y-%m-%d %H:%M", "%d-%m-%Y %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    # fallback without deprecated infer_datetime_format
    return pd.to_datetime(s, dayfirst=True).to_pydatetime()

def test(data_path):

    # Load model and data
    pipeline = joblib.load(PIPELINE_PATH)
    df = pd.read_csv(data_path)
    summary_txt_path = data_path[:-4] + '_Prediction_summary.txt'
    out_csv_path = data_path[:-4] + '_Results.csv'

    # 1) Parse datetimes
    df['Time of incident'] = df['Time of incident'].map(parse_date)
    df['Time of claim']    = df['Time of claim'].map(parse_date)

    # 2) Compute time difference (hours)
    df['time_diff_hrs'] = (
        df['Time of claim'] - df['Time of incident']
    ).dt.total_seconds() / 3600

    # 3) Select features and copy
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

    # 4) Impute missing values (no chained assignment)
    X_new['Policy status']          = X_new['Policy status'].fillna('Unknown')
    X_new['License']                = X_new['License'].fillna('Unknown')
    X_new['drunk driving']          = X_new['drunk driving'].fillna('No')
    X_new['FIR filed?']             = X_new['FIR filed?'].fillna('No')
    X_new['Driver age']             = X_new['Driver age'].fillna(X_new['Driver age'].median())
    X_new['No. of previous claims'] = X_new['No. of previous claims'].fillna(0)
    X_new['time_diff_hrs']          = X_new['time_diff_hrs'].fillna(X_new['time_diff_hrs'].median())

    # 5) Predict
    proba = pipeline.predict_proba(X_new)
    df['Model Predicted Output'] = [
        'Genuine Claim' if p[1] >= p[0] else 'Fraud Claim'
        for p in proba
    ]

    # 6) Clean out old results
    for p in (out_csv_path, summary_txt_path):
        try: os.remove(p)
        except OSError: pass

    # 7) Save predictions
    out = df[[
        'policy_id',
        'Policy status',
        'Original Claim status',
        'Model Predicted Output'
    ]]
    out.to_csv(out_csv_path, index=False)

    # 8) Build summary stats
    total     = len(out)
    actual_g  = (out['Original Claim status'] == 'Genuine Claim').sum()
    pred_g    = (out['Model Predicted Output'] == 'Genuine Claim').sum()
    actual_f  = total - actual_g
    pred_f    = total - pred_g
    correct   = (out['Original Claim status'] == out['Model Predicted Output']).sum()
    incorrect = total - correct
    gen_as_f  = ((out['Original Claim status']=='Genuine Claim') & (out['Model Predicted Output']=='Fraud Claim')).sum()
    fraud_as_g= ((out['Original Claim status']=='Fraud Claim') & (out['Model Predicted Output']=='Genuine Claim')).sum()
    accuracy  = correct / total * 100

    # 9) Write summary (UTF-8 to support arrows)
    with open(summary_txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Total Records: {total}\n\n")
        f.write(f"Actual Genuine Claims: {actual_g}\n")
        f.write(f"Predicted Genuine Claims: {pred_g}\n\n")
        f.write(f"Actual Fraud Claims: {actual_f}\n")
        f.write(f"Predicted Fraud Claims: {pred_f}\n\n")
        f.write(f"Correctly Predicted: {correct}\n")
        f.write(f"Incorrectly Predicted: {incorrect}\n\n")
        f.write(f"Genuine → Fraud: {gen_as_f}\n")
        f.write(f"Fraud → Genuine: {fraud_as_g}\n\n")
        f.write(f"Accuracy of the Model: {accuracy:.2f}%\n")

    # 10) Print out file URIs
    print("✅ Done!")
    print("📄 Results:", pathlib.Path(out_csv_path).absolute().as_uri())
    print("📝 Summary:", pathlib.Path(summary_txt_path).absolute().as_uri())

if __name__ == "__main__":
    # Run on whichever dataset you need:
    test(DATA_PATH_2)
    test(DATA_PATH_1)
