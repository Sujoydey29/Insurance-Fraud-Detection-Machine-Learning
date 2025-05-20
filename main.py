#!/usr/bin/env python3
"""
Claim Status Predictor
 - direct lookup for existing Policy ID
 - logistic regression fallback for new entries
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import tkinter as tk
from tkinter import messagebox

# --- 1) Load & preprocess data ---
DATA_PATH = 'whole_new_dataset_claimstatus_24h.csv'
df = pd.read_csv(DATA_PATH)

# Normalize casing
df['License']       = df['License'].str.lower().map({'yes':'Yes','no':'No'})
df['drunk driving'] = df['drunk driving'].str.lower()
df['FIR filed?']    = df['FIR filed?'].str.lower().map({'yes':'Yes','no':'No'})
df['Policy status'] = df['Policy status'].str.lower()

# Map to flags
df['License_flag'] = df['License'].map({'Yes':1, 'No':0})
df['Drunk_flag']   = df['drunk driving'].map({'yes':1, 'no':0})
df['FIR_flag']     = df['FIR filed?'].map({'Yes':1, 'No':0})
df['Active_flag']  = df['Policy status'].map({'active':1, 'inactive':0})

# Target
df['Target'] = df['Claim status'].map({'genuine':1, 'fraud':0})

# Features & target
feature_cols = ['Driver age','License_flag','Drunk_flag',
                'No. of claims','FIR_flag','Active_flag']
X = df[feature_cols].astype(int)
y = df['Target'].astype(int)

# Train logistic regression on full data
model = LogisticRegression(max_iter=1000)
model.fit(X, y)


# --- 2) Build the GUI ---
root = tk.Tk()
root.title("Claim Status Predictor")

# Input labels
labels = [
    "Policy ID:",
    "Driver age:",
    "License (Yes/No):",
    "Drunk driving (yes/no):",
    "No. of claims:",
    "FIR filed? (Yes/No):",
    "Policy status (active/inactive):"
]
for i, txt in enumerate(labels):
    tk.Label(root, text=txt).grid(row=i, column=0, padx=5, pady=2, sticky='e')

# Input widgets
entry_pid    = tk.Entry(root); entry_pid.grid(row=0, column=1)
entry_age    = tk.Entry(root); entry_age.grid(row=1, column=1)

var_lic      = tk.StringVar(value='Yes')
tk.OptionMenu(root, var_lic, 'Yes','No').grid(row=2, column=1)

var_drunk    = tk.StringVar(value='no')
tk.OptionMenu(root, var_drunk, 'yes','no').grid(row=3, column=1)

entry_claims = tk.Entry(root); entry_claims.grid(row=4, column=1)

var_fir      = tk.StringVar(value='Yes')
tk.OptionMenu(root, var_fir, 'Yes','No').grid(row=5, column=1)

var_status   = tk.StringVar(value='active')
tk.OptionMenu(root, var_status, 'active','inactive').grid(row=6, column=1)


def predict_claim():
    pid = entry_pid.get().strip()
    # parse inputs
    try:
        age    = int(entry_age.get())
        claims = int(entry_claims.get())
    except ValueError:
        return messagebox.showerror("Input Error", "Age and No. of claims must be integers.")
    lic    = var_lic.get() == 'Yes'
    drunk  = var_drunk.get() == 'yes'
    fir    = var_fir.get() == 'Yes'
    active = var_status.get() == 'active'

    # 1) Direct lookup if ID exists
    match = df['policy_id'] == pid
    if match.any():
        actual = df.loc[match, 'Claim status'].iloc[0]
        return messagebox.showinfo(
            "Lookup Result",
            f"Policy ID: {pid}\nActual Claim status: {actual}"
        )

    # 2) Otherwise predict with logistic regression
    x_in = np.array([[age, int(lic), int(drunk), claims, int(fir), int(active)]])
    p_fraud, p_genuine = model.predict_proba(x_in)[0]
    pred_label = 'genuine' if p_genuine >= p_fraud else 'fraud'

    messagebox.showinfo(
        "Prediction Result",
        f"Policy ID: {pid}\n"
        f"Predicted: {pred_label}\n\n"
        f"P(genuine) = {p_genuine:.2f}\n"
        f"P(fraud)    = {p_fraud:.2f}"
    )

# Predict button
tk.Button(root, text="Predict Claim Status", command=predict_claim)\
  .grid(row=7, column=0, columnspan=2, pady=10)

root.mainloop()
