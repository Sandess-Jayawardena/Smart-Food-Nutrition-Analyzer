from pathlib import Path

# Central constants keep paths, limits, and menu values consistent across modules.
# pathlib builds file paths that work across operating systems.
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

# Data files read by DataManager.
PRODUCTS_FILE = DATA_DIR / "products_clean.csv"
NUTRITION_FILE = DATA_DIR / "nutrition_clean.csv"
PRODUCT_COUNTRIES_FILE = DATA_DIR / "product_countries.csv"
COUNTRY_REGIONS_FILE = DATA_DIR / "country_regions.csv"
COUNTRY_TRENDS_FILE = DATA_DIR / "country_year_trends.csv"
REGION_TRENDS_FILE = DATA_DIR / "region_year_trends.csv"

# Files written by profile and tracking features.
TRACKING_HISTORY_FILE = REPORTS_DIR / "tracking_history.csv"
PROFILE_FILE = REPORTS_DIR / "profiles.csv"
CHECK_TYPE_CHART_FILE = REPORTS_DIR / "check_type_tracking_bar_chart.png"
RISK_SCORE_CHART_FILE = REPORTS_DIR / "risk_score_tracking_line_chart.png"

# Health warning thresholds per 100g.
HIGH_SUGAR_LIMIT = 22.5
HIGH_FAT_LIMIT = 17.5 
HIGH_SALT_LIMIT = 1.5
HIGH_CALORIE_LIMIT = 400
