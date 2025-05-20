# Part 3: Tkinter GUI for Live Prediction

import pandas as pd
import joblib
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# ----- Load Model & Data -----
PIPELINE_PATH = 'fraud_detection_pipeline.joblib'
DATA_PATH     = '../data/final_dataset.csv'

pipeline = joblib.load(PIPELINE_PATH)
df_all   = pd.read_csv(DATA_PATH)

# ----- Helper to compute time difference in hours -----
def compute_time_diff(inc_str, claim_str):
    # Remove trailing " IST"
    inc = datetime.strptime(inc_str.replace(' IST',''), '%Y-%m-%d %I:%M %p')
    clm = datetime.strptime(claim_str.replace(' IST',''), '%Y-%m-%d %I:%M %p')
    return (clm - inc).total_seconds() / 3600.0

# ----- GUI Setup -----
root = tk.Tk()
root.title("Insurance Fraud Detection")

# Input fields
fields = {
    'Policy ID':     tk.StringVar(),
    'Policy status': tk.StringVar(value='active'),
    'License':       tk.StringVar(value='Yes'),
    'Driver age':    tk.StringVar(value='25'),
    'drunk driving': tk.StringVar(value='No'),
    'FIR filed?':    tk.StringVar(value='Yes'),
    'No. of previous claims': tk.StringVar(value='0'),
    'Time of incident': tk.StringVar(value='2024-01-01 12:00 PM IST'),
    'Time of claim':    tk.StringVar(value='2024-01-01 01:00 PM IST'),
}

# Layout labels and widgets
row = 0
for label, var in fields.items():
    ttk.Label(root, text=label + ":").grid(column=0, row=row, sticky=tk.W, padx=5, pady=3)
    if label in ['Policy status', 'License', 'drunk driving', 'FIR filed?']:
        opts = ['active','inactive'] if label=='Policy status' else ['Yes','No']
        ttk.Combobox(root, textvariable=var, values=opts, state='readonly').grid(column=1, row=row, padx=5, pady=3)
    else:
        ttk.Entry(root, textvariable=var, width=25).grid(column=1, row=row, padx=5, pady=3)
    row += 1

# ----- Actions -----
def load_policy():
    pid = fields['Policy ID'].get().strip()
    if not pid:
        messagebox.showwarning("Input Error", "Please enter a Policy ID to load.")
        return
    row_data = df_all[df_all['policy_id']==pid]
    if row_data.empty:
        messagebox.showinfo("Not Found", f"No record found for Policy ID '{pid}'.")
        return
    row_data = row_data.iloc[0]
    # Populate fields
    fields['Policy status'].set(row_data['Policy status'])
    fields['License'].set(row_data['License'])
    fields['Driver age'].set(str(int(row_data['Driver age'])))
    fields['drunk driving'].set(row_data['drunk driving'])
    fields['FIR filed?'].set(row_data['FIR filed?'])
    fields['No. of previous claims'].set(str(int(row_data['No. of previous claims'])))
    fields['Time of incident'].set(row_data['Time of incident'])
    fields['Time of claim'].set(row_data['Time of claim'])

def predict_claim():
    try:
        data = {
            'Policy status': [fields['Policy status'].get()],
            'License':       [fields['License'].get()],
            'Driver age':    [int(fields['Driver age'].get())],
            'drunk driving': [fields['drunk driving'].get()],
            'FIR filed?':    [fields['FIR filed?'].get()],
            'No. of previous claims': [int(fields['No. of previous claims'].get())],
            'time_diff_hrs': [compute_time_diff(fields['Time of incident'].get(),
                                                fields['Time of claim'].get())]
        }
        X_new = pd.DataFrame(data)
        proba = pipeline.predict_proba(X_new)[0]
        if proba[1] >= 0.90:
            pred_label = 'Genuine Claim'
        elif proba[0] >= 0.50:
            pred_label = 'Fraud Claim'
        else:
            pred_label = 'Need Further Investigation'
        
        # pred_label = 'Genuine Claim' if proba[1] >= proba[0] else 'Fraud Claim'
        msg = (f"Genuine Claim probability: {proba[1]*100:.1f}%\n"
               f"Fraud Claim probability:   {proba[0]*100:.1f}%")
        messagebox.showinfo(
            # "Prediction Result",
            f"Predicted : {pred_label}\n\n",
            msg
            )
    except Exception as e:
        messagebox.showerror("Prediction Error", str(e))

# Buttons
ttk.Button(root, text="Load by Policy ID", command=load_policy).grid(column=0, row=row, pady=8)
ttk.Button(root, text="Predict", command=predict_claim).grid(column=1, row=row, pady=8)

# Start GUI loop
root.mainloop()
