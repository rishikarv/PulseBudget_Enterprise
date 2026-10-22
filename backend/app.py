"""
=============================================================================
PulseBudget: Professional Digital Platform Expense & Budget Intelligence Server
Enterprise Release v2.4
=============================================================================
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import database

# Paths
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

# Initialize database on startup
database.init_db()

@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

# -----------------------------------------------------------------------------
# REST API Endpoints
# -----------------------------------------------------------------------------
@app.route("/api/budget/summary", methods=["GET"])
def api_budget_summary():
    """Returns high-level platform budget KPIs, category breakdowns, and AI recommendations."""
    try:
        data = database.compute_budget_analytics()
        settings = database.get_settings()
        return jsonify({"status": "success", "analytics": data, "settings": settings})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/budget/expenses", methods=["GET"])
def api_get_expenses():
    """Returns list of active platform tools/expenses with optional category and search filtering."""
    try:
        category = request.args.get("category", "ALL")
        necessity = request.args.get("necessity", "ALL")
        search = request.args.get("search", "").strip()

        expenses = database.get_all_expenses(category=category, necessity=necessity, search=search)
        return jsonify({"status": "success", "count": len(expenses), "expenses": expenses})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/budget/expenses", methods=["POST"])
def api_add_expense():
    """Adds a new platform expense or digital subscription."""
    try:
        body = request.get_json(force=True)
        name = body.get("name", "").strip()
        category = body.get("category", "SaaS & Productivity").strip()
        amount = float(body.get("amount", 0))
        billing_cycle = body.get("billing_cycle", "Monthly").strip()
        necessity = body.get("necessity", "Essential").strip()
        notes = body.get("notes", "").strip()

        if not name or amount <= 0:
            return jsonify({"status": "error", "message": "Expense name and positive amount are required."}), 400

        exp_id = database.add_expense(
            name=name, category=category, amount=amount,
            billing_cycle=billing_cycle, necessity=necessity, notes=notes
        )

        analytics = database.compute_budget_analytics()
        return jsonify({
            "status": "success",
            "message": f"Successfully added '{name}' (${amount:,.2f}/mo)",
            "expense_id": exp_id,
            "analytics": analytics
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/budget/expenses/<expense_id>", methods=["DELETE"])
def api_delete_expense(expense_id):
    """Deletes an expense item by ID."""
    try:
        deleted = database.delete_expense(expense_id)
        if not deleted:
            return jsonify({"status": "error", "message": "Expense ID not found."}), 404

        analytics = database.compute_budget_analytics()
        return jsonify({"status": "success", "message": "Expense removed.", "analytics": analytics})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/budget/settings", methods=["POST"])
def api_update_settings():
    """Updates monthly budget ceiling and platform name."""
    try:
        body = request.get_json(force=True)
        limit = float(body.get("monthly_budget_limit", 5000.0))
        platform_name = body.get("platform_name")

        if limit <= 0:
            return jsonify({"status": "error", "message": "Budget limit must be greater than zero."}), 400

        database.update_settings(limit, platform_name)
        analytics = database.compute_budget_analytics()
        return jsonify({"status": "success", "analytics": analytics})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/budget/load-preset", methods=["POST"])
def api_load_preset():
    """Loads a ready-made business template (ecommerce, saas_startup, creator_agency)."""
    try:
        body = request.get_json(force=True)
        template_type = body.get("template_type", "ecommerce")
        database.load_preset_template(template_type)

        analytics = database.compute_budget_analytics()
        expenses = database.get_all_expenses()
        return jsonify({
            "status": "success",
            "message": f"Loaded template: {template_type.replace('_', ' ').title()}",
            "analytics": analytics,
            "expenses": expenses
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/budget/simulate", methods=["POST"])
def api_simulate_budget():
    """
    Simulates budget adjustments:
      - custom_budget_limit: New monthly budget ceiling
      - trim_discretionary_pct: % to cut from discretionary tools (0 to 100%)
      - renegotiate_infra_pct: % savings on cloud/hosting (e.g. 15%)
    Returns Before vs After analysis, monthly savings, and 12-month runway projection.
    """
    try:
        body = request.get_json(force=True)
        custom_limit = float(body.get("custom_budget_limit", 6500.0))
        trim_disc = float(body.get("trim_discretionary_pct", 0.0)) / 100.0
        reneg_infra = float(body.get("renegotiate_infra_pct", 0.0)) / 100.0

        expenses = database.get_all_expenses()
        baseline_spend = sum(e["amount"] for e in expenses)

        # Apply simulation levers
        simulated_spend = 0.0
        for e in expenses:
            amt = e["amount"]
            if e["necessity"] == "Discretionary":
                amt = amt * (1.0 - trim_disc)
            if e["category"] == "Cloud & Infrastructure":
                amt = amt * (1.0 - reneg_infra)
            simulated_spend += amt

        monthly_savings = max(0.0, baseline_spend - simulated_spend)
        annual_savings = monthly_savings * 12.0
        new_remaining = custom_limit - simulated_spend
        burn_rate_pct = (simulated_spend / custom_limit * 100.0) if custom_limit > 0 else 0.0

        return jsonify({
            "status": "success",
            "simulation": {
                "baseline_spend": round(baseline_spend, 2),
                "simulated_spend": round(simulated_spend, 2),
                "monthly_savings": round(monthly_savings, 2),
                "annual_savings": round(annual_savings, 2),
                "simulated_remaining": round(new_remaining, 2),
                "burn_rate_pct": round(burn_rate_pct, 1),
                "is_under_budget": simulated_spend <= custom_limit
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    print("=" * 65)
    print(" 🚀 PULSEBUDGET ENTERPRISE SUITE RUNNING")
    print(" Live Platform Dashboard: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=True)
