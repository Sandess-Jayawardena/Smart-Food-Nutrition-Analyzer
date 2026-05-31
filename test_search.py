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

results = analyzer.search_products("indomie", limit=5)

print(f"Search results found: {len(results)}")

for item in results:
    product = item["product"]
    nutrition = item["nutrition"]
    countries = item["countries"]

    print(product.display_product())
    print(nutrition.display_nutrition())
    print("Countries:", countries)
    print("-" * 50)