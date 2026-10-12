# Hotel Booking Analysis for Understanding Customer Behavior and Cancellation Trends

## Project Overview

This project analyses hotel booking data to understand customer behaviour and identify patterns associated with booking cancellations.

The analysis uses MySQL for data storage, Pandas for data cleaning and exploratory analysis, Plotly and Cufflinks for interactive visualisations, and Streamlit for the final interactive dashboard.

## Dataset

**Dataset:** Hotel Bookings Analysis  
**Source:** https://www.kaggle.com/datasets/thedevastator/hotel-bookings-analysis

The dataset contains hotel booking information including hotel type, cancellation status, lead time, arrival date, customer type, market segment, average daily rate (ADR), stay duration, previous cancellations, repeated guest status, special requests and reservation status.

## Analysis Questions

1. What is the overall cancellation rate, and how does it differ between hotel types?
2. How are lead time and average daily rate (ADR) associated with cancellations?
3. Which market segments and customer types show the highest cancellation rates?
4. How do booking and cancellation volumes change over time?
5. How do stay characteristics and special requests differ between cancelled and non-cancelled bookings?

## Technologies Used

- Python
- MySQL
- Pandas
- NumPy
- SQLAlchemy
- PyMySQL
- Plotly
- Cufflinks
- Streamlit
- Jupyter Notebook

## Project Structure

```text
HotelBookingAnalysis/
│
├── data/
│   └── hotel_bookings.csv
│
├── notebooks/
│   └── hotel_booking_analysis.ipynb
│
├── sql/
│   └── create_database.sql
│
├── app.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Create a Virtual Environment

Open PowerShell in the project folder and run:

```powershell
py -3.11 -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install Required Libraries

```powershell
pip install -r requirements.txt
```

## MySQL Setup

Open MySQL Workbench and run:

```text
sql/create_database.sql
```

This script creates:

```text
Database: hotel_booking_analysis
Table: hotel_bookings
User: hotel_user
```

The default project credentials used in the supplied files are:

```text
Host: localhost
Port: 3306
User: hotel_user
Password: HotelProject@2026
Database: hotel_booking_analysis
```

If a different password is used, update the password in both:

```text
hotel_booking_analysis.ipynb
app.py
```

## Load the Dataset into MySQL

Download the dataset from Kaggle and place the CSV file inside:

```text
data/hotel_bookings.csv
```

Import the dataset into the MySQL table:

```text
hotel_bookings
```

The table must contain the columns defined in `create_database.sql`.

### CSV Import Note

When importing the CSV using MySQL Workbench, import the data into the
existing `hotel_bookings` table.

The CSV contains an additional `index` column that is not required by the
database table. During column mapping, leave the `index` column unchecked
and map all remaining source columns to destination columns with the same
names.

After a successful import, the raw dataset should contain 119,390 rows.

After importing, verify the data in MySQL using:

```sql
SELECT COUNT(*) AS total_rows
FROM hotel_bookings;
```

```sql
SELECT *
FROM hotel_bookings
LIMIT 10;
```

## Run the Jupyter Notebook

Start Jupyter Notebook:

```powershell
jupyter notebook
```

Open:

```text
notebooks/hotel_booking_analysis.ipynb
```

Run all cells from top to bottom.

The notebook performs:

- MySQL connection and data retrieval
- row count, sample row and null verification
- data type checking
- missing value handling
- duplicate removal
- outlier handling
- Pandas exploratory analysis
- cancellation analysis
- hotel comparison
- market segment analysis
- customer behaviour analysis
- monthly booking trend analysis
- lead time analysis
- ADR analysis
- correlation analysis
- Plotly and Cufflinks visualisations
- written observations
- key insights
- recommendations

## Run the Streamlit Dashboard

From the project folder, run:

```powershell
streamlit run app.py
```

The dashboard will normally open at:

```text
http://localhost:8501
```

## Dashboard Features

The dashboard displays key metrics including:

- Total Bookings
- Cancelled Bookings
- Cancellation Rate
- Average ADR
- Average Lead Time

Interactive filters are provided for:

- Hotel Type
- Arrival Year
- Arrival Month
- Market Segment
- Customer Type
- Booking Status
- Lead Time

The dashboard also includes interactive visualisations for:

- cancellation status
- cancellation rate by hotel type
- cancellation rate by market segment
- monthly booking and cancellation trends
- bookings by arrival month
- lead time distribution
- ADR distribution
- cancellation rate by customer type
- new versus repeated guests

The Insights section automatically updates according to the selected filters and displays key observations and recommendations.

## Deliverables

The project includes the required deliverables:

1. `create_database.sql` – MySQL database and table creation script
2. `hotel_booking_analysis.ipynb` – data cleaning, analysis, visualisations and observations
3. `app.py` – interactive Streamlit dashboard
4. `requirements.txt` – required Python libraries
5. `README.md` – project description and instructions for running the project
