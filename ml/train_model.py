"""
=============================================================================
PulseCommerce: E-Commerce Customer Churn Prediction
Machine Learning Training & Evaluation Script
Course: Final Year Capstone Project / B.Tech / B.E. / BCA / MCA
=============================================================================
Description:
    This script generates a realistic e-commerce customer behavior dataset,
    trains a Random Forest Classification model to predict churn,
    evaluates model metrics (Accuracy, Precision, Recall, F1, Confusion Matrix),
    and exports:
      1. churn_model.pkl (trained model)
      2. scaler.pkl (feature normalization scaler)
      3. evaluation_report.txt (metrics for viva presentation)
      4. ../powerbi/ecommerce_churn_powerbi.csv (dataset for Power BI)
=============================================================================
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

# Ensure folders exist
os.makedirs("ml", exist_ok=True)
os.makedirs("powerbi", exist_ok=True)

def generate_synthetic_data(n_samples=1500, random_state=42):
    """
    Generates a realistic synthetic e-commerce customer dataset with known business drivers.
    Features:
      - recency_days: Days since last order (1 to 120)
      - frequency_orders: Total orders placed in past year (1 to 40)
      - monetary_spend: Total amount spent in USD (50 to 3500)
      - cart_abandonment_rate: Ratio of carts abandoned (0.05 to 0.95)
      - support_tickets: Customer complaint count (0 to 7)
      - avg_delivery_delay_days: Average delay in deliveries (0 to 10 days)
      - satisfaction_score: Rating from 1 (terrible) to 5 (excellent)
    """
    np.random.seed(random_state)
    
    customer_ids = [f"CUST-{1000 + i}" for i in range(n_samples)]
    names = [
        "Aarav Sharma", "Diya Patel", "Rohan Mehta", "Pooja Verma", "Vikram Singh",
        "Ananya Iyer", "Karan Malhotra", "Neha Joshi", "Aditya Nair", "Sneha Rao",
        "John Miller", "Emily Davis", "Michael Brown", "Sarah Wilson", "David Taylor",
        "Jessica White", "Daniel Clark", "Laura Harris", "James Lewis", "Rachel Martin"
    ]
    customer_names = [np.random.choice(names) + f" #{i+1}" for i in range(n_samples)]
    
    categories = ["Electronics", "Fashion & Apparel", "Home & Kitchen", "Beauty & Care", "Sports & Fitness"]
    preferred_category = np.random.choice(categories, size=n_samples, p=[0.25, 0.30, 0.20, 0.15, 0.10])
    
    # Feature distributions
    recency_days = np.random.randint(1, 120, size=n_samples)
    frequency_orders = np.random.randint(1, 40, size=n_samples)
    monetary_spend = np.round(frequency_orders * np.random.uniform(25.0, 110.0, size=n_samples), 2)
    cart_abandonment_rate = np.round(np.random.beta(a=2, b=3, size=n_samples), 2)
    support_tickets = np.random.poisson(lam=1.8, size=n_samples)
    avg_delivery_delay_days = np.random.exponential(scale=2.2, size=n_samples).round(1)
    satisfaction_score = np.random.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.12, 0.18, 0.25, 0.30, 0.15])
    
    # Calculate Latent Churn Risk Score (Ground Truth logic)
    # Risk factors: high recency, high cart abandonment, many support tickets, delays, low satisfaction
    risk_score = (
        (recency_days / 120.0) * 0.30 +
        (cart_abandonment_rate) * 0.20 +
        (np.clip(support_tickets, 0, 6) / 6.0) * 0.20 +
        (np.clip(avg_delivery_delay_days, 0, 10) / 10.0) * 0.15 +
        ((5 - satisfaction_score) / 4.0) * 0.25 -
        (np.clip(frequency_orders, 0, 30) / 30.0) * 0.10
    )
    
    # Add mild noise
    risk_score += np.random.normal(0, 0.05, size=n_samples)
    churn = (risk_score > 0.48).astype(int)
    
    df = pd.DataFrame({
        "customer_id": customer_ids,
        "customer_name": customer_names,
        "preferred_category": preferred_category,
        "recency_days": recency_days,
        "frequency_orders": frequency_orders,
        "monetary_spend": monetary_spend,
        "cart_abandonment_rate": cart_abandonment_rate,
        "support_tickets": support_tickets,
        "avg_delivery_delay_days": avg_delivery_delay_days,
        "satisfaction_score": satisfaction_score,
        "churn": churn
    })
    
    return df

def train_and_evaluate():
    print("=" * 65)
    print(" PULSECOMMERCE ML PIPELINE: STUDENT MODEL TRAINING")
    print("=" * 65)
    
    # 1. Generate Dataset
    print("[1/5] Generating synthetic e-commerce customer dataset...")
    df = generate_synthetic_data(n_samples=1500)
    
    # Save Power BI dataset
    csv_path = os.path.join("powerbi", "ecommerce_churn_powerbi.csv")
    df.to_csv(csv_path, index=False)
    print(f" -> Exported dataset to: {csv_path} ({len(df)} rows)")
    
    # 2. Select ML Features
    feature_cols = [
        "recency_days",
        "frequency_orders",
        "monetary_spend",
        "cart_abandonment_rate",
        "support_tickets",
        "avg_delivery_delay_days",
        "satisfaction_score"
    ]
    
    X = df[feature_cols]
    y = df["churn"]
    
    # 3. Train / Test Split (80% Train, 20% Test)
    print("[2/5] Performing Train-Test Split (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    # 4. Feature Scaling (StandardScaler)
    print("[3/5] Scaling features using StandardScaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 5. Train Random Forest Classifier
    print("[4/5] Training Random Forest Classifier (100 trees)...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=4,
        random_state=42
    )
    clf.fit(X_train_scaled, y_train)
    
    # 6. Evaluation
    print("[5/5] Evaluating model performance...")
    y_pred = clf.predict(X_test_scaled)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    
    print("-" * 65)
    print(f" Model Accuracy : {acc * 100:.2f}%")
    print(f" Precision      : {prec * 100:.2f}%")
    print(f" Recall         : {rec * 100:.2f}%")
    print(f" F1-Score       : {f1 * 100:.2f}%")
    print("-" * 65)
    print("Confusion Matrix:\n", cm)
    print("\nClassification Report:\n", report)
    
    # Feature Importances
    importances = clf.feature_importances_
    feature_rank = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
    print("\nFeature Importances (Top Churn Drivers):")
    for feat, imp in feature_rank:
        print(f" - {feat:25s}: {imp * 100:.2f}%")
    
    # Save artifacts
    with open("ml/churn_model.pkl", "wb") as f:
        pickle.dump(clf, f)
    with open("ml/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open("ml/feature_cols.pkl", "wb") as f:
        pickle.dump(feature_cols, f)
        
    # Write evaluation report for viva presentation
    report_text = f"""===================================================================
PULSECOMMERCE - MACHINE LEARNING MODEL EVALUATION REPORT
Final Year Capstone Project
===================================================================
Algorithm           : Random Forest Classifier
Number of Trees     : 100
Features Used       : {', '.join(feature_cols)}
Dataset Size        : 1,500 customer records (80/20 train-test split)

PERFORMANCE METRICS:
-------------------------------------------------------------------
- Overall Accuracy  : {acc * 100:.2f}%
- Precision (Churn) : {prec * 100:.2f}%
- Recall (Churn)    : {rec * 100:.2f}%
- F1-Score          : {f1 * 100:.2f}%

CONFUSION MATRIX:
-------------------------------------------------------------------
True Negative (Retained correctly)  : {cm[0][0]}
False Positive (Flagged by mistake) : {cm[0][1]}
False Negative (Missed churners)    : {cm[1][0]}
True Positive (Caught churners)     : {cm[1][1]}

FEATURE IMPORTANCE RANKING (TOP CHURN DRIVERS):
-------------------------------------------------------------------
"""
    for feat, imp in feature_rank:
        report_text += f"- {feat:25s}: {imp * 100:.2f}%\n"
        
    report_text += "\nConclusion: The Random Forest model provides strong balance between Precision and Recall for proactive retention campaigns.\n"
    
    with open("ml/evaluation_report.txt", "w") as f:
        f.write(report_text)
        
    print("\n[SUCCESS] Model artifacts and evaluation report saved in 'ml/' folder!")

if __name__ == "__main__":
    train_and_evaluate()
