# Restaurant Menu Optimization System

A college Data Mining project. It reads restaurant order records, then shows best and worst selling dishes, revenue and estimated profit, dishes that are ordered together (Apriori), groups of similar dishes (K-Means), a Pareto analysis, and rule-based menu recommendations, all in a website that runs on your own computer.

> **The CSV files in `data/` are synthetic demonstration data** created by `tools/generate_data.py`. They are not from a real restaurant. Every number on the website is calculated from these files when you open a page, and it is not hardcoded.

## Quick start on Windows (recommended)

1. Extract the ZIP (right-click, **Extract All**).
2. Open the extracted `Restaurant_Menu_Optimization_System` folder.
3. Double-click **`run_project.bat`**.
4. Wait while it sets itself up. The first run downloads libraries and needs internet.
5. Your browser opens by itself. If it does not, open **http://127.0.0.1:5000**.
6. To stop, click the black window and press `Ctrl+C`, or close the window.

You need **Python 3.9 or newer** from https://www.python.org/downloads/ (tick **Add python.exe to PATH** in the installer).

## Manual setup (if you prefer typing commands)

Open **Command Prompt** inside the project folder (type `cmd` in the folder's address bar and press Enter):

```bat
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000. Next time you only need the `activate` and `python app.py` lines.

If `pip install` fails on `mlxtend`, run `pip install -r requirements-core.txt` instead. The app works without MLxtend by using its own Apriori code.

## Run the tests

```bat
.venv\Scripts\activate
python -m unittest discover -s tests -v
```

## Pages

| Page | URL | What it does |
|---|---|---|
| Home | `/` | Introduction and a live preview built from the data |
| Dashboard | `/dashboard` | KPIs, sales trend, category chart, best and worst sellers, weekday chart, Pareto chart |
| Menu analytics | `/menu` | Searchable, sortable table of every dish, menu class, K-Means groups |
| Market basket | `/market-basket` | Apriori rules (support, confidence, lift) and combo offers |
| Recommendations | `/recommendations` | Promote, review price, rework, combo and insight cards |
| Dataset | `/dataset` | Files, columns, quality checks, cleaning log, available analyses |
| About | `/about` | Problem statement, method, architecture, limits |

Filters (dates, category, dish) and **CSV export** buttons are on the analysis pages. Exports follow the current filters.

## Dataset

| File | Rows | Columns |
|---|---|---|
| `data/menu_items.csv` | 38 | item_id, item_name, category, price, cost, is_veg |
| `data/orders.csv` | 1,896 | order_id, order_date, order_time, order_type |
| `data/order_items.csv` | 5,833 | order_id, item_id, quantity, unit_price |

Dates run from 2026-01-01 to 2026-06-29. Prices and costs are in INR. To make a fresh copy of the same data, run `python tools/generate_data.py` (it is seeded, so the result is identical). To use your own data, keep the same file names and column names.

## Project structure

```
app.py                 Flask app, pages, JSON API, CSV exports
analysis/              data_loader, data_cleaning, menu_analytics,
                       association_rules, clustering, recommendations
templates/             HTML pages (Jinja2)
static/css, static/js  styles and page scripts (Chart.js is loaded from a CDN)
data/                  the three CSV files
tests/                 unit tests and Flask route tests
reports/               project report, viva Q&A, features/testing/resume notes
tools/generate_data.py synthetic data generator
run_project.bat        one-click Windows launcher
wsgi.py, Procfile      production entry points
```

## Troubleshooting

| Problem | Fix |
|---|---|
| "Python was not found" | Install Python 3.9+ and tick **Add python.exe to PATH**. Reopen the folder and run again. |
| Windows opens the Microsoft Store when `python` is typed | Install Python from python.org, or use `py -3` as shown above. |
| `pip install` fails or is very slow | Check internet. Try `python -m pip install --upgrade pip`, then run the install again. |
| `mlxtend` will not install | Use `pip install -r requirements-core.txt`. The built-in Apriori is used. |
| "Address already in use" | Another program uses port 5000. Run `set PORT=5050` then `python app.py` and open http://127.0.0.1:5050. |
| Charts are empty or show a Chart.js message | The charts library and fonts load from the internet. Connect and reload. Tables and numbers work offline. |
| Red "Missing data file" message | Keep `orders.csv`, `order_items.csv` and `menu_items.csv` in `data/`, or run `python tools/generate_data.py`. |
| Changed a CSV but nothing changed | Reload the page. The app re-reads files when they change on disk. |
| `run_project.bat` window closes at once | Open Command Prompt in the folder and run `run_project.bat` to read the error. |

## Settings (optional)

Set as environment variables (see `.env.example`): `HOST`, `PORT`, `FLASK_DEBUG` (1 for debug), `MENU_DATA_DIR`. There are no passwords, API keys or accounts.

## Deploying online later (optional, not done in this project)

The app has not been deployed anywhere. It is ready for a Python host such as Render, Railway or PythonAnywhere:

1. Put the project in a Git repository (the `.gitignore` is included).
2. Add `gunicorn` to `requirements.txt` for Linux hosts. The included `Procfile` runs `gunicorn wsgi:app`.
3. Set `HOST=0.0.0.0` if the host asks for it, and leave `FLASK_DEBUG` at 0.
4. On Windows servers use `pip install waitress` and `waitress-serve --listen=0.0.0.0:8000 wsgi:app`.

Do not use `python app.py` (the development server) for a public site.
