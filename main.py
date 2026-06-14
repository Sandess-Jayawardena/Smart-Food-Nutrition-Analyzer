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

def display_numbered_results(results):
    """Display product search results with numbers so the user can choose easily."""
    for index, item in enumerate(results, start=1):
        product = item["product"]
        nutrition = item["nutrition"]
        countries = item["countries"]
        calories = "Unknown" if nutrition.energy_kcal_100g is None else f"{nutrition.energy_kcal_100g} kcal"
        sugar = "Unknown" if nutrition.sugars_100g is None else f"{nutrition.sugars_100g}g"
        salt = "Unknown" if nutrition.salt_100g is None else f"{nutrition.salt_100g}g"

        print(f"{index}. {product.product_name}")
        print(f"   Code: {product.code}")
        print(f"   Brand: {product.brands}")
        print(f"   Calories: {calories} | Sugar: {sugar} | Salt: {salt}")
        print(f"   Risk: {nutrition.calculate_risk_score()} | {nutrition.get_risk_level()}")
        print(f"   Countries: {', '.join(countries)}")
        print("-" * 50)

def select_product_from_search(analyzer, prompt, excluded_code=None):
    """Let the user search for a product and select one result by number."""
    while True:
        search_text = input(prompt).strip()

        if search_text == "0":
            print("\nCancelled.")
            return None

        results = analyzer.search_products(search_text, limit=10)

        if excluded_code is not None:
            results = [item for item in results if item["product"].code != excluded_code]

        if len(results) == 0:
            print("\nNo products found. Try a shorter word or check the spelling.")
            print("Type 0 to cancel.")
            continue

        print("\nChoose one product:")
        print("=" * 50)
        display_numbered_results(results)

        try:
            choice = int(input("Enter the product number, or 0 to search again: ").strip())
        except ValueError:
            print("\nInvalid number. Please type one of the numbers shown.")
            continue

        if choice == 0:
            print("\nSearch again.")
            continue

        if choice < 1 or choice > len(results):
            print("\nChoice out of range. Please choose one of the numbers shown.")
            continue

        return results[choice - 1]   

def search_products(analyzer):
    """Search products and display matching nutrition details."""
    search_text = input("Enter product name, brand, or category: ").strip()
    limit = get_result_limit()
    results = analyzer.search_products(search_text, limit)

    if len(results) == 0:
        print("\nNo products found.")
        return

    print(f"\nSearch results found: {len(results)}")
    print("=" * 50)
    display_numbered_results(results)
    
def compare_products(analyzer):
    """Search for two products and compare their nutrition values."""
    print("\nFirst product")
    first = select_product_from_search(analyzer, "Search for the first product: ")

    if first is None:
        return

    print("\nSecond product")
    second = select_product_from_search(analyzer, "Search for the second product: ", first["product"].code)

    if second is None:
        return

    comparison = analyzer.compare_products(first["product"].code, second["product"].code)

    if comparison is None:
        print("\nOne or both products were not found.")
        return

    print("\nPRODUCT COMPARISON")
    print("=" * 50)

    print("\nProduct 1:")
    print(comparison["first"]["product"].display_product())
    print(comparison["first"]["nutrition"].display_nutrition())
    print(f"Countries: {', '.join(comparison['first']['countries'])}")

    print("\nProduct 2:")
    print(comparison["second"]["product"].display_product())
    print(comparison["second"]["nutrition"].display_nutrition())
    print(f"Countries: {', '.join(comparison['second']['countries'])}")

    first_product = comparison["first"]["product"]
    first_nutrition = comparison["first"]["nutrition"]
    second_product = comparison["second"]["product"]
    second_nutrition = comparison["second"]["nutrition"]
    first_risk = first_nutrition.calculate_risk_score()
    second_risk = second_nutrition.calculate_risk_score()
    first_sugar = "Unknown" if first_nutrition.sugars_100g is None else f"{first_nutrition.sugars_100g}g"
    second_sugar = "Unknown" if second_nutrition.sugars_100g is None else f"{second_nutrition.sugars_100g}g"
    first_salt = "Unknown" if first_nutrition.salt_100g is None else f"{first_nutrition.salt_100g}g"
    second_salt = "Unknown" if second_nutrition.salt_100g is None else f"{second_nutrition.salt_100g}g"

    print("\nQUICK DECISION")
    print("=" * 50)
    print(f"Product 1 risk score: {first_risk}")
    print(f"Product 2 risk score: {second_risk}")
    print(f"Product 1 sugar: {first_sugar}")
    print(f"Product 2 sugar: {second_sugar}")
    print(f"Product 1 salt: {first_salt}")
    print(f"Product 2 salt: {second_salt}")

    if first_risk < second_risk:
        print(f"Recommendation: {first_product.product_name} has the lower risk score.")
    elif second_risk < first_risk:
        print(f"Recommendation: {second_product.product_name} has the lower risk score.")
    else:
        print("Recommendation: Both products have the same risk score.")

def show_health_warning_report(analyzer):
    """Search for one product and show its health warning report."""
    selected = select_product_from_search(analyzer, "Search for the product you want to check: ")

    if selected is None:
        return

    code = selected["product"].code
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
