from datetime import datetime
import csv

from constants import (PRODUCTS_FILE, NUTRITION_FILE, PRODUCT_COUNTRIES_FILE, COUNTRY_REGIONS_FILE, COUNTRY_TRENDS_FILE, REGION_TRENDS_FILE, DATA_SOURCES_FILE, REPORT_FILE, REPORT_HISTORY_FILE, PROFILE_FILE)
from food_product import FoodProduct
from nutrition_profile import NutritionProfile

class DataManager:

    def check_data_files(self):
        required_files = [PRODUCTS_FILE, NUTRITION_FILE, PRODUCT_COUNTRIES_FILE, COUNTRY_REGIONS_FILE, COUNTRY_TRENDS_FILE, REGION_TRENDS_FILE, DATA_SOURCES_FILE]

        missing_files = []

        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(file_path.name)

        return missing_files

    def read_products(self):
        products = []

        # Read product rows from the CSV file.
        with open(PRODUCTS_FILE, "r", encoding="utf-8-sig") as file:
            # DictReader gives each CSV row as a dictionary using column names.
            reader = csv.DictReader(file)

            for row in reader:
                product = FoodProduct(row["code"], row["product_name"], row["brands"], row["main_category"], row["created_year"])
                products.append(product)

            return products
    
    def read_nutrition_profiles(self):
        nutrition_profiles = []

        # Read nutrition rows from the CSV file.
        with open(NUTRITION_FILE, "r", encoding = "utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                nutrition = NutritionProfile(row["code"], row["energy_kcal_100g"], row["sugars_100g"], row["fat_100g"], row["salt_100g"], row["proteins_100g"], row["nutriscore_grade"], row["nutriscore_score"], row["nova_group"])
                nutrition_profiles.append(nutrition)

        return nutrition_profiles

    def read_simple_csv(self, file_path):
        rows = []

        # Read smaller lookup/trend CSV files.
        with open(file_path, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                rows.append(row)
                
        return rows

    def load_all_data(self):
        data = {"products": self.read_products(), "nutrition": self.read_nutrition_profiles(), "product_countries": self.read_simple_csv(PRODUCT_COUNTRIES_FILE), "country_regions": self.read_simple_csv(COUNTRY_REGIONS_FILE), "country_trends": self.read_simple_csv(COUNTRY_TRENDS_FILE), "region_trends": self.read_simple_csv(REGION_TRENDS_FILE), "data_sources": self.read_simple_csv(DATA_SOURCES_FILE)}

        return data 

    def write_report(self, report_text):
        REPORT_FILE.parent.mkdir(exist_ok=True)

        # Write the generated report to the reports folder.
        # This saves the report output as a text file.
        with open(REPORT_FILE, "w", encoding="utf-8") as file:
            file.write(report_text)

    def append_report_history(self, report_type):
        REPORT_HISTORY_FILE.parent.mkdir(exist_ok=True)

        file_exists = REPORT_HISTORY_FILE.exists()

        # Record that a report was exported, with the current date and time.
        with open(REPORT_HISTORY_FILE, "a", encoding = "utf-8", newline= "") as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(["generated_at", "report_type"])
            
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), report_type])

    def save_profile(self, profile):
        """Save one user nutrition profile to the profiles CSV file."""
        try:
            PROFILE_FILE.parent.mkdir(exist_ok=True)
            file_exists = PROFILE_FILE.exists()
            fieldnames = ["profile_name", "country", "region", "max_sugar", "include_ultra_processed", "result_limit"]

            with open(PROFILE_FILE, "a", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                if not file_exists:
                    writer.writeheader()

                writer.writerow(profile)

            return True
        except (OSError, csv.Error, ValueError) as error:
            print(f"Could not save profile: {error}")
            return False

    def read_profiles(self):
        """Read saved user nutrition profiles from the profiles CSV file."""
        profiles = []

        if not PROFILE_FILE.exists():
            return profiles

        try:
            with open(PROFILE_FILE, "r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    profiles.append(row)
        except (OSError, csv.Error, UnicodeError) as error:
            print(f"Could not read profiles: {error}")
            return []

        return profiles
            
