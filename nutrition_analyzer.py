class NutritionAnalyzer:

    def __init__(self, products, nutrition_profiles, product_countries, country_regions, country_trends, region_trends,):
        self.products = products
        self.nutrition_profiles = nutrition_profiles
        self.product_countries = product_countries
        self.country_regions = country_regions
        self.country_trends = country_trends
        self.region_trends = region_trends
        self.product_lookup = {}
        self.nutrition_lookup = {}
        self.country_lookup = {}
        self.region_lookup = {}
        self.create_lookups()
    
    def create_lookups(self):
        for product in self.products:
            self.product_lookup[product.code] = product

        for nutrition in self.nutrition_profiles:
            self.nutrition_lookup[nutrition.code] = nutrition   

        for row in self.product_countries:
            code = row["code"]
            country = row["country"]

            if code not in self.country_lookup:
                self.country_lookup[code] = []

            if country not in self.country_lookup[code]:
                self.country_lookup[code].append(country)

        for row in self.country_regions:
            country = row["country"]
            region = row["region"]
            self.region_lookup[country] = region

    def get_product_by_code(self, code):
        code = str(code).strip()

        if code in self.product_lookup:
            return self.product_lookup[code]

        return None

    def get_nutrition_by_code(self, code):
        code = str(code).strip()

        if code in self.nutrition_lookup:
            return self.nutrition_lookup[code]

        return None

    def get_countries_for_product(self, code):
        code = str(code).strip()

        if code in self.country_lookup:
            return self.country_lookup[code]
        
        return []

    def get_combined_product_info(self, code):
        product = self.get_product_by_code(code)
        nutrition = self.get_nutrition_by_code(code)
        countries = self.get_countries_for_product(code)

        if product is None or nutrition is None:
            return None

        return {"product": product, "nutrition": nutrition, "countries": countries}

    def count_combined_products(self):
        count = 0

        for product in self.products:
            if product.code in self.nutrition_lookup:
                count = count + 1

        return count
    
    def search_products(self, search_text, limit=10):
        search_text = str(search_text).strip()

        results = []

        if search_text == "":
            return results

        for product in self.products:
            if product.matches_search(search_text):
                combined_info = self.get_combined_product_info(product.code)

                if combined_info is not None:
                    results.append(combined_info)

                if len(results) >= limit:
                    break

        return results

    def compare_products(self, first_code, second_code):
        first_product_info = self.get_combined_product_info(first_code)
        second_product_info = self.get_combined_product_info(second_code)

        if first_product_info is None or second_product_info is None:
            return None

        return {"first": first_product_info, "second": second_product_info}

    def get_health_warning_report(self, code):
        combined_info = self.get_combined_product_info(code)

        if combined_info is None:
            return None

        product = combined_info["product"]
        nutrition = combined_info["nutrition"]
        countries = combined_info["countries"]
        warnings = nutrition.get_health_warnings()
        
        report_lines = []

        report_lines.append("HEALTH WARNING REPORT")
        report_lines.append("=" * 40)
        report_lines.append(product.display_product())
        report_lines.append(nutrition.display_nutrition())
        report_lines.append(f"Countries: {', '.join(countries)}")
        report_lines.append("")
        report_lines.append("Warnings:")

        for warning in warnings:
            report_lines.append(f"- {warning}")

        return "\n".join(report_lines)

    def is_valid_nutrition_value(self, field_name, value):
        if value is None:
            return False

        valid_ranges = {
            "energy_kcal_100g": (0, 900),
            "sugars_100g": (0, 100),
            "fat_100g": (0, 100),
            "salt_100g": (0, 100),
            "proteins_100g": (0, 100),
            "nutriscore_score": (-15, 40),
            "nova_group": (1, 4),
        }

        if field_name not in valid_ranges:
            return False

        minimum_value, maximum_value = valid_ranges[field_name]

        return minimum_value <= value <= maximum_value    

    def sort_products_by_nutrition(self, field_name, limit=10):
        combined_results = []

        allowed_fields = [
            "energy_kcal_100g", "sugars_100g", "fat_100g", "salt_100g", "proteins_100g", "nutriscore_score", "nova_group"]

        if field_name not in allowed_fields:
            return combined_results

        for product in self.products:
            nutrition = self.get_nutrition_by_code(product.code)

            if nutrition is None:
                continue

            value = getattr(nutrition, field_name)

            if self.is_valid_nutrition_value(field_name, value):
                combined_results.append({
                    "product": product,
                    "nutrition": nutrition,
                    "value": value,
                    "countries": self.get_countries_for_product(product.code)
                })

        combined_results.sort(key=lambda item: item["value"], reverse=True)

        return combined_results[:limit]

    def get_country_report(self, country_name):
        country_name = str(country_name).strip().lower()
        results = []

        if country_name == "":
            return results

        for row in self.country_trends:
            row_country = row.get("country", "").strip().lower()

            if row_country == country_name:
                results.append(row)

        return results

    def get_region_report(self, region_name):
        region_name = str(region_name).strip().lower()
        results = []

        if region_name == "":
            return results

        for row in self.region_trends:
            row_region = row.get("region", "").strip().lower()

            if row_region == region_name:
                results.append(row)

        return results
    
    def format_trend_report(self, title, rows):
        if len(rows) == 0:
            return "No trend data found."

        report_lines = []

        report_lines.append(title)
        report_lines.append("=" * len(title))

        for row in rows:
            report_lines.append(                
                f"{row.get('year')} | Products: {row.get('product_count')} | "
                f"Avg kcal: {row.get('avg_kcal_100g')} | "
                f"Avg sugar: {row.get('avg_sugars_100g')}g | "
                f"Avg salt: {row.get('avg_salt_100g')}g | "
                f"Ultra-processed: {row.get('ultra_processed_percentage')}%")
        
        return "\n".join(report_lines)

    def generate_full_report(self):
        report_lines = []

        report_lines.append("SMART FOOD NUTRITION ANALYZER REPORT")
        report_lines.append("=" * 45)
        report_lines.append(f"Total products loaded: {len(self.products)}")
        report_lines.append(f"Total nutrition profiles loaded: {len(self.nutrition_profiles)}")
        report_lines.append("")

        sections = [("sugars_100g", "Top High-Sugar Products", "Sugar", "g"), ("energy_kcal_100g", "Top High-Calorie Products", "Calories", " kcal"), ("salt_100g", "Top High-Salt Products", "Salt", "g"), ("proteins_100g", "Top High-Protein Products", "Protein", "g")]

        for field_name, title, label, unit in sections:
            report_lines.append(title)
            report_lines.append("=" * len(title))

            results = self.sort_products_by_nutrition(field_name, limit=5)

            for item in results:
                product = item["product"]
                value = item["value"]
                countries = item["countries"]
                report_lines.append(f"{product.product_name} | {label}: {round(value, 2)}{unit} | Countries: {', '.join(countries)}")

            report_lines.append("")

        selected_countries = ["Austria", "Sri Lanka"]

        for country in selected_countries:
            rows = self.get_country_report(country)
            recent_rows = rows[-5:]
            report_lines.append(self.format_trend_report(f"Country Trend: {country}", recent_rows))
            report_lines.append("")

        regions = []

        for row in self.region_trends:
            region = row.get("region", "")

            if region != "" and region not in regions:
                regions.append(region)

        regions.sort()

        for region in regions:
            rows = self.get_region_report(region)
            recent_rows = rows[-5:]
            report_lines.append(self.format_trend_report(f"Region Trend: {region}", recent_rows))
            report_lines.append("")

        report_lines.append("Note:")
        report_lines.append("The data comes from Open Food Facts. Because the source is crowdsourced, some values may contain outliers or entry mistakes.")

        return "\n".join(report_lines)