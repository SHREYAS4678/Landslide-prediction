"""
LandSlide AI — Model Training Script
Trains a Random Forest + XGBoost ensemble on sensor data.
Run: python ml/train.py
"""
import joblib, numpy as np, pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report
from xgboost import XGBClassifier

DATA_PATH  = Path("data/landslide_sensor_data.csv")
MODEL_DIR  = Path("ml/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = ["rainfall","soil_moisture","temperature","vibration","slope_angle",
            "soil_rain","vib_slope","moisture_deficit"]

def generate_synthetic(n=5000):
    rng = np.random.default_rng(42)
    rf  = rng.uniform(0, 100, n)
    sm  = rng.uniform(20, 100, n)
    tp  = rng.uniform(10, 40, n)
    vb  = rng.uniform(0, 8, n)
    sl  = rng.uniform(15, 55, n)
    score = (rf/100*0.82 + sm/100*0.88 + vb/8*0.71 + sl/55*0.65
             + (sm/100*rf/100)*0.74) / (0.82+0.88+0.71+0.65+0.74)
    score += rng.normal(0, 0.05, n)
    labels = np.where(score>0.70,"HIGH",np.where(score>0.40,"MEDIUM","LOW"))
    return pd.DataFrame({"rainfall":rf,"soil_moisture":sm,"temperature":tp,
                          "vibration":vb,"slope_angle":sl,"risk_label":labels})

def engineer(df):
    df = df.copy()
    df["soil_rain"]        = df["soil_moisture"] * df["rainfall"]
    df["vib_slope"]        = df["vibration"] * (df["slope_angle"] / 45)
    df["moisture_deficit"] = 100 - df["soil_moisture"]
    return df

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH) if DATA_PATH.exists() else generate_synthetic()
    if not DATA_PATH.exists():
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(DATA_PATH, index=False)
        print("Synthetic data saved to", DATA_PATH)

    df  = engineer(df)
    le  = LabelEncoder()
    y   = le.fit_transform(df["risk_label"])
    X   = df[FEATURES].values
    sc  = StandardScaler()
    Xs  = sc.fit_transform(X)
    X_tr, X_te, y_tr, y_te = train_test_split(Xs, y, test_size=0.2,
                                               random_state=42, stratify=y)

    rf  = RandomForestClassifier(n_estimators=300, max_depth=12, n_jobs=-1, random_state=42)
    xgb = XGBClassifier(n_estimators=200, max_depth=8, learning_rate=0.05,
                         eval_metric="mlogloss", random_state=42)
    ens = VotingClassifier([("rf",rf),("xgb",xgb)], voting="soft")

    print("Training ensemble…")
    ens.fit(X_tr, y_tr)
    cv = cross_val_score(ens, Xs, y, cv=StratifiedKFold(5), scoring="accuracy").mean()
    print(f"CV Accuracy: {cv:.4f}")
    print(classification_report(y_te, ens.predict(X_te), target_names=le.classes_))

    joblib.dump(ens, MODEL_DIR/"rf_model.pkl")
    joblib.dump(sc,  MODEL_DIR/"scaler.pkl")
    joblib.dump(le,  MODEL_DIR/"label_encoder.pkl")
    print("Models saved →", MODEL_DIR)
