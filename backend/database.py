"""
=============================================================================
PulseBudget: SQLite Database & Business Logic
Digital Platform Expense & Budget Intelligence Suite
Enterprise Edition
=============================================================================
"""

import os
import sqlite3
import uuid
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "pulsebudget.db")

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Budget Settings (Monthly Target Ceiling, Company Name, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_settings (
            id INTEGER PRIMARY KEY,
            monthly_budget_limit REAL NOT NULL DEFAULT 5000.0,
            currency TEXT NOT NULL DEFAULT 'USD',
            platform_name TEXT NOT NULL DEFAULT 'PulseCommerce Digital Store',
            target_growth_rate REAL NOT NULL DEFAULT 15.0
        )
    """)

    # Platform Expenses & Subscriptions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_expenses (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            billing_cycle TEXT NOT NULL DEFAULT 'Monthly',
            necessity TEXT NOT NULL DEFAULT 'Essential',
            vendor_tier TEXT DEFAULT 'Standard',
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()

    # Seed initial budget settings if not exists
    cursor.execute("SELECT COUNT(*) AS cnt FROM budget_settings")
    if cursor.fetchone()["cnt"] == 0:
        cursor.execute("""
            INSERT INTO budget_settings (id, monthly_budget_limit, currency, platform_name, target_growth_rate)
            VALUES (1, 6500.0, 'USD', 'OmniCommerce Global Platform', 20.0)
        """)
        conn.commit()

    # Seed default platform expenses if table is empty
    cursor.execute("SELECT COUNT(*) AS cnt FROM platform_expenses")
    if cursor.fetchone()["cnt"] == 0:
        seed_default_expenses(conn)

    conn.close()

def seed_default_expenses(conn):
    cursor = conn.cursor()
    defaults = [
        # (name, category, amount, billing_cycle, necessity, notes)
        ("AWS Cloud Hosting & S3", "Cloud & Infrastructure", 1250.0, "Monthly", "Essential", "Kubernetes cluster, EC2 and media CDN"),
        ("Shopify Plus Core Platform", "E-Commerce & Platform", 2000.0, "Monthly", "Essential", "Enterprise checkout & catalog hosting"),
        ("Meta & Instagram Performance Ads", "Marketing & Ad Spend", 1400.0, "Monthly", "Growth", "Customer acquisition & retargeting campaigns"),
        ("Google Search & Shopping Ads", "Marketing & Ad Spend", 950.0, "Monthly", "Growth", "High-intent search traffic campaigns"),
        ("Klaviyo Email & SMS Retention", "Marketing & Ad Spend", 320.0, "Monthly", "Essential", "Automated cart abandonment & win-back flows"),
        ("Slack Enterprise Grid", "SaaS & Productivity", 180.0, "Monthly", "Essential", "Internal team communication & alerts"),
        ("GitHub Team & Actions CI/CD", "Engineering & DevTools", 85.0, "Monthly", "Essential", "Source code repositories & automated tests"),
        ("Figma Professional", "Design & UX", 60.0, "Monthly", "Discretionary", "Product design and promotional banners"),
        ("Cloudflare Enterprise WAF/DDoS", "Security & Networking", 200.0, "Monthly", "Essential", "DDoS mitigation, SSL, and edge caching"),
        ("Datadog Infrastructure Monitoring", "Engineering & DevTools", 220.0, "Monthly", "Discretionary", "APM and server log analysis"),
        ("Zendesk Support Desk", "Operations & Support", 190.0, "Monthly", "Essential", "Customer service ticket resolution"),
        ("Freelance Senior React Developer", "Operations & Support", 800.0, "Monthly", "Growth", "Part-time frontend feature delivery")
    ]

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    for name, cat, amt, cycle, nec, notes in defaults:
        exp_id = f"EXP-{uuid.uuid4().hex[:6].upper()}"
        cursor.execute("""
            INSERT INTO platform_expenses (id, name, category, amount, billing_cycle, necessity, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (exp_id, name, cat, amt, cycle, nec, notes, now))

    conn.commit()

def get_settings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budget_settings WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"monthly_budget_limit": 6500.0, "currency": "USD", "platform_name": "Digital Commerce Platform", "target_growth_rate": 20.0}

def update_settings(budget_limit, platform_name=None):
    conn = get_db()
    cursor = conn.cursor()
    if platform_name:
        cursor.execute("""
            UPDATE budget_settings 
            SET monthly_budget_limit = ?, platform_name = ? 
            WHERE id = 1
        """, (budget_limit, platform_name))
    else:
        cursor.execute("""
            UPDATE budget_settings 
            SET monthly_budget_limit = ? 
            WHERE id = 1
        """, (budget_limit,))
    conn.commit()
    conn.close()

def get_all_expenses(category=None, necessity=None, search=None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM platform_expenses WHERE 1=1"
    params = []

    if category and category != "ALL":
        query += " AND category = ?"
        params.append(category)

    if necessity and necessity != "ALL":
        query += " AND necessity = ?"
        params.append(necessity)

    if search:
        query += " AND (name LIKE ? OR notes LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s])

    query += " ORDER BY amount DESC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def add_expense(name, category, amount, billing_cycle="Monthly", necessity="Essential", notes=""):
    conn = get_db()
    cursor = conn.cursor()
    exp_id = f"EXP-{uuid.uuid4().hex[:6].upper()}"
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO platform_expenses (id, name, category, amount, billing_cycle, necessity, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (exp_id, name, category, float(amount), billing_cycle, necessity, notes, now))

    conn.commit()
    conn.close()
    return exp_id

def delete_expense(expense_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM platform_expenses WHERE id = ?", (expense_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def load_preset_template(template_type="ecommerce"):
    """Replaces current expenses with a chosen business preset."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM platform_expenses")
    conn.commit()

    templates = {
        "ecommerce": [
            ("Shopify Plus / Checkout", "E-Commerce & Platform", 2000.0, "Monthly", "Essential", "Core store engine"),
            ("AWS Cloud & Media Storage", "Cloud & Infrastructure", 1100.0, "Monthly", "Essential", "High availability server cluster"),
            ("Meta & Instagram Ad Spend", "Marketing & Ad Spend", 1800.0, "Monthly", "Growth", "Direct response shopping campaigns"),
            ("Google Performance Max Ads", "Marketing & Ad Spend", 1200.0, "Monthly", "Growth", "Search intent and Google Shopping ads"),
            ("Klaviyo Retention Engine", "Marketing & Ad Spend", 350.0, "Monthly", "Essential", "Automated email/SMS workflows"),
            ("Zendesk Support Suite", "Operations & Support", 250.0, "Monthly", "Essential", "Customer service management"),
            ("Cloudflare Pro CDN", "Security & Networking", 120.0, "Monthly", "Essential", "DDoS mitigation and CDN"),
            ("Hotjar / Clarity Analytics", "Design & UX", 90.0, "Monthly", "Discretionary", "Heatmap & checkout dropoff tracking")
        ],
        "saas_startup": [
            ("AWS Cloud & RDS Databases", "Cloud & Infrastructure", 1600.0, "Monthly", "Essential", "Production backend, cache, and DB"),
            ("OpenAI / AI Model API Tokens", "Cloud & Infrastructure", 850.0, "Monthly", "Growth", "LLM inference and embeddings"),
            ("Stripe Payment Processing Reserve", "E-Commerce & Platform", 400.0, "Monthly", "Essential", "SaaS subscription billing gateway"),
            ("Google Ads & SEO Agency", "Marketing & Ad Spend", 1500.0, "Monthly", "Growth", "B2B lead generation"),
            ("Slack Enterprise & Zoom", "SaaS & Productivity", 220.0, "Monthly", "Essential", "Internal collaboration"),
            ("GitHub Team & Sentry Monitoring", "Engineering & DevTools", 180.0, "Monthly", "Essential", "Dev pipeline & error tracking"),
            ("Figma & Webflow Landing Page", "Design & UX", 140.0, "Monthly", "Discretionary", "Design system & marketing site"),
            ("Contract QA Engineer", "Operations & Support", 900.0, "Monthly", "Growth", "Automated testing & releases")
        ],
        "creator_agency": [
            ("Vercel & Supabase Cloud", "Cloud & Infrastructure", 250.0, "Monthly", "Essential", "Client web applications"),
            ("Canva Pro & Adobe Creative Cloud", "Design & UX", 160.0, "Monthly", "Essential", "Graphic design and video editing"),
            ("Meta Ad Spend for Clients", "Marketing & Ad Spend", 2200.0, "Monthly", "Growth", "Paid social client acquisition"),
            ("Notion & Loom Team", "SaaS & Productivity", 80.0, "Monthly", "Essential", "Client project portal"),
            ("Freelance Copywriter", "Operations & Support", 600.0, "Monthly", "Growth", "Ad copy & email newsletters"),
            ("Circle / Skool Community Platform", "E-Commerce & Platform", 190.0, "Monthly", "Growth", "Membership portal")
        ]
    }

    selected = templates.get(template_type, templates["ecommerce"])
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    for name, cat, amt, cycle, nec, notes in selected:
        exp_id = f"EXP-{uuid.uuid4().hex[:6].upper()}"
        cursor.execute("""
            INSERT INTO platform_expenses (id, name, category, amount, billing_cycle, necessity, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (exp_id, name, cat, amt, cycle, nec, notes, now))

    conn.commit()
    conn.close()

def compute_budget_analytics():
    """Calculates all budget intelligence KPIs, category allocations, and optimization alerts."""
    settings = get_settings()
    monthly_budget = float(settings.get("monthly_budget_limit", 6500.0))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM platform_expenses")
    expenses = [dict(r) for r in cursor.fetchall()]
    conn.close()

    total_monthly_spend = sum(e["amount"] for e in expenses)
    remaining_budget = monthly_budget - total_monthly_spend
    burn_percentage = (total_monthly_spend / monthly_budget * 100.0) if monthly_budget > 0 else 0.0

    # Categorized Spend
    category_totals = {}
    for e in expenses:
        cat = e["category"]
        category_totals[cat] = category_totals.get(cat, 0.0) + e["amount"]

    # Necessity Breakdown
    necessity_totals = {"Essential": 0.0, "Growth": 0.0, "Discretionary": 0.0}
    for e in expenses:
        nec = e.get("necessity", "Essential")
        necessity_totals[nec] = necessity_totals.get(nec, 0.0) + e["amount"]

    # Budget Health Status
    if total_monthly_spend > monthly_budget:
        status = "OVER_BUDGET"
        status_label = "Critical: Over Budget"
        status_color = "#ef4444" # Red
    elif total_monthly_spend >= (monthly_budget * 0.90):
        status = "NEAR_LIMIT"
        status_label = "Warning: Near 90% Ceiling"
        status_color = "#f59e0b" # Amber
    else:
        status = "HEALTHY"
        status_label = "Healthy: Within Allocated Budget"
        status_color = "#10b981" # Green

    # AI / Heuristic Spending Optimization Recommendations
    recommendations = []

    # 1. Discretionary savings potential
    if necessity_totals["Discretionary"] > 0:
        recommendations.append({
            "type": "SAVINGS_OPPORTUNITY",
            "title": f"Identify ${necessity_totals['Discretionary']:,.0f}/mo in Discretionary Tools",
            "detail": "Tools marked as Discretionary can be paused or downgraded immediately if cash flow tightens.",
            "impact": f"-${necessity_totals['Discretionary']:,.0f}/mo"
        })

    # 2. Marketing vs Infrastructure Balance
    mkt_spend = category_totals.get("Marketing & Ad Spend", 0.0)
    infra_spend = category_totals.get("Cloud & Infrastructure", 0.0)

    if total_monthly_spend > 0:
        infra_ratio = (infra_spend / total_monthly_spend) * 100.0
        if infra_ratio > 30.0:
            recommendations.append({
                "type": "INFRA_OPTIMIZATION",
                "title": f"Infrastructure Consumes {infra_ratio:.1f}% of Total Spend",
                "detail": "Cloud costs exceed the 25% target benchmark. Consider 1-year AWS/GCP Savings Plans or reserved instances to reduce bills by 20-35%.",
                "impact": f"Est. savings ~${infra_spend * 0.25:,.0f}/mo"
            })

    # 3. Overbudget Alert Action
    if total_monthly_spend > monthly_budget:
        overage = total_monthly_spend - monthly_budget
        recommendations.append({
            "type": "BUDGET_DEFICIT",
            "title": f"Budget Deficit of ${overage:,.0f}/month",
            "detail": f"Monthly spend exceeds your ${monthly_budget:,.0f} ceiling. Adjust ad spend or pause discretionary tools to return to green.",
            "impact": f"Deficit: ${overage:,.0f}"
        })
    else:
        recommendations.append({
            "type": "BUFFER_AVAILABLE",
            "title": f"Healthy Monthly Surplus: ${remaining_budget:,.0f}",
            "detail": f"You are operating within limits with {100 - burn_percentage:.1f}% buffer available for growth experiments or emergency reserves.",
            "impact": f"+${remaining_budget:,.0f} Runway"
        })

    # 12-Month Run Rate
    annual_run_rate = total_monthly_spend * 12.0

    return {
        "budget_limit": round(monthly_budget, 2),
        "total_monthly_spend": round(total_monthly_spend, 2),
        "remaining_budget": round(remaining_budget, 2),
        "burn_percentage": round(burn_percentage, 1),
        "annual_run_rate": round(annual_run_rate, 2),
        "status": status,
        "status_label": status_label,
        "status_color": status_color,
        "total_tools_count": len(expenses),
        "category_breakdown": {k: round(v, 2) for k, v in category_totals.items()},
        "necessity_breakdown": {k: round(v, 2) for k, v in necessity_totals.items()},
        "recommendations": recommendations
    }

if __name__ == "__main__":
    init_db()
    print("PulseBudget Database initialized successfully.")
