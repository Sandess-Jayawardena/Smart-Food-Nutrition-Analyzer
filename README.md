# Smart Food Nutrition Analyzer

Smart Food Nutrition Analyzer is a Python console app that helps users make healthier food choices. It searches products, compares nutrition risk scores, uses personal nutrition profiles, saves decision reports, tracks report history, shows country and region trends, and creates trend line charts.

## Run

```powershell
py main.py
```

Load the food dataset from the main menu before using the analysis features.

## Matplotlib

Install Matplotlib to generate trend line charts:

```powershell
py -3 -m pip install matplotlib
```

## Main Features

* Product search
* Product comparison
* Health warning report
* Risk score and risk level
* User nutrition profiles
* Profile-based product finder
* Nutrition decision report
* Report history tracking
* Country and region trends
* Matplotlib trend chart

## Files Read

The app reads the CSV files in the `data` folder for products, nutrition values, countries, regions, and yearly trends.

## Files Written

* `reports/profiles.csv`
* `reports/report_history.csv`
* `reports/nutrition_decision_report.txt`
* `reports/trend_line_chart.png`


Open Food Facts data is crowdsourced, so some nutrition values may be missing or unusual.
