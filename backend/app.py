from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pathlib import Path
import shutil
import pandas as pd
import joblib
import traceback

# ── App & CORS ─────────────────────────
app = FastAPI(title="Insurance Fraud Detection API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Paths & Artifacts ───────────────────
BASE_DIR      = Path(__file__).parent.parent
PIPELINE_PATH = BASE_DIR / "src" / "fraud_detection_pipeline.joblib"
DATA_PATH     = BASE_DIR / "data" / "Final_training_dataset.csv"
SUMMARY_PATH  = BASE_DIR / "data" / "Prediction_Summary.txt"

pipeline = joblib.load(PIPELINE_PATH)
df_all   = pd.read_csv(DATA_PATH)

# ── Helpers ─────────────────────────────
def compute_time_diff(inc: str, clm: str) -> float:
    a = datetime.strptime(inc.replace(" IST",""), "%Y-%m-%d %I:%M %p")
    b = datetime.strptime(clm.replace(" IST",""), "%Y-%m-%d %I:%M %p")
    return (b - a).total_seconds() / 3600.0

# ── Schemas ─────────────────────────────
class ClaimRequest(BaseModel):
    policy_id: Optional[str] = None
    policy_status: Optional[str] = None
    license: Optional[str] = None
    driver_age: Optional[int] = None
    drunk_driving: Optional[str] = None
    fir_filed: Optional[str] = None
    no_previous_claims: Optional[int] = None
    time_of_incident: Optional[str] = None
    time_of_claim: Optional[str] = None

class ClaimResponse(BaseModel):
    genuine_probability: float
    fraud_probability: float
    predicted_label: str

# ── Record lookup endpoint ─────────────
@app.get("/record/{policy_id}")
def get_record(policy_id: str):
    row = df_all[df_all["policy_id"] == policy_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Policy ID not found")
    r = row.iloc[0]
    return {
        "fuel_type":         r["fuel_type"],
        "model":             r["model"],
        "transmission_type": r["transmission_type"],
        "policy_status":      r["Policy status"],
        "license":            r["License"],
        "driver_age":         int(r["Driver age"]),
        "drunk_driving":      r["drunk driving"],
        "fir_filed":          r["FIR filed?"],
        "no_previous_claims": int(r["No. of previous claims"]),
        "time_of_incident":   r["Time of incident"],
        "time_of_claim":      r["Time of claim"],
    }

# ── Prediction endpoint ─────────────────
@app.post("/predict", response_model=ClaimResponse)
def predict(request: ClaimRequest):
    if request.policy_id:
        row = df_all[df_all["policy_id"] == request.policy_id]
        if row.empty:
            raise HTTPException(status_code=404, detail="Policy ID not found")
        r = row.iloc[0]
        params = {
            "Policy status":        r["Policy status"],
            "License":              r["License"],
            "Driver age":           int(r["Driver age"]),
            "drunk driving":        r["drunk driving"],
            "FIR filed?":           r["FIR filed?"],
            "No. of previous claims": int(r["No. of previous claims"]),
            "time_diff_hrs":        compute_time_diff(
                                        r["Time of incident"],
                                        r["Time of claim"]
                                    )
        }
    else:
        required = [
            ("policy_status",      request.policy_status),
            ("license",            request.license),
            ("driver_age",         request.driver_age),
            ("drunk_driving",      request.drunk_driving),
            ("fir_filed",          request.fir_filed),
            ("no_previous_claims", request.no_previous_claims),
            ("time_of_incident",   request.time_of_incident),
            ("time_of_claim",      request.time_of_claim),
        ]
        missing = [n for n,v in required if v is None]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing fields: {', '.join(missing)}"
            )
        params = {
            "Policy status":        request.policy_status,
            "License":              request.license,
            "Driver age":           request.driver_age,
            "drunk driving":        request.drunk_driving,
            "FIR filed?":           request.fir_filed,
            "No. of previous claims": request.no_previous_claims,
            "time_diff_hrs":        compute_time_diff(
                                        request.time_of_incident,
                                        request.time_of_claim
                                    )
        }

    X_new = pd.DataFrame([params])
    proba = pipeline.predict_proba(X_new)[0]
    fraud, genuine = float(proba[0]), float(proba[1])
    label = "Genuine Claim" if genuine >= fraud else "Fraud Claim"

    return ClaimResponse(
        genuine_probability=genuine,
        fraud_probability=fraud,
        predicted_label=label
    )

# ── Default summary endpoint ───────────────────
@app.get("/summary", response_class=PlainTextResponse)
def get_summary():
    if not SUMMARY_PATH.exists():
        raise HTTPException(status_code=404, detail="Summary file not found")
    return SUMMARY_PATH.read_text(encoding="utf-8")

# ── Upload & Summarize ─────────────────────────
@app.post("/summary/upload", response_class=PlainTextResponse)
def upload_and_summarize(file: UploadFile = File(...)):
    upload_dir = BASE_DIR / "data" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest_path = upload_dir / file.filename

    # Save the CSV
    with dest_path.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    # Run the testing logic and capture any exception
    try:
        from testing import test
        test(str(dest_path))
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"{str(e)}\n\n{tb}")

    # Build the summary path correctly
    summary_filename = dest_path.stem + "_Prediction_summary.txt"
    summary_path     = dest_path.parent / summary_filename

    if not summary_path.exists():
        raise HTTPException(status_code=500, detail="Summary file was not created")
    return summary_path.read_text(encoding="utf-8")

# ── Fetch a specific uploaded summary ─────────
@app.get("/summary/{datasetName}", response_class=PlainTextResponse)
def get_uploaded_summary(datasetName: str):
    upload_dir   = BASE_DIR / "data" / "uploads"
    summary_path = upload_dir / f"{datasetName}_Prediction_summary.txt"
    if not summary_path.exists():
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary_path.read_text(encoding="utf-8")
