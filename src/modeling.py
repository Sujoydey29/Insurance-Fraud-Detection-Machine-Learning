from preprocessing import preprocessor, X_train, X_test, y_train, y_test
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import joblib
import matplotlib.pyplot as plt

# 1. Build & train
clf = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier',   LogisticRegression(max_iter=1000))
])
clf.fit(X_train, y_train)

# 2. Evaluate
y_pred  = clf.predict(X_test)
y_proba = clf.predict_proba(X_test)[:,1]
print(classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print(f"ROC AUC: {roc_auc_score(y_test, y_proba):.3f}")

# 3. Optional: plot ROC
fpr, tpr, _ = roc_curve(y_test, y_proba)
plt.plot(fpr, tpr, label=f"AUC={roc_auc_score(y_test,y_proba):.3f}")
plt.plot([0,1],[0,1],'k--'); plt.legend(); plt.show()

# 4. Save the trained pipeline
joblib.dump(clf, 'fraud_detection_pipeline.joblib')
print("Saved: fraud_detection_pipeline.joblib")
