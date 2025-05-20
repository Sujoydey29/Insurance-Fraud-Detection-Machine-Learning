#!/usr/bin/env python3
"""
Claim Status Predictor with Rule Lookup and Logistic Regression Fallback
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import tkinter as tk
from tkinter import messagebox

# --- Configuration ---
DATA_PATH = 'whole_new_dataset_claimstatus_24h.csv'   # Excel file with ground-truth
MODEL_PATH = 'claim_model.pkl'               # Saved logistic model (optional)

# --- 1. Load dataset ---
try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    raise SystemExit(f"Error: '{DATA_PATH}' not found")

# Standardize columns for rule lookup
df['License_flag'] = df['License'].str.lower().map({'yes': True, 'no': False})
df['Drunk_flag']   = df['drunk driving'].str.lower().map({'yes': True, 'no': False})
df['FIR_flag']     = df['FIR filed?'].str.lower().map({'yes': True, 'no': False})
df['Active_flag']  = df['Policy status'].str.lower().map({'active': True, 'inactive': False})

# Optional: Train logistic regression model on same features
feature_cols = ['Driver age', 'License_flag', 'Drunk_flag', 'No. of claims', 'FIR_flag', 'Active_flag']
X = df[feature_cols].astype(int)
y = df['Claim status'].map({'fraud':0, 'genuine':1})

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LogisticRegression(max_iter=1000).fit(X_train, y_train)

# --- GUI Definition ---
root = tk.Tk()
root.title("Claim Status Predictor")

# Helper: Boolean rule check
def check_rule(age, lic, drunk, claims, fir, active):
    return (
        active and lic and (18 <= age <= 95) and fir
        and (claims < 5) and (not drunk)
    )

# Prediction callback
def predict_claim():
    pid = entry_pid.get().strip()
    try:
        age    = int(entry_age.get())
        lic    = (var_lic.get().lower() == 'yes')
        drunk  = (var_drunk.get().lower() == 'yes')
        claims = int(entry_claims.get())
        fir    = (var_fir.get().lower() == 'yes')
        active = (var_status.get().lower() == 'active')
    except ValueError:
        return messagebox.showerror("Input Error", "Enter numeric age/claims and select Yes/No or active/inactive.")

    # 1) Lookup in DataFrame
    match = df['policy_id'] == pid
    if match.any():
        true_status = df.loc[match, 'Claim status'].iloc[0]
        return messagebox.showinfo("Lookup Result", f"Policy ID: {pid}\nActual Claim status: {true_status}")

    # 2) If not found, apply Boolean rule
    if check_rule(age, lic, drunk, claims, fir, active):
        label = 'genuine'
        prob_genuine = 1.0
    else:
        label = 'fraud'
        prob_genuine = 0.0
    prob_fraud = 1 - prob_genuine

    # 3) Fallback to logistic regression if desired
    # Uncomment below to use model probabilities instead of rule
    # inp = np.array([[age, lic, drunk, claims, fir, active]], dtype=int)
    # prob_genuine = model.predict_proba(inp)[0][1]
    # prob_fraud    = model.predict_proba(inp)[0][0]
    # label = 'genuine' if prob_genuine >= 0.5 else 'fraud'

    # Display
    messagebox.showinfo(
        "Prediction Result",
        f"Policy ID: {pid}\n"
        f"Predicted Claim status: {label}\n"
        f"P(genuine) = {prob_genuine:.2f}\n"
        f"P(fraud) = {prob_fraud:.2f}"
    )

# --- Build GUI Elements ---
labels = ["Policy ID:", "Driver age:", "License (Yes/No):",
          "Drunk driving (Yes/No):", "No. of claims:",
          "FIR filed? (Yes/No):", "Policy status (active/inactive):"]
for idx, text in enumerate(labels):
    tk.Label(root, text=text).grid(row=idx, column=0, sticky='e', padx=5, pady=2)

entry_pid    = tk.Entry(root);    entry_pid.grid(row=0, column=1)
entry_age    = tk.Entry(root);    entry_age.grid(row=1, column=1)

var_lic      = tk.StringVar(value='Yes')
tk.OptionMenu(root, var_lic, 'Yes', 'No').grid(row=2, column=1)

var_drunk    = tk.StringVar(value='No')
tk.OptionMenu(root, var_drunk, 'Yes', 'No').grid(row=3, column=1)

entry_claims = tk.Entry(root);    entry_claims.grid(row=4, column=1)

var_fir      = tk.StringVar(value='Yes')
tk.OptionMenu(root, var_fir, 'Yes', 'No').grid(row=5, column=1)

var_status   = tk.StringVar(value='active')
tk.OptionMenu(root, var_status, 'active', 'inactive').grid(row=6, column=1)

tk.Button(root, text="Predict Claim Status", command=predict_claim).grid(
    row=7, column=0, columnspan=2, pady=10
)

root.mainloop()
