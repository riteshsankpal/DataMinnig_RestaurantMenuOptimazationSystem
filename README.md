# Restaurant Menu Optimization System

A college Data Mining project. It reads restaurant order records, then shows best and worst selling dishes, revenue and estimated profit, dishes that are ordered together (Apriori), groups of similar dishes (K-Means), a Pareto analysis, and rule-based menu recommendations, all in a website that runs on your own computer.

> **The CSV files in `data/` are synthetic demonstration data** created by `tools/generate_data.py`. They are not from a real restaurant. Every number on the website is calculated from these files when you open a page, and it is not hardcoded.

**Quick start on Windows (recommended)
**
Download the project ZIP and right-click it → Extract All.

Open the extracted Restaurant_Menu_Optimization_System folder containing app.py and requirements.txt.

Double-click run_project.bat.

Wait while the project sets itself up. The first run requires an internet connection to install the required libraries.

Your browser should open automatically. If it does not, visit http://127.0.0.1:5000.

If Windows Smart App Control blocks run_project.bat:

Do not disable Windows security. Instead, follow the manual setup instructions below to launch the application through Command Prompt.

**You need Python 3.9 or newer from python.org. During installation, enable Add python.exe to PATH if that option is available.
**
Download the project ZIP and right-click it → Extract All.

Open the extracted Restaurant_Menu_Optimization_System folder containing app.py and requirements.txt.

Double-click run_project.bat.

Wait while the project sets itself up. The first run requires an internet connection to install the required libraries.

Your browser should open automatically. If it does not, visit http://127.0.0.1:5000.

If Windows Smart App Control blocks run_project.bat:

Do not disable Windows security. Instead, follow the manual setup instructions below to launch the application through Command Prompt.

You need Python 3.9 or newer from python.org. During installation, enable Add python.exe to PATH if that option is available.

**Manual setup (if the launcher is blocked or you prefer commands)
**
Open the project folder containing app.py.

Click the File Explorer address bar, type cmd, and press Enter.

Create a virtual environment:

py -3 -m venv .venv

Skip this step if .venv already exists.

Install the project dependencies:

.venv\Scripts\python.exe -m pip install -r requirements.txt

Start the application:

.venv\Scripts\python.exe app.py

Open http://127.0.0.1:5000 in your browser.

Important: Keep the Command Prompt window open while using the application. Press Ctrl+C in that window to stop it.

If py is not recognized, install Python from the official website and try again. If requirements.txt cannot install mlxtend, try:

.venv\Scripts\python.exe -m pip install -r requirements-core.txt

The application includes a fallback implementation of the Apriori algorithm.

**Run the tests
**
From the project folder, run:

.venv\Scripts\python.exe -m unittest discover -s tests -v

**Troubleshooting
**
Problem

Solution

Windows blocks run_project.bat

Use the Manual setup instructions above. Do not disable Smart App Control.

Python was not found

Install Python 3.9+ from python.org.

Dependencies fail to install

Check your internet connection and retry.

Address already in use

Another application may be using port 5000. Stop that application or configure a different port.

Missing data files

Check that the required CSV files exist in the data/ folder, or regenerate them using the included data-generation script.

Launcher window closes immediately

Open Command Prompt in the project folder and follow the Manual setup instructions to see any errors.

## Settings (optional)

Set as environment variables (see `.env.example`): `HOST`, `PORT`, `FLASK_DEBUG` (1 for debug), `MENU_DATA_DIR`. There are no passwords, API keys or accounts.

## Deploying online later (optional, not done in this project)

The app has not been deployed anywhere. It is ready for a Python host such as Render, Railway or PythonAnywhere:

1. Put the project in a Git repository (the `.gitignore` is included).
2. Add `gunicorn` to `requirements.txt` for Linux hosts. The included `Procfile` runs `gunicorn wsgi:app`.
3. Set `HOST=0.0.0.0` if the host asks for it, and leave `FLASK_DEBUG` at 0.
4. On Windows servers use `pip install waitress` and `waitress-serve --listen=0.0.0.0:8000 wsgi:app`.

Do not use `python app.py` (the development server) for a public site.
