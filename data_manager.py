from datetime import datetime
import csv

from constants import (
    PRODUCTS_FILE, NUTRITION_FILE, PRODUCT_COUNTRIES_FILE, COUNTRY_REGIONS_FILE,
    COUNTRY_TRENDS_FILE, REGION_TRENDS_FILE, TRACKING_HISTORY_FILE, PROFILE_FILE
)
from food_product import FoodProduct
from nutrition_profile import ProductNutrition

PROFILE_FIELDS = "profile_name country region max_sugar include_ultra_processed result_limit start_date".split()
TRACKING_FIELDS = (
    "timestamp check_type profile_name search_text product_checked "
    "second_product results_found best_product average_risk_score"
).split()

class DataManager:
    """Read project CSV data and save profiles and tracking history."""

    def read_csv_rows(self, file_path):
        """Read a CSV file and return dictionary rows safely."""
        if not file_path.exists():
            return []

        try:
            with open(file_path, "r", encoding="utf-8-sig") as file:
                return list(csv.DictReader(file))
        except (OSError, csv.Error, UnicodeError) as error:
            print(f"Could not read {file_path.name}: {error}")
            return []

    def write_csv_rows(self, file_path, rows, fieldnames):
        """Rewrite a CSV file with a header and dictionary rows."""
        try:
            file_path.parent.mkdir(exist_ok=True)

            with open(file_path, "w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            return True
        except (OSError, csv.Error, ValueError) as error:
            print(f"Could not write {file_path.name}: {error}")
            return False

    def append_csv_row(self, file_path, row, fieldnames):
        """Append one dictionary row and create the header when needed."""
        try:
            file_path.parent.mkdir(exist_ok=True)
            needs_header = not file_path.exists() or file_path.stat().st_size == 0

            with open(file_path, "a", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                if needs_header:
                    writer.writeheader()

                writer.writerow(row)

            return True
        except (OSError, csv.Error, ValueError) as error:
            print(f"Could not append to {file_path.name}: {error}")
            return False

    def check_data_files(self):
        """Return the names of required data files that are missing."""
        required_files = [
            PRODUCTS_FILE, NUTRITION_FILE, PRODUCT_COUNTRIES_FILE,
            COUNTRY_REGIONS_FILE, COUNTRY_TRENDS_FILE, REGION_TRENDS_FILE
        ]
        return [file_path.name for file_path in required_files if not file_path.exists()]

    def read_products(self):
        """Read product records from the products CSV file."""
        products = []

        # Convert each CSV dictionary into a FoodProduct object.
        for row in self.read_csv_rows(PRODUCTS_FILE):
            products.append(FoodProduct(row["code"], row["product_name"], row["brands"], row["main_category"]))

        return products
    
    def read_nutrition_profiles(self):
        """Read nutrition records from the nutrition CSV file."""
        nutrition_profiles = []

        # Convert each nutrition row into an object with safe numeric values.
        for row in self.read_csv_rows(NUTRITION_FILE):
            nutrition = ProductNutrition(
                row["code"], row["energy_kcal_100g"], row["sugars_100g"],
                row["fat_100g"], row["salt_100g"], row["proteins_100g"],
                row["nova_group"]
            )
            nutrition_profiles.append(nutrition)

        return nutrition_profiles

    def load_all_data(self):
        """Load all project CSV data into one dictionary."""
        return {
            "products": self.read_products(),
            "nutrition": self.read_nutrition_profiles(),
            "product_countries": self.read_csv_rows(PRODUCT_COUNTRIES_FILE),
            "country_regions": self.read_csv_rows(COUNTRY_REGIONS_FILE),
            "country_trends": self.read_csv_rows(COUNTRY_TRENDS_FILE),
            "region_trends": self.read_csv_rows(REGION_TRENDS_FILE)
        }

    def save_tracking_row(self, check_type, profile_name, search_text, product_checked, second_product, results_found, best_product, average_risk_score):
        """Append one automatic tracking history row."""
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "check_type": check_type,
            "profile_name": profile_name or "Without profile",
            "search_text": search_text,
            "product_checked": product_checked,
            "second_product": second_product,
            "results_found": results_found,
            "best_product": best_product,
            "average_risk_score": average_risk_score
        }
        return self.append_csv_row(TRACKING_HISTORY_FILE, row, TRACKING_FIELDS)

    def read_tracking_history(self):
        """Read automatic tracking history."""
        return self.read_csv_rows(TRACKING_HISTORY_FILE)

    def save_profile(self, profile):
        """Save one user nutrition profile to the profiles CSV file."""
        # Store simple CSV-friendly values instead of Python Boolean text.
        new_profile = {
            "profile_name": str(profile.get("profile_name") or "Default profile").strip(),
            "country": str(profile.get("country") or "").strip(),
            "region": str(profile.get("region") or "").strip(),
            "max_sugar": profile.get("max_sugar", ""),
            "include_ultra_processed": "yes" if profile.get("include_ultra_processed") else "no",
            "result_limit": profile.get("result_limit", 10),
            "start_date": str(profile.get("start_date") or "")
        }
        profile_name = new_profile["profile_name"].lower()
        # Replace an older profile when the same profile name is saved again.
        profiles = [
            saved for saved in self.read_profiles()
            if str(saved.get("profile_name", "") or "").strip().lower() != profile_name
        ]
        profiles.append(new_profile)

        for saved in profiles:
            saved["include_ultra_processed"] = "yes" if saved["include_ultra_processed"] in [True, "yes", "true", "1"] else "no"

        return self.write_csv_rows(PROFILE_FILE, profiles, PROFILE_FIELDS)

    def read_profiles(self):
        """Read saved user nutrition profiles from the profiles CSV file."""
        profiles = {}

        for row in self.read_csv_rows(PROFILE_FILE):
            # Nested loop: any() checks each value inside the current CSV row.
            # Empty rows are skipped before profile fields are processed.
            if not any(str(value or "").strip() for value in row.values()):
                continue

            name = str(row.get("profile_name", "") or "").strip().lower()

            if name:
                row["include_ultra_processed"] = str(row.get("include_ultra_processed", "")).lower() in ["yes", "true", "1"]
                try:
                    datetime.strptime(row.get("start_date", ""), "%Y-%m-%d")
                except (TypeError, ValueError):
                    row["start_date"] = ""
                profiles[name] = row

        return list(profiles.values())
            
