# 📊 Power BI DAX Formulas Reference Guide
**Project:** PulseCommerce E-Commerce Churn Intelligence Platform  
**Target:** Final Year Student Presentation / Capstone Evaluation

When you open **Power BI Desktop** and load `powerbi/ecommerce_churn_powerbi.csv`, create a **New Measure** for each of the following formulas:

---

### 1. Total Customer Count
```dax
Total Customers = COUNTROWS('ecommerce_churn_powerbi')
```
*Purpose:* Displays the total customer accounts monitored.

---

### 2. Churned Customers Count
```dax
Churned Customers = 
CALCULATE(
    COUNTROWS('ecommerce_churn_powerbi'),
    'ecommerce_churn_powerbi'[churn] = 1
)
```
*Purpose:* Counts how many customers have left or discontinued purchasing.

---

### 3. Customer Churn Rate (%)
```dax
Churn Rate % = 
DIVIDE(
    [Churned Customers],
    [Total Customers],
    0
)
```
*Format:* Set Data format to **Percentage (1 decimal place)**.  
*Benchmark:* Typically ranges between 15% and 25% for e-commerce.

---

### 4. Total Platform Revenue
```dax
Total Revenue = SUM('ecommerce_churn_powerbi'[monetary_spend])
```
*Format:* Set Data format to **Currency ($)**.

---

### 5. Revenue at Risk
```dax
Revenue At Risk = 
CALCULATE(
    SUM('ecommerce_churn_powerbi'[monetary_spend]),
    'ecommerce_churn_powerbi'[churn] = 1
)
```
*Purpose:* Calculates total monetary value belonging to churned or high-risk accounts.

---

### 6. Average Customer Lifetime Value (CLV)
```dax
Average Customer Value = AVERAGE('ecommerce_churn_powerbi'[monetary_spend])
```
*Format:* Currency ($).

---

### 7. High-Risk Abandonment Customers
```dax
High Abandonment Accounts = 
CALCULATE(
    COUNTROWS('ecommerce_churn_powerbi'),
    'ecommerce_churn_powerbi'[cart_abandonment_rate] > 0.60
)
```
*Purpose:* Tracks how many users consistently abandon their cart without buying.

---

### 8. Customer Retention Rate (%)
```dax
Retention Rate % = 1 - [Churn Rate %]
```
*Format:* Percentage.
