import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from constants import CHECK_TYPE_CHART_FILE, RISK_SCORE_CHART_FILE
from data_manager import DataManager
from nutrition_analyzer import NutritionAnalyzer

MENU = [
    "1. Load food dataset",
    "2. Search products",
    "3. Compare two products",
    "4. Check product warnings",
    "5. Show top products",
    "6. Country trends",
    "7. Region trends",
    "8. Profile",
    "9. Profile search",
    "10. Tracking",
    "0. Exit"
]

# Some product names contain international characters, so use UTF-8 when the
# current terminal supports changing its output encoding.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def ask_text(prompt, default=""):
    """Read text without crashing when automated input ends."""
    try:
        return input(prompt).strip()
    except EOFError:
        return default


def ask_number(prompt, default, number_type=float, minimum=0, maximum=None):
    """Read a number and use a safe default when it is invalid."""
    try:
        number = number_type(ask_text(prompt, str(default)))
    except ValueError:
        print(f"Invalid number. Using {default}.")
        return default

    if number < minimum:
        print(f"Number is too small. Using {default}.")
        return default
    if maximum is not None and number > maximum:
        print(f"Number is too large. Using {maximum}.")
        return maximum

    return number


def ask_menu_choice():
    """Read the main menu choice as an integer from 0 to 10."""
    while True:
        try:
            choice = int(ask_text("\nType a number: "))
        except ValueError:
            print("\nPlease enter a number from 0 to 10.")
            continue

        if 0 <= choice <= 10:
            return choice

        print("\nPlease enter a number from 0 to 10.")


def ask_choice(prompt, choices, default="0"):
    """Keep asking until the user enters one allowed choice."""
    while True:
        choice = ask_text(prompt, default)

        if choice in choices:
            return choice

        print("Please type one of the numbers shown.")


def show_menu():
    """Print the main program menu."""
    print("\nSMART FOOD NUTRITION ANALYZER\n")

    for line in MENU:
        print(line)


def data_is_loaded(analyzer):
    """Check that the food data is ready before an analysis option runs."""
    if analyzer is None:
        print("\nPlease load the food dataset first.")
        return False

    return True


def show_value(value, unit=""):
    """Format a nutrition value or show Unknown when data is missing."""
    return "Unknown" if value is None else f"{value}{unit}"


def selected_profile_name(profile):
    """Return the selected profile name for automatic tracking."""
    if profile is None:
        return "Without profile"

    return profile.get("profile_name", "Without profile")


def tracking_result(results):
    """Return the lowest-risk product and average risk."""
    if not results:
        return "", 0

    risks = [item["nutrition"].calculate_food_risk_score() for item in results]
    best = min(results, key=lambda item: item["nutrition"].calculate_food_risk_score())
    return best["product"].product_name, round(sum(risks) / len(risks), 2)


def load_all_food_data():
    """Load all required CSV data and create the nutrition analyzer."""
    data_manager = DataManager()
    missing = data_manager.check_data_files()

    if missing:
        print("\nMissing data files:")

        # List every missing file so the user knows what must be restored.
        for file_name in missing:
            print(f"- {file_name}")

        return data_manager, None

    data = data_manager.load_all_data()
    analyzer = NutritionAnalyzer(
        data["products"],
        data["nutrition"],
        data["product_countries"],
        data["country_regions"],
        data["country_trends"],
        data["region_trends"]
    )
    print("\nFood dataset loaded.")
    print(f"Products: {len(data['products'])}")
    print(f"Products with nutrition: {analyzer.count_combined_products()}")
    return data_manager, analyzer


def show_product_details(item, number=None):
    """Print the main product and nutrition details for one result."""
    product = item["product"]
    nutrition = item["nutrition"]
    heading = f"{number}. " if number is not None else ""
    print(f"{heading}{product.product_name}")
    print(f"   Code: {product.code} | Brand: {product.brands}")
    print(
        f"   Calories: {show_value(nutrition.energy_kcal_100g, ' kcal')} | "
        f"Sugar: {show_value(nutrition.sugars_100g, 'g')} | "
        f"Salt: {show_value(nutrition.salt_100g, 'g')}"
    )
    print(f"   Risk: {nutrition.calculate_food_risk_score()} | {nutrition.get_food_risk_level()}")
    print(f"   Countries: {', '.join(item['countries'])}")


def show_product_results(results):
    """Print all product results in a numbered list."""
    if not results:
        print("\nNo products found.")
        return

    print(f"\nProducts found: {len(results)}")

    for number, item in enumerate(results, start=1):
        show_product_details(item, number)


def choose_product_from_results(analyzer, prompt, excluded_code=None):
    """Search, show matches, and return one chosen product."""
    while True:
        search_text = ask_text(prompt, "0")

        if search_text == "0":
            return None

        results = analyzer.search_products(search_text, 10)

        if excluded_code:
            results = [item for item in results if item["product"].code != excluded_code]

        if not results:
            print("No products found. Try again or type 0 to cancel.")
            continue

        show_product_results(results)
        choices = [str(number) for number in range(len(results) + 1)]
        choice = ask_choice("Choose product number (0 to search again): ", choices)

        if choice == "0":
            continue

        selected = results[int(choice) - 1]
        selected["search_text"] = search_text
        return selected


def search_and_show_products(data_manager, analyzer, profile):
    """Search for products, display them, and save one tracking row."""
    search_text = ask_text("Enter product name, brand, or category: ")
    limit = ask_number("How many results: ", 10, int, 1, 50)
    results = analyzer.search_products(search_text, limit)
    show_product_results(results)

    best_product, average_risk = tracking_result(results)
    first_product = results[0]["product"].product_name if results else ""
    data_manager.save_tracking_row(
        "normal search",
        selected_profile_name(profile),
        search_text,
        first_product,
        "",
        len(results),
        best_product,
        average_risk
    )


def compare_two_products(data_manager, analyzer, profile):
    """Let the user choose two products and recommend the lower-risk one."""
    first = choose_product_from_results(analyzer, "Enter first product: ")

    if first is None:
        return

    second = choose_product_from_results(
        analyzer,
        "Enter second product: ",
        first["product"].code
    )

    if second is None:
        return

    # The recommendation is based on the same risk score shown to the user.
    first_risk = first["nutrition"].calculate_food_risk_score()
    second_risk = second["nutrition"].calculate_food_risk_score()
    best = first if first_risk <= second_risk else second

    print("\nPRODUCT COMPARISON")
    show_product_details(first)
    print()
    show_product_details(second)

    if first_risk == second_risk:
        print("\nResult: Both products have the same risk score.")
    else:
        print(f"\nResult: {best['product'].product_name} has the lower risk score.")

    data_manager.save_tracking_row(
        "comparison",
        selected_profile_name(profile),
        f"{first['search_text']} / {second['search_text']}",
        first["product"].product_name,
        second["product"].product_name,
        2,
        best["product"].product_name,
        round((first_risk + second_risk) / 2, 2)
    )


def check_one_product_warnings(data_manager, analyzer, profile):
    """Show nutrition warnings for one selected product and track the check."""
    selected = choose_product_from_results(analyzer, "Enter product name, brand, or category: ")

    if selected is None:
        return

    nutrition = selected["nutrition"]
    print("\nNUTRITION WARNING")
    show_product_details(selected)
    print("\nNutrition notes:")

    for note in nutrition.get_health_warnings():
        print(f"- {note}")

    risk = nutrition.calculate_food_risk_score()
    data_manager.save_tracking_row(
        "warning check",
        selected_profile_name(profile),
        selected["search_text"],
        selected["product"].product_name,
        "",
        1,
        selected["product"].product_name,
        risk
    )


def show_top_nutrition_products(analyzer):
    """Show products with the highest value for a chosen nutrition field."""
    options = {
        "1": ("Calories", "energy_kcal_100g"),
        "2": ("Sugar", "sugars_100g"),
        "3": ("Salt", "salt_100g"),
        "4": ("Fat", "fat_100g"),
        "5": ("Protein", "proteins_100g")
    }
    print("\n1. Calories\n2. Sugar\n3. Salt\n4. Fat\n5. Protein")
    choice = ask_choice("Type a number: ", list(options))
    limit = ask_number("How many results: ", 10, int, 1, 50)
    label, field_name = options[choice]
    results = analyzer.sort_products_by_nutrition(field_name, limit)

    print(f"\nTop products by {label}:")

    for item in results:
        print(f"{item['product'].product_name} | {label}: {round(item['value'], 2)}")


def show_trends(analyzer, trend_type):
    """Show yearly country or region nutrition trends as console text."""
    if trend_type == "country":
        name = ask_text("Enter country name: ")
        rows = analyzer.get_country_report(name)
        title = f"Country trends: {name}"
    else:
        name = ask_text("Enter region name: ")
        rows = analyzer.get_region_report(name)
        title = f"Region trends: {name}"

    print("\n" + analyzer.format_trend_report(title, rows))


def ask_yes_no(prompt):
    """Keep asking until the user enters yes or no."""
    while True:
        answer = ask_text(prompt, "no").lower()

        if answer in ["yes", "y"]:
            return True
        if answer in ["no", "n", ""]:
            return False

        print("Please type yes or no.")


def ask_date():
    """Read a profile start date or use today's date."""
    prompt = "Enter profile start date (YYYY-MM-DD), or press Enter for today: "
    date_text = ask_text(prompt)

    if not date_text:
        return datetime.now().date()

    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date. Using today's date.")
        return datetime.now().date()


def create_profile(data_manager):
    """Ask for user preferences and save them as a profile."""
    profile = {
        "profile_name": ask_text("Enter profile name: ") or "Default profile",
        "country": ask_text("Enter country, or leave blank: "),
        "region": ask_text("Enter region, or leave blank: "),
        "start_date": ask_date(),
        "max_sugar": ask_number("Maximum sugar per 100g: ", 22.5),
        "include_ultra_processed": ask_yes_no("Include ultra-processed products? (yes/no): "),
        "result_limit": ask_number("How many results: ", 10, int, 1, 50)
    }

    if data_manager.save_profile(profile):
        print("Profile saved.")
        return profile

    return None


def select_profile(data_manager):
    """Display saved profiles and return the profile chosen by the user."""
    profiles = data_manager.read_profiles()

    if not profiles:
        print("No saved profiles.")
        return None

    print("\nSaved profiles:")

    for number, profile in enumerate(profiles, start=1):
        print(f"{number}. {profile['profile_name']}")

    choices = [str(number) for number in range(len(profiles) + 1)]
    choice = ask_choice("Choose profile number (0 to cancel): ", choices)
    return None if choice == "0" else profiles[int(choice) - 1]


def create_or_select_profile(data_manager):
    """Open the small profile menu and create or select a profile."""
    print("\n1. Create profile\n2. Select profile\n0. Cancel")
    choice = ask_choice("Type a number: ", ["0", "1", "2"])

    if choice == "1":
        return create_profile(data_manager)
    if choice == "2":
        return select_profile(data_manager)

    return None


def search_with_selected_profile(data_manager, analyzer, profile):
    """Search for products that match the selected user profile."""
    if profile is None:
        print("Please create or select a profile first.")
        return

    search_text = ask_text("Enter product name, brand, or category: ")
    results = analyzer.find_products_for_profile(search_text, profile)
    show_product_results(results)
    best_product, average_risk = tracking_result(results)

    data_manager.save_tracking_row(
        "profile search",
        selected_profile_name(profile),
        search_text,
        best_product,
        "",
        len(results),
        best_product,
        average_risk
    )


def make_tracking_graphs(history, check_counts):
    """Create the check-type and risk-score tracking graph files."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    check_types = ["normal search", "comparison", "warning check", "profile search"]
    CHECK_TYPE_CHART_FILE.parent.mkdir(exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.bar(check_types, [check_counts[name] for name in check_types])
    plt.title("Checks used by the user")
    plt.ylabel("Number of saved checks")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(CHECK_TYPE_CHART_FILE)
    plt.close()

    # Keep matched timestamp/risk pairs so one damaged CSV row cannot stop a graph.
    dates = []
    risk_scores = []

    for row in history:
        try:
            saved_date = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            risk_score = float(row["average_risk_score"])
        except (ValueError, TypeError):
            continue

        dates.append(saved_date)
        risk_scores.append(risk_score)

    plt.figure(figsize=(8, 5))
    plt.plot(dates, risk_scores, marker="o")
    plt.title("Average risk score over time")
    plt.xlabel("Date")
    plt.ylabel("Average risk score")
    axis = plt.gca()
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M:%S"))
    if dates and min(dates) == max(dates):
        axis.set_xlim(dates[0] - timedelta(minutes=1), dates[0] + timedelta(minutes=1))
    plt.xticks(rotation=25)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(RISK_SCORE_CHART_FILE)
    plt.close()
    return True


def show_tracking_over_time(data_manager):
    """Print tracking summaries and create the two tracking graphs."""
    history = data_manager.read_tracking_history()

    if not history:
        print("\nNo tracking history yet. Use search, comparison, warning check, or profile search first.")
        return

    check_types = ["normal search", "comparison", "warning check", "profile search"]
    profile_counts = defaultdict(Counter)
    check_counts = Counter()
    profile_risks = defaultdict(list)

    # Build totals by profile and collect risk values for profile averages.
    for row in history:
        profile = row.get("profile_name") or "Without profile"
        check_type = row.get("check_type", "")
        profile_counts[profile][check_type] += 1
        check_counts[check_type] += 1

        try:
            profile_risks[profile].append(float(row["average_risk_score"]))
        except (ValueError, TypeError):
            pass

    print("\nCHECK TYPE TRACKER")
    print(f"{'Profile':<20}{'Normal search':>15}{'Comparison':>13}{'Warning check':>15}{'Profile search':>16}{'Total':>8}")

    # Nested loop: each profile is compared with every tracked check type.
    for profile, counts in profile_counts.items():
        values = []

        for check_type in check_types:
            values.append(counts[check_type])

        print(
            f"{profile:<20}{values[0]:>15}{values[1]:>13}"
            f"{values[2]:>15}{values[3]:>16}{sum(values):>8}"
        )

    print()

    for check_type in check_types:
        count = check_counts[check_type]
        print(f"{check_type:<15} | {'#' * count} {count}")

    print("\nRISK SCORE TRACKER")
    print("Saved checks by date")
    print("Each row is one saved check. The date shows when it happened.")
    print(f"{'No.':<5}{'Date and time':<20}{'Profile':<20}{'Check type':<17}{'Average risk':>13}")

    for number, row in enumerate(history[-10:], start=1):
        print(
            f"{number:<5}{row.get('timestamp', '')[:16]:<20}"
            f"{row.get('profile_name', ''):<20}{row.get('check_type', ''):<17}"
            f"{row.get('average_risk_score', ''):>13}"
        )

    print(f"\n{'Profile':<20}{'Average risk score':>20}")

    for profile, risks in profile_risks.items():
        average = round(sum(risks) / len(risks), 2) if risks else 0
        print(f"{profile:<20}{average:>20}")

    start_dates = {
        profile["profile_name"]: profile.get("start_date", "")
        for profile in data_manager.read_profiles()
    }
    print("\nProfile start dates:")

    for profile in profile_counts:
        print(f"{profile:<20}{start_dates.get(profile) or '-'}")

    if make_tracking_graphs(history, check_counts):
        print("\nEach point in the risk graph is one saved check. The date shows when it happened.")
        print("\nGraphs saved:")
        print("reports/check_type_tracking_bar_chart.png")
        print("reports/risk_score_tracking_line_chart.png")
    else:
        print("\nMatplotlib is not installed. Tracking tables are still available.")


def main():
    """Run the console menu until the user chooses Exit."""
    data_manager = DataManager()
    analyzer = None
    selected_profile = None

    while True:
        show_menu()
        choice = ask_menu_choice()

        # A final safety net keeps unexpected bad input from ending the program.
        try:
            if choice == 0:
                print("\nGoodbye!")
                break
            if choice == 1:
                data_manager, analyzer = load_all_food_data()
            elif choice == 10:
                show_tracking_over_time(data_manager)
            elif not data_is_loaded(analyzer):
                continue
            elif choice == 2:
                search_and_show_products(data_manager, analyzer, selected_profile)
            elif choice == 3:
                compare_two_products(data_manager, analyzer, selected_profile)
            elif choice == 4:
                check_one_product_warnings(data_manager, analyzer, selected_profile)
            elif choice == 5:
                show_top_nutrition_products(analyzer)
            elif choice == 6:
                show_trends(analyzer, "country")
            elif choice == 7:
                show_trends(analyzer, "region")
            elif choice == 8:
                profile = create_or_select_profile(data_manager)

                if profile is not None:
                    selected_profile = profile
            elif choice == 9:
                search_with_selected_profile(data_manager, analyzer, selected_profile)
        except Exception:
            print("\nSomething went wrong. Please try again.")


if __name__ == "__main__":
    main()
