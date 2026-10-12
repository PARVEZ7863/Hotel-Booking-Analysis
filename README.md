# Hotel Booking Analysis for Understanding Customer Behavior and Cancellation Trends

## Overview
Analyze hotel bookings and cancellation patterns using MySQL, Python, Pandas, Plotly/Cufflinks and Streamlit.

## Dataset
Kaggle: https://www.kaggle.com/datasets/thedevastator/hotel-bookings-analysis
Original CSV contains 119,390 rows. Download `hotel_bookings.csv` from Kaggle and put it in `data/` (or import directly from your local download).

## Project files
- `sql/create_database.sql` — MySQL database and table schema, plus verification queries
- `notebooks/hotel_booking_analysis.ipynb` — analysis, charts and observations
- `app.py` — interactive Streamlit dashboard
- `requirements.txt` — Python dependencies

## Setup (Windows / VS Code)
1. Create or open your MySQL database using `sql/create_database.sql` in MySQL Workbench. Import the CSV into the existing `hotel_bookings` table; skip the extra CSV `index` column. Verify `SELECT COUNT(*) FROM hotel_bookings;` returns 119390 after a complete import.
2. Install packages: `py -3.13 -m pip install -r requirements.txt`.
3. In the **same PowerShell terminal** used to launch your app, set the password privately: `$env:HOTEL_DB_PASSWORD = Read-Host "MySQL password"`. Do not save it in GitHub. The Python files use `hotel_user` on localhost by default.
4. Open `notebooks/hotel_booking_analysis.ipynb` in VS Code, select the correct Python kernel, and run cells in order.
5. From the project root run `py -3.13 -m streamlit run app.py`.

## Analysis questions
1. What percentage of bookings are cancelled?
2. How do cancellation rates differ by hotel type and market segment?
3. How do lead time and ADR relate to cancellations?
4. How do booking volumes change across months?
5. What customer characteristics are associated with cancellations?

## Notes
- Dashboard totals can be smaller than imported raw rows because the app removes duplicates and bookings with zero guests.
- The notebook's saved cell outputs are cleared in this GitHub copy. Run it with your local MySQL database to regenerate the charts.
- Never commit credentials or `.env` files. If a password was previously published, change it in MySQL.
