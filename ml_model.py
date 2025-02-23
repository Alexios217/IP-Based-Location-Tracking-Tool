import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Sample dataset (we can expand this with real data later)
data = {
    "fraud_score": [10, 50, 90, 20, 80, 95, 5, 70],
    "vpn": [0, 1, 1, 0, 1, 1, 0, 1],
    "tor": [0, 0, 1, 0, 0, 1, 0, 1],
    "recent_abuse": [0, 1, 1, 0, 1, 1, 0, 1],
    "bot_status": [0, 1, 1, 0, 0, 1, 0, 1],
    "label": [0, 1, 1, 0, 1, 1, 0, 1],
}

df = pd.DataFrame(data)

# Split data
X = df.drop(columns=["label"])
y = df["label"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train logistic regression model
model = LogisticRegression(random_state=42)
model.fit(X_train_scaled, y_train)

# Save model & scaler
joblib.dump(model, "ip_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Model training complete! ✅")
