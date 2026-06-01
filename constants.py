from pathlib import Path

#folders

# pathlib helps build file paths that work across operating systems.
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

#data files

# Constants keep CSV paths and warning limits in one place.
PRODUCTS_FILE = DATA_DIR / "products_clean.csv"
NUTRITION_FILE = DATA_DIR / "nutrition_clean.csv"
PRODUCT_COUNTRIES_FILE = DATA_DIR / "product_countries.csv"
COUNTRY_REGIONS_FILE = DATA_DIR / "country_regions.csv"
COUNTRY_TRENDS_FILE = DATA_DIR / "country_year_trends.csv"
REGION_TRENDS_FILE = DATA_DIR / "region_year_trends.csv"
DATA_SOURCES_FILE = DATA_DIR / "data_sources.csv"

#report files

REPORT_FILE = REPORTS_DIR / "nutrition_report.txt"
REPORT_HISTORY_FILE = REPORTS_DIR / "report_history.csv"

#Health warning threshold per 100g

HIGH_SUGAR_LIMIT = 22.5
HIGH_FAT_LIMIT = 17.5 
HIGH_SALT_LIMIT = 1.5
HIGH_CALORIE_LIMIT = 400

EXIT_OPTION = "0"
