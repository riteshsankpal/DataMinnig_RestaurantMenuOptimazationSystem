"""Restaurant Menu Optimization System - Flask entry point.

Run locally:   python app.py        then open  http://127.0.0.1:5000
Settings come from optional environment variables: HOST, PORT, FLASK_DEBUG, MENU_DATA_DIR.
"""
import io
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, Response, jsonify, render_template, request
from flask.json.provider import DefaultJSONProvider

from analysis import association_rules as ar
from analysis import clustering as km
from analysis import data_cleaning as dc
from analysis import data_loader as dl
from analysis import menu_analytics as ma
from analysis import recommendations as rec

BASE_DIR = Path(__file__).resolve().parent


class NumpyJSON(DefaultJSONProvider):
    """Let jsonify handle numpy numbers and NaN (sent as null)."""
    @staticmethod
    def default(o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, (np.floating,)):
            return None if np.isnan(o) else float(o)
        if isinstance(o, (pd.Timestamp, datetime)):
            return o.strftime("%Y-%m-%d")
        return DefaultJSONProvider.default(o)


class DataStore:
    """Loads and cleans the CSVs once, and reloads automatically if a file changes on disk."""
    def __init__(self):
        self._stamp, self._data, self._error = None, None, None

    def _mtime(self):
        try:
            return tuple((dl.DATA_DIR / f).stat().st_mtime for f in dl.FILES.values())
        except OSError:
            return None

    def get(self):
        """Returns (data dict, error message). Exactly one of them is None."""
        stamp = self._mtime()
        if stamp is None or stamp != self._stamp or (self._data is None and self._error is None):
            self._stamp = stamp
            try:
                raw = dl.load_raw()
                orders, items, menu, log = dc.clean(raw)
                sales = ma.build_sales(orders, items, menu)
                if sales.empty:
                    raise dl.DataLoadError("No valid sales rows remain after cleaning. Check the CSV files.")
                self._data = {"raw": raw, "quality": dc.quality_report(raw), "orders": orders, "items": items,
                              "menu": menu, "sales": sales, "log": log}
                self._error = None
            except dl.DataLoadError as exc:
                self._data, self._error = None, str(exc)
        return self._data, self._error


def records(df):
    return df.astype(object).where(df.notna(), None).to_dict("records")


def create_app():
    app = Flask(__name__)
    app.json = NumpyJSON(app)
    store = DataStore()

    # ---------- helpers ----------
    def need_data():
        data, err = store.get()
        return data, err

    def api_guard(fn):
        """Wrap an API view: data-load errors -> 503, bad filters -> 400, anything else -> 500 with a clear message."""
        def wrapper(*a, **kw):
            data, err = need_data()
            if err:
                return jsonify(error=err), 503
            try:
                return fn(data, *a, **kw)
            except ma.FilterError as exc:
                return jsonify(error=str(exc)), 400
            except Exception as exc:  # last resort so the UI shows an error state instead of crashing
                app.logger.exception("API error")
                return jsonify(error=f"Unexpected error: {exc}"), 500
        wrapper.__name__ = fn.__name__
        return wrapper

    def filtered(data):
        f = ma.parse_filters(request.args, data["menu"])
        return ma.apply_filters(data["sales"], f), f

    def num(name, default, lo, hi):
        raw = request.args.get(name)
        if raw in (None, ""):
            return default
        try:
            v = float(raw)
        except ValueError:
            raise ma.FilterError(f"{name} must be a number.")
        if not lo <= v <= hi:
            raise ma.FilterError(f"{name} must be between {lo} and {hi}.")
        return v

    def csv_response(df, name):
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        stamp = datetime.now().strftime("%Y%m%d")
        return Response("\ufeff" + buf.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": f"attachment; filename={name}_{stamp}.csv"})

    def rules_result(data, s):
        res = ar.mine(s, num("min_support", 0.02, 0.001, 1), num("min_confidence", 0.3, 0, 1),
                      num("min_lift", 1.0, 0, 100))
        res["combos"] = ar.combo_suggestions(res["rules"], data["menu"], num("discount", 10, 0, 50))
        return res

    def clusters_result(s):
        k = request.args.get("k")
        try:
            k = int(k) if k else None
        except ValueError:
            raise ma.FilterError("k must be a whole number.")
        return km.cluster_items(ma.item_performance(s), k)

    # ---------- pages ----------
    def page(template, active, **ctx):
        return render_template(template, active=active, **ctx)

    @app.route("/")
    def index():
        return page("index.html", "home")

    @app.route("/dashboard")
    def dashboard():
        return page("dashboard.html", "dashboard")

    @app.route("/menu")
    def menu_page():
        return page("menu_analytics.html", "menu")

    @app.route("/market-basket")
    def basket_page():
        return page("market_basket.html", "basket")

    @app.route("/recommendations")
    def recs_page():
        return page("recommendations.html", "recs")

    @app.route("/about")
    def about_page():
        return page("about.html", "about")

    @app.route("/dataset")
    def dataset_page():
        data, err = need_data()
        if err:
            return page("dataset_overview.html", "dataset", error=err, files=[], log=[], info={})
        files = []
        for name, fname in dl.FILES.items():
            q = data["quality"][name]
            path = dl.DATA_DIR / fname
            files.append({"name": fname, "key": name, "rows": q["rows"], "size_kb": round(path.stat().st_size / 1024, 1),
                          "missing_total": q["missing_total"], "duplicates": q["duplicate_rows"],
                          "columns": [{"name": c, "meaning": dl.COLUMN_INFO[name].get(c, "Extra column"),
                                       "missing": q["missing"][c]} for c in q["columns"]]})
        s = data["sales"]
        totals = ma.order_totals(s)
        info = {"date_from": s["order_date"].min().strftime("%Y-%m-%d"), "date_to": s["order_date"].max().strftime("%Y-%m-%d"),
                "outliers": dc.order_value_outliers(totals), "categories": int(data["menu"]["category"].nunique()),
                "analyses": [
                    ("Item popularity and ranking", True, "order_items + menu_items"),
                    ("Revenue by item and category", True, "quantity x unit_price"),
                    ("Estimated cost, profit and margin", "cost" in data["menu"].columns, "cost column in menu_items.csv"),
                    ("Daily / weekly / monthly trends", "order_date" in data["orders"].columns, "order_date column"),
                    ("Market-basket (Apriori) rules", s["order_id"].nunique() >= 10, "needs many multi-item orders"),
                    ("K-Means clustering of items", s["item_id"].nunique() >= 4, "needs 4 or more sold items"),
                    ("Pareto (80/20) revenue analysis", True, "revenue per item")]}
        return page("dataset_overview.html", "dataset", error=None, files=files, log=data["log"], info=info)

    # ---------- JSON API ----------
    @app.route("/api/filter-options")
    @api_guard
    def api_filter_options(data):
        s, m = data["sales"], data["menu"]
        return jsonify(categories=sorted(m["category"].unique()),
                       items=[{"id": r.item_id, "name": r.item_name, "category": r.category}
                              for r in m.sort_values("item_name").itertuples()],
                       date_min=s["order_date"].min().strftime("%Y-%m-%d"), date_max=s["order_date"].max().strftime("%Y-%m-%d"))

    @app.route("/api/kpis")
    @api_guard
    def api_kpis(data):
        s, _ = filtered(data)
        return jsonify(kpis=ma.kpis(s), rows=int(len(s)))

    @app.route("/api/items")
    @api_guard
    def api_items(data):
        s, _ = filtered(data)
        return jsonify(items=records(ma.item_performance(s)))

    @app.route("/api/categories")
    @api_guard
    def api_categories(data):
        s, _ = filtered(data)
        return jsonify(categories=records(ma.category_performance(s)))

    @app.route("/api/trend")
    @api_guard
    def api_trend(data):
        s, _ = filtered(data)
        freq = request.args.get("freq", "day")
        return jsonify(freq=freq, trend=records(ma.sales_trend(s, freq)), weekday=records(ma.weekday_pattern(s)))

    @app.route("/api/pareto")
    @api_guard
    def api_pareto(data):
        s, _ = filtered(data)
        return jsonify(pareto=records(ma.pareto(ma.item_performance(s))))

    @app.route("/api/clusters")
    @api_guard
    def api_clusters(data):
        s, _ = filtered(data)
        return jsonify(clusters_result(s))

    @app.route("/api/rules")
    @api_guard
    def api_rules(data):
        s, _ = filtered(data)
        return jsonify(rules_result(data, s))

    @app.route("/api/recommendations")
    @api_guard
    def api_recs(data):
        s, _ = filtered(data)
        perf = ma.item_performance(s)
        combos = ar.combo_suggestions(ar.mine(s)["rules"], data["menu"]) if not s.empty else []
        return jsonify(recommendations=rec.build(perf, ma.category_performance(s), ma.pareto(perf), combos, ma.kpis(s)))

    # ---------- CSV exports ----------
    @app.route("/export/<report>.csv")
    @api_guard
    def export(data, report):
        s, _ = filtered(data)
        perf = ma.item_performance(s)
        builders = {
            "items": lambda: perf,
            "categories": lambda: ma.category_performance(s),
            "trend": lambda: ma.sales_trend(s, request.args.get("freq", "day")),
            "pareto": lambda: ma.pareto(perf),
            "rules": lambda: pd.DataFrame(rules_result(data, s)["rules"]),
            "clusters": lambda: pd.DataFrame(clusters_result(s).get("items", [])),
            "recommendations": lambda: pd.DataFrame(rec.build(
                perf, ma.category_performance(s), ma.pareto(perf), ar.combo_suggestions(ar.mine(s)["rules"], data["menu"]), ma.kpis(s))
            ).drop(columns=["evidence"], errors="ignore"),
        }
        if report not in builders:
            return jsonify(error=f"Unknown report '{report}'. Choose from: {', '.join(builders)}."), 404
        df = builders[report]()
        if df.empty:
            return jsonify(error="There is nothing to export for the current filters."), 404
        return csv_response(df, f"menu_{report}")

    @app.route("/healthz")
    def healthz():
        _, err = need_data()
        return (jsonify(status="error", detail=err), 503) if err else jsonify(status="ok")

    # ---------- error pages ----------
    @app.errorhandler(404)
    def not_found(_):
        if request.path.startswith(("/api/", "/export/")):
            return jsonify(error="Not found."), 404
        return render_template("error.html", active="", code=404, message="That page does not exist."), 404

    @app.errorhandler(500)
    def server_error(_):
        return render_template("error.html", active="", code=500, message="Something went wrong on the server."), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "5000")),
            debug=os.environ.get("FLASK_DEBUG", "0") == "1")
