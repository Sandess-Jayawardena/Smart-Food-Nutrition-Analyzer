Smart Food Nutrition Analyzer

A console-based Python app for searching, comparing, and analysing food nutrition data.

The program loads food data from CSV files and lets users search products, compare nutrition values, check warnings, create a simple nutrition profile, and track their searches over time.

Features
Load food and nutrition data from CSV files
Search products by name, brand, or category
Compare two products
Check product nutrition warnings
Show top products by calories, sugar, salt, fat, or protein
View country nutrition trends
View region nutrition trends
Create and select a nutrition profile
Search products using a selected profile
Track searches, comparisons, warning checks, and profile searches over time
Generate tracking graphs with Matplotlib
Main Menu
1. Load food dataset
2. Search products
3. Compare two products
4. Check product warnings
5. Show top products
6. Country trends
7. Region trends
8. Profile
9. Profile search
10. Tracking
0. Exit
Requirements

Python 3 is required.

Matplotlib is used for graph creation:

py -3 -m pip install matplotlib
How to Run

Open the project folder in a terminal and run:

py -3 main.py

Load the food dataset from the menu before using the other features.

Project Structure
Smart-Food-Nutrition-Analyzer/
│
├── main.py
├── constants.py
├── base_record.py
├── food_product.py
├── nutrition_profile.py
├── data_manager.py
├── nutrition_analyzer.py
│
├── data/
│   ├── products_clean.csv
│   ├── nutrition_clean.csv
│   ├── product_countries.csv
│   ├── country_regions.csv
│   ├── country_year_trends.csv
│   ├── region_year_trends.csv
│   └── data_sources.csv
│
└── reports/
    ├── profiles.csv
    └── tracking_history.csv
Data Files

The app reads food and nutrition data from the data folder.

The app writes saved profiles and tracking history to the reports folder.

Generated graph files are created when option 10 is used:

reports/check_type_tracking_bar_chart.png
reports/risk_score_tracking_line_chart.png

These graph files are generated automatically and are not included in the repository.

Tracking

Option 10 shows tracking over time.

It tracks:

normal searches
product comparisons
warning checks
profile searches

It also tracks average risk score over time and saves the data in:

reports/tracking_history.csv
Risk Score

The risk score is a simple project calculation based on available nutrition data.

It considers calories, sugar, fat, salt, protein, and NOVA processing group.

The score is only for project use and is not medical advice.
