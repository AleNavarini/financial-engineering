from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, classification_report

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INPUT_FILE = DATA_DIR / "features_dataset.csv"

PREDICTORS = ["intensity_t", "VIX", "r_pre_20", "rv_pre_20"]
TARGET = "stress_fwd_20"
N_FOLDS = 5
RANDOM_STATE = 42


def load_events() -> pd.DataFrame:
    df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])
    events = df[df["entry_backwardation_t"] == 1].copy()
    model_df = events.dropna(subset=PREDICTORS + [TARGET])
    print(f"Eventos totales: {len(events)}")
    print(f"Eventos usados (con todos los regresores y el target disponibles): {len(model_df)}")
    print(f"Eventos descartados por datos faltantes: {len(events) - len(model_df)}")
    print()
    return model_df


def fit_statsmodels_logit(model_df: pd.DataFrame) -> None:
    X = sm.add_constant(model_df[PREDICTORS])
    y = model_df[TARGET]

    model = sm.Logit(y, X).fit(disp=0)
    print("=== Regresión logística (statsmodels, ajuste in-sample) ===")
    print(model.summary())
    print()


def cross_validated_accuracy(model_df: pd.DataFrame) -> None:
    X = model_df[PREDICTORS].to_numpy()
    y = model_df[TARGET].to_numpy()

    baseline_accuracy = max(y.mean(), 1 - y.mean())

    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    clf = LogisticRegression()

    y_pred = cross_val_predict(clf, X, y, cv=cv, method="predict")
    y_proba = cross_val_predict(clf, X, y, cv=cv, method="predict_proba")[:, 1]

    acc = accuracy_score(y, y_pred)
    auc = roc_auc_score(y, y_proba)
    cm = confusion_matrix(y, y_pred)

    print(f"=== Precisión predictiva fuera de muestra ({N_FOLDS}-fold cross-validation) ===")
    print(f"Baseline (predecir siempre la clase mayoritaria, 'no estrés'): {baseline_accuracy:.1%}")
    print(f"Accuracy del modelo logístico (out-of-sample):                 {acc:.1%}")
    print(f"AUC-ROC:                                                       {auc:.3f}")
    print()
    print("Matriz de confusión (filas: real, columnas: predicho) [0=sin estrés, 1=con estrés]:")
    print(cm)
    print()
    print(classification_report(y, y_pred, target_names=["sin estrés", "con estrés"]))


def main() -> None:
    model_df = load_events()
    fit_statsmodels_logit(model_df)
    cross_validated_accuracy(model_df)


if __name__ == "__main__":
    main()
