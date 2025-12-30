"""
train_fusion_model.py
=====================
Trains a DIRECT FUSION classifier and computes FULL evaluation metrics.

Outputs:
- fusion_model.pkl
- fusion_metrics.json
- confusion_matrix.npy
- roc_auc.npy
"""

import json
import numpy as np
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    roc_auc_score
)

from xgboost import XGBClassifier

# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PREPROC_DIR = BASE_DIR / "ml_training" / "preprocessed"
ARTIFACT_DIR = BASE_DIR / "ml_training" / "artifacts"
MODEL_DIR = BASE_DIR / "ml_training" / "models"
REPORT_DIR = BASE_DIR / "ml_training" / "reports"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================
# LOAD DATA
# ======================================================

X = np.load(PREPROC_DIR / "X_fusion.npy")
y = np.load(PREPROC_DIR / "y_3class.npy")

print("Loaded data")
print("X shape:", X.shape)
print("y shape:", y.shape)

# ======================================================
# TRAIN / VALIDATION SPLIT
# ======================================================

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ======================================================
# MODEL
# ======================================================

model = XGBClassifier(
    objective="multi:softprob",
    num_class=3,
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1
)

# ======================================================
# TRAIN
# ======================================================

print("Training fusion model...")
model.fit(X_train, y_train)

# ======================================================
# PREDICTIONS
# ======================================================

y_pred = model.predict(X_val)
y_prob = model.predict_proba(X_val)

# ======================================================
# METRICS
# ======================================================

accuracy = accuracy_score(y_val, y_pred)

precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
    y_val, y_pred, average="macro"
)

precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
    y_val, y_pred, average="weighted"
)

conf_mat = confusion_matrix(y_val, y_pred)

# ROC-AUC (One-vs-Rest)
roc_auc_per_class = roc_auc_score(
    y_val,
    y_prob,
    multi_class="ovr",
    average=None
)

roc_auc_macro = roc_auc_score(
    y_val,
    y_prob,
    multi_class="ovr",
    average="macro"
)

# ======================================================
# SAVE METRICS
# ======================================================

metrics = {
    "accuracy": float(accuracy),
    "precision_macro": float(precision_macro),
    "recall_macro": float(recall_macro),
    "f1_macro": float(f1_macro),
    "precision_weighted": float(precision_weighted),
    "recall_weighted": float(recall_weighted),
    "f1_weighted": float(f1_weighted),
    "roc_auc_macro": float(roc_auc_macro),
    "roc_auc_per_class": roc_auc_per_class.tolist(),
    "class_labels": ["Low", "Moderate", "High"]
}

with open(REPORT_DIR / "fusion_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

np.save(REPORT_DIR / "confusion_matrix.npy", conf_mat)
np.save(REPORT_DIR / "roc_auc.npy", roc_auc_per_class)

# ======================================================
# SAVE MODEL
# ======================================================

joblib.dump(model, MODEL_DIR / "fusion_model.pkl")

# ======================================================
# PRINT SUMMARY
# ======================================================

print("\n===== VALIDATION METRICS =====")
print("Accuracy:", accuracy)
print("Macro Precision:", precision_macro)
print("Macro Recall:", recall_macro)
print("Macro F1:", f1_macro)
print("Weighted F1:", f1_weighted)
print("Macro ROC-AUC:", roc_auc_macro)
print("Confusion Matrix:\n", conf_mat)

print("\nModel and metrics saved successfully.")
