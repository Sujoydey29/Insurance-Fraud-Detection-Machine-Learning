import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# 1. Load data
df = pd.read_csv('../data/final_dataset.csv')

# 2. Engineer time_diff_hrs
df['incident_dt'] = pd.to_datetime(
    df['Time of incident'].str.replace(' IST','', regex=False),
    format='%Y-%m-%d %I:%M %p',
    errors='coerce'
)
df['claim_dt'] = pd.to_datetime(
    df['Time of claim'].str.replace(' IST','', regex=False),
    format='%Y-%m-%d %I:%M %p',
    errors='coerce'
)
df['time_diff_hrs'] = (df['claim_dt'] - df['incident_dt']).dt.total_seconds()/3600

# 3. Features & target
X = df[['Policy status','License','Driver age','drunk driving',
        'FIR filed?','No. of previous claims','time_diff_hrs']]
y = df['Claim status'].map({'Fraud Claim':0,'Genuine Claim':1})

# 4. Preprocessor
cat = ['Policy status','License','drunk driving','FIR filed?']
num = ['Driver age','No. of previous claims','time_diff_hrs']
preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(drop='first'), cat),
    ('num', StandardScaler(), num)
])

# 5. Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
