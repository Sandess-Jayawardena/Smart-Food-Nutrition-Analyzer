import csv

from constants import (PRODUCTS_FILE, NUTRITION_FILE, PRODUCT_COUNTRIES_FILE, COUNTRY_REGIONS_FILE, COUNTRY_TRENDS_FILE, REGION_TRENDS_FILE, DATA_SOURCES_FILE)
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

        with open(PRODUCTS_FILE, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                product = FoodProduct(row["code"], row["product_name"], row["brands"], row["main_category"], row["created_year"])
                products.append(product)

            return products
    
    def read_nutrition_profiles(self):
        nutrition_profiles = []

        with open(NUTRITION_FILE, "r", encoding = "utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                nutrition = NutritionProfile(row["code"], row["energy_kcal_100g"], row["sugars_100g"], row["fat_100g"], row["salt_100g"], row["proteins_100g"], row["nutriscore_grade"], row["nutriscore_score"], row["nova_group"])
                nutrition_profiles.append(nutrition)

        return nutrition_profiles

    def read_simple_csv(self, file_path):
        rows = []

        with open(file_path, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                rows.append(row)
                
        return rows

    def load_all_data(self):
        data = {"products": self.read_products(), "nutrition": self.read_nutrition_profiles(), "product_countries": self.read_simple_csv(PRODUCT_COUNTRIES_FILE), "country_regions": self.read_simple_csv(COUNTRY_REGIONS_FILE), "country_trends": self.read_simple_csv(COUNTRY_TRENDS_FILE), "region_trends": self.read_simple_csv(REGION_TRENDS_FILE), "data_sources": self.read_simple_csv(DATA_SOURCES_FILE)}

        return data 

