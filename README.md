# Smart Food Nutrition Analyzer

A Python console app for searching and comparing food products using Open Food Facts nutrition data.

## Features

* Search products by name, brand, or category
* Compare two products by product code
* Show health warnings for sugar, fat, salt, calories, and ultra-processing
* Sort products by calories, sugar, fat, salt, protein, Nutri-Score, or NOVA group
* View country and region nutrition trends
* Export a text report

## Data

The app uses cleaned CSV files based on Open Food Facts data. The data includes product details, nutrition values, countries, regions, and yearly trend summaries.

## Run

```powershell
py -3 main.py
```

Load the data first from the menu, then choose the feature you want to use.

## Output

Exported reports are saved in the `reports` folder.

## Note

Open Food Facts is crowdsourced, so some values may be missing or unusual. The program filters unrealistic values during sorting.
