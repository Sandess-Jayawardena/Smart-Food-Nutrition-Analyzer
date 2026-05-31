from data_manager import DataManager
from nutrition_analyzer import NutritionAnalyzer

data_manager = DataManager()
data = data_manager.load_all_data()

analyzer = NutritionAnalyzer(
    data["products"],
    data["nutrition"],
    data["product_countries"],
    data["country_regions"],
    data["country_trends"],
    data["region_trends"],
)

print("Products:", len(data["products"]))
print("Nutrition profiles:", len(data["nutrition"]))
print("Combined products:", analyzer.count_combined_products())

sample_code = data["products"][0].code
combined = analyzer.get_combined_product_info(sample_code)

print("\nSample combined product:")
print(combined["product"].display_product())
print(combined["nutrition"].display_nutrition())
print("Countries:", combined["countries"])