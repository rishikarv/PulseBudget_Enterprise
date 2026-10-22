# 📈 Step-by-Step Power BI Dashboard Setup Guide
**PulseCommerce Student Capstone Project**

Follow these 4 simple steps to build your Power BI executive dashboard using the generated dataset:

---

## Step 1: Load Data into Power BI Desktop
1. Open **Power BI Desktop**.
2. Click **Get Data** ➔ **Text/CSV**.
3. Select the file: `first_project/powerbi/ecommerce_churn_powerbi.csv`.
4. Click **Load**.

---

## Step 2: Create the DAX Measures
In the **Modeling** tab, click **New Measure** and paste the formulas from [DAX_Formulas.md](file:///Users/akshit/Desktop/CODE/first_project/powerbi/DAX_Formulas.md):
- `Total Customers`
- `Churn Rate %`
- `Total Revenue`
- `Revenue At Risk`

---

## Step 3: Build the Recommended Visuals

### Visual 1: Executive KPI Cards (Top Banner)
- Add 4 **Card** visuals in a row:
  - Card 1: `[Total Customers]`
  - Card 2: `[Total Revenue]` (formatted as currency)
  - Card 3: `[Churn Rate %]` (formatted as percentage)
  - Card 4: `[Revenue At Risk]` (formatted as currency)

### Visual 2: Churn Distribution by Product Category (Clustered Column Chart)
- **X-axis**: `preferred_category`
- **Y-axis**: `[Total Customers]` and `[Churned Customers]`
- **Legend**: `churn` (0 = Retained, 1 = Churned)
- *Viva Talking Point:* Shows which department (e.g., Electronics vs. Fashion) loses the most customers.

### Visual 3: Satisfaction Score vs. Churn Rate (Line & Stacked Bar)
- **X-axis**: `satisfaction_score` (1 to 5)
- **Column Values**: `[Total Customers]`
- **Line Values**: `[Churn Rate %]`
- *Viva Talking Point:* Proves that 1-star and 2-star satisfaction accounts have over 75% churn probability.

### Visual 4: Revenue At Risk Scatter Plot
- **X-axis**: `recency_days` (Days inactive)
- **Y-axis**: `monetary_spend` (Customer Value)
- **Legend**: `churn`
- *Viva Talking Point:* High-value customers in the top-right quadrant represent urgent retention priorities.

---

## Step 4: Add Slicers (Interactive Filters)
Add 2 **Slicers** at the top or side:
1. Slicer by `preferred_category` (dropdown).
2. Slicer by `satisfaction_score` (1 to 5 tiles).
