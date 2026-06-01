from data_manager import DataManager
from nutrition_analyzer import NutritionAnalyzer
from constants import EXIT_OPTION

def display_menu():
    # Console menu shown after each action.
    print("\nSMART FOOD NUTRITION ANALYZER")
    print("=" * 35)
    print("1. Load data")
    print("2. Search products")
    print("3. Compare two products")
    print("4. View health warning report")
    print("5. Sort products by nutrition value")
    print("6. View country trend report")
    print("7. View region trend report")
    print("8. Export full report")
    print("0. Exit")

def load_program_data():
    data_manager = DataManager()
    missing_files = data_manager.check_data_files()

    if len(missing_files) > 0:
        print("\nMissing data files:")

        for file_name in missing_files:
            print(f" - {file_name}")

        return None, None

    data = data_manager.load_all_data()

    analyzer = NutritionAnalyzer(data["products"], data["nutrition"], data["product_countries"], data["country_regions"], data["country_trends"], data["region_trends"])

    print("\nData loaded successfully.")
    print(f"Products loaded: {len(data['products'])}")
    print(f"Nutrition profiles loaded: {len(data['nutrition'])}")
    print(f"Combined products: {analyzer.count_combined_products()}")

    return data_manager, analyzer

def get_result_limit():
    # input() returns text, so int() converts it to a number.
    try:
        limit = int(input("How many results do you want to show? ").strip())
    except ValueError:
        # try/except handles letters or empty input without crashing.
        return 10

    if limit < 1:
        return 10

    return limit

def search_products(analyzer):
    # User input is read as a string and stripped of extra spaces.
    search_text = input("Enter product name, brand, or category: ").strip()
    limit = get_result_limit()
    results = analyzer.search_products(search_text, limit)

    if len(results) == 0:
        print("\nNo products found.")
        return

    print(f"\nSearch results found: {len(results)}")
    print("=" * 50)

    for item in results:
        product = item["product"]
        nutrition = item["nutrition"]
        countries = item["countries"]

        print(product.display_product())
        print(nutrition.display_nutrition())
        print(f"Countries: {', '.join(countries)}")
        print("-" * 50)
    
def compare_products(analyzer):
    first_code = input("Enter first product code: ").strip()
    second_code = input("Enter second product code: ").strip()

    comparison = analyzer.compare_products(first_code, second_code)

    if comparison is None:
        print("\nOne or both products were not found.")
        return

    first = comparison["first"]
    second = comparison["second"]

    print("\nPRODUCT COMPARISON")
    print("=" * 50)

    print("\nProduct 1:")
    print(first["product"].display_product())
    print(first["nutrition"].display_nutrition())
    print(f"Countries: {', '.join(first['countries'])}")

    print("\nProduct 2:")
    print(second["product"].display_product())
    print(second["nutrition"].display_nutrition())
    print(f"Countries: {', '.join(second['countries'])}")

def show_health_warning_report(analyzer):
    code = input("Enter product code: ").strip()
    report = analyzer.get_health_warning_report(code)

    if report is None:
        print("\nProduct not found.")
    else:
        print("\n" + report)


def sort_products(analyzer):
    print("\nSort by:")
    print("1. Calories")
    print("2. Sugar")
    print("3. Fat")
    print("4. Salt")
    print("5. Protein")
    print("6. Nutri-Score")
    print("7. NOVA group")

    choice = input("Choose a sorting option: ").strip()

    field_map = {
        "1": "energy_kcal_100g",
        "2": "sugars_100g",
        "3": "fat_100g",
        "4": "salt_100g",
        "5": "proteins_100g",
        "6": "nutriscore_score",
        "7": "nova_group"
    }

    label_map = {
        "energy_kcal_100g": "Calories",
        "sugars_100g": "Sugar",
        "fat_100g": "Fat",
        "salt_100g": "Salt",
        "proteins_100g": "Protein",
        "nutriscore_score": "Nutri-Score",
        "nova_group": "NOVA group"
    }

    if choice not in field_map:
        print("\nInvalid sorting option.")
        return

    field_name = field_map[choice]
    limit = get_result_limit()
    results = analyzer.sort_products_by_nutrition(field_name, limit)

    print(f"\nTop {limit} products by {label_map[field_name]}")
    print("=" * 50)

    for item in results:
        product = item["product"]
        value = item["value"]
        countries = item["countries"]

        print(f"{product.product_name} | {label_map[field_name]}: {round(value, 2)} | Countries: {', '.join(countries)}")


def show_country_report(analyzer):
    country = input("Enter country name: ").strip()
    rows = analyzer.get_country_report(country)
    report = analyzer.format_trend_report(f"Country Report: {country}", rows)

    print("\n" + report)


def show_region_report(analyzer):
    region = input("Enter region name: ").strip()
    rows = analyzer.get_region_report(region)
    report = analyzer.format_trend_report(f"Region Report: {region}", rows)

    print("\n" + report)


def export_full_report(data_manager, analyzer):
    report = analyzer.generate_full_report()

    data_manager.write_report(report)
    data_manager.append_report_history("full_report")

    print("\nReport exported successfully.")
    print("Check the reports folder.")


def main():
    data_manager = None
    analyzer = None

    while True:
        display_menu()
        # The menu choice is also string input from the console.
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            data_manager, analyzer = load_program_data()

        elif choice == "2":
            # Menu features need loaded data before using the analyzer.
            if analyzer is None:
                print("\nPlease load the data first.")
            else:
                search_products(analyzer)

        elif choice == "3":
            if analyzer is None:
                print("\nPlease load the data first.")
            else:
                compare_products(analyzer)

        elif choice == "4":
            if analyzer is None:
                print("\nPlease load the data first.")
            else:
                show_health_warning_report(analyzer)

        elif choice == "5":
            if analyzer is None:
                print("\nPlease load the data first.")
            else:
                sort_products(analyzer)

        elif choice == "6":
            if analyzer is None:
                print("\nPlease load the data first.")
            else:
                show_country_report(analyzer)

        elif choice == "7":
            if analyzer is None:
                print("\nPlease load the data first.")
            else:
                show_region_report(analyzer)

        elif choice == "8":
            # Export needs both the analyzer and data manager.
            if analyzer is None or data_manager is None:
                print("\nPlease load the data first.")
            else:
                export_full_report(data_manager, analyzer)

        elif choice == EXIT_OPTION:
            print("\nThank you for using Smart Food Nutrition Analyzer. Goodbye!")
            break

        else:
            print("\nInvalid choice. Please enter a number from the menu.")


if __name__ == "__main__":
    main()
