# 💎 PulseBudget Enterprise: Digital Platform Budget & Expense Intelligence Suite

> **Edition:** Enterprise Production Release v2.4  
> **Domain:** Full-Stack Web Development • Financial Modeling • REST Microservices • Relational Database • Business Intelligence

PulseBudget is a centralized platform cost management and financial intelligence suite designed for modern digital platforms, e-commerce stores, and SaaS businesses. It tracks cloud hosting, digital marketing ad spend, SaaS software licenses, and operational contractor payroll—providing real-time budget utilization, spending alerts, and What-If financial optimization.

---

## 🏛️ System Architecture

```
[ Frontend: Modern HTML5 / Dark-Slate CSS / Vanilla ES6 / Chart.js ]
                               │
                      (Asynchronous REST API)
                               ▼
        [ Backend Core: Python 3 / Flask Microservice Engine ]
                               │
                        (ACID SQL Store)
                               ▼
      [ Database Layer: SQLite (pulsebudget.db) / Star-Schema CSV ]
                               │
                       (Direct Analytics)
                               ▼
          [ Executive BI: Power BI / Financial Reports ]
```

---

## 🛠️ Complete Tech Stack

| Layer | Technology | Key Capabilities |
| :--- | :--- | :--- |
| **Frontend UI** | HTML5, CSS3, JavaScript (ES6+), Chart.js | Executive dark-mode dashboard, real-time KPI cards, dynamic range sliders, doughnut & bar charts, responsive data grid. |
| **Backend API** | Python 3, Flask, Flask-CORS | REST API providing endpoints for budget metrics, expense management, scenario simulations, and presets. |
| **Database** | SQLite3 (`pulsebudget.db`) | Relational database tracking `budget_settings` and `platform_expenses`. |
| **Analytics & BI** | Chart.js, CSV Export, Power BI Ready | Cost elasticity metrics, 12-month run-rate projections, and DAX-ready CSV generation. |

---

## 🚀 Key Features

1. **Platform Expense & Subscription Entry**:
   - Add any software tool, cloud provider (AWS, GCP, Azure), digital ad campaign (Meta, Google), or operational contractor.
   - Categorize by functional group (`Cloud & Infrastructure`, `E-Commerce & Platform`, `Marketing & Ad Spend`, `SaaS & Productivity`, etc.) and necessity tier (`Essential`, `Growth`, `Discretionary`).
2. **Real-Time Executive KPI Dashboard**:
   - **Monthly Budget Target**: Configurable monthly budget ceiling with inline editing.
   - **Total Monthly Spend**: Aggregated sum of all active recurring tools and services.
   - **Remaining Budget / Buffer**: Live cash buffer or deficit calculation.
   - **Budget Utilization & Burn Rate**: Percentage gauge with visual alert thresholds (`Healthy`, `Near Limit`, `Over Budget`).
   - **Annual Run-Rate**: Automatically projects annual expenditure.
3. **AI / Heuristic Spending Optimization & Alerts**:
   - Audits expense ratios against industry benchmarks (e.g. flagging cloud infrastructure exceeding 30% of total budget).
   - Identifies discretionary SaaS subscriptions that can be trimmed during lean cycles.
4. **Interactive "What-If" Budget Optimization Simulator**:
   - Sliders to simulate adjusting monthly budget ceilings, cutting discretionary SaaS by $X\%$, or negotiating cloud discounts by $Y\%$.
   - Live Before vs. After comparison showing monthly savings and annual capital preserved.
5. **Quick-Load Platform Templates**:
   - One-click preset models for:
     - 🛒 **E-Commerce Store** (Shopify, AWS, Meta Ads, Klaviyo, Zendesk)
     - 💻 **SaaS Startup** (AWS RDS, AI API tokens, Stripe reserve, Google Ads, GitHub, Sentry)
     - 🎨 **Digital Agency** (Vercel, Adobe Creative Cloud, Meta Ads, Notion, Freelancers)
6. **Active Subscriptions Data Grid & CSV Export**:
   - Search by tool name, filter by category or necessity tier.
   - Instant delete and one-click export to CSV for Power BI and Excel reporting.

---

## 📂 Project Directory Structure

```
first_project/
├── backend/
│   ├── app.py                            # Flask REST API server (Entry point)
│   ├── database.py                       # SQLite database manager, analytics & seeders
│   ├── pulsebudget.db                    # SQLite database file (auto-generated)
│   └── requirements.txt                  # Python dependencies
├── frontend/
│   ├── index.html                        # Enterprise dashboard interface
│   ├── style.css                         # Dark slate glassmorphic CSS design system
│   └── app.js                            # REST API fetch calls, Chart.js visuals, simulator logic
├── powerbi/
│   ├── DAX_Formulas.md                   # Power BI DAX formulas reference
│   └── PowerBI_Dashboard_Guide.md        # Executive dashboard setup guide
├── ENTERPRISE_SYSTEM_SPEC_AND_FAQ.md     # Technical specification & system architecture review
└── README.md                             # Project documentation
```

---

## ⚡ Quick Start & Execution

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Launch Backend Server
```bash
python3 backend/app.py
```
Output:
```
=================================================================
 🚀 PULSEBUDGET ENTERPRISE SUITE RUNNING
 Live Platform Dashboard: http://127.0.0.1:5000
=================================================================
```

### 3. Open in Browser
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

*(Or open [frontend/index.html](file:///Users/akshit/Desktop/CODE/first_project/frontend/index.html) in your browser)*
