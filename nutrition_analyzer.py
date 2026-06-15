VALID_RANGES = {
    "energy_kcal_100g": (0, 900),
    "sugars_100g": (0, 100),
    "fat_100g": (0, 100),
    "salt_100g": (0, 100),
    "proteins_100g": (0, 100)
}

class NutritionAnalyzer:
    """Search, compare, filter, warn, and report loaded nutrition data."""

    def __init__(self, products, nutrition_profiles, product_countries, country_regions, country_trends, region_trends):
        """Store loaded data and prepare lookup dictionaries."""
        self.products = products
        self.nutrition_profiles = nutrition_profiles
        self.country_trends = country_trends
        self.region_trends = region_trends
        # Lookup dictionaries avoid scanning every dataset for each menu action.
        self.product_lookup = {product.code: product for product in self.products}
        self.nutrition_lookup = {nutrition.code: nutrition for nutrition in self.nutrition_profiles}
        self.region_lookup = {row["country"]: row["region"] for row in country_regions}
        self.country_lookup = {}

        # One product can appear in several countries, so each code stores a list.
        for row in product_countries:
            code = row["code"]
            country = row["country"]

            if code not in self.country_lookup:
                self.country_lookup[code] = []

            if country not in self.country_lookup[code]:
                self.country_lookup[code].append(country)

    def get_full_product_details(self, code):
        """Combine product, nutrition, and country information."""
        code = str(code).strip()
        product = self.product_lookup.get(code)
        nutrition = self.nutrition_lookup.get(code)

        if product is None or nutrition is None:
            return None

        return {"product": product, "nutrition": nutrition, "countries": self.country_lookup.get(code, [])}

    def count_combined_products(self):
        """Count products that also have nutrition information."""
        return sum(1 for product in self.products if product.code in self.nutrition_lookup)
    
    def search_products(self, search_text, limit=10):
        """Search products and return combined matching records."""
        search_text = str(search_text).strip()

        results = []

        if search_text == "":
            return results

        for product in self.products:
            if product.matches_search(search_text):
                combined_info = self.get_full_product_details(product.code)

                if combined_info is not None:
                    results.append(combined_info)

                if len(results) >= limit:
                    break

        return results

    def get_profile_number(self, profile, field_name, default_value, number_type):
        """Read a numeric profile setting with a safe default."""
        try:
            return number_type(profile.get(field_name, default_value))
        except (ValueError, TypeError):
            return default_value

    def matches_profile_location(self, countries, country_filter, region_filter):
        """Check whether product countries match profile location settings."""
        normalized_countries = [country.strip().lower() for country in countries]

        if country_filter and country_filter not in normalized_countries:
            return False

        if region_filter:
            regions = [self.region_lookup.get(country, "").strip().lower() for country in countries]

            if region_filter not in regions:
                return False

        return True

    def find_products_for_profile(self, search_text, profile):
        """Find products that match a saved user nutrition profile."""
        if not isinstance(profile, dict):
            profile = {}

        max_sugar = self.get_profile_number(profile, "max_sugar", 100, float)
        result_limit = self.get_profile_number(profile, "result_limit", 10, int)
        result_limit = result_limit if result_limit > 0 else 10
        country_filter = str(profile.get("country", "") or "").strip().lower()
        region_filter = str(profile.get("region", "") or "").strip().lower()
        include_ultra_processed = bool(profile.get("include_ultra_processed", False))
        filtered_results = []

        # Apply every profile rule before sorting the remaining products by risk.
        for item in self.search_products(search_text, len(self.products)):
            nutrition = item["nutrition"]

            if not self.matches_profile_location(item["countries"], country_filter, region_filter):
                continue
            if nutrition.sugars_100g is None or nutrition.sugars_100g > max_sugar:
                continue
            if not include_ultra_processed and nutrition.is_ultra_processed():
                continue

            filtered_results.append(item)

        return sorted(filtered_results, key=lambda item: item["nutrition"].calculate_food_risk_score())[:result_limit]

    def format_trend_row(self, row):
        """Format one country or region trend row."""
        return (
            f"{row.get('year')} | Products: {row.get('product_count')} | "
            f"Avg kcal: {row.get('avg_kcal_100g')} | "
            f"Avg sugar: {row.get('avg_sugars_100g')}g | "
            f"Avg salt: {row.get('avg_salt_100g')}g | "
            f"Ultra-processed: {row.get('ultra_processed_percentage')}%"
        )

    def is_valid_nutrition_value(self, field_name, value):
        """Check whether a nutrition value is within a realistic range."""
        return value is not None and field_name in VALID_RANGES and VALID_RANGES[field_name][0] <= value <= VALID_RANGES[field_name][1]

    def sort_products_by_nutrition(self, field_name, limit=10):
        """Return products sorted by one nutrition field."""
        combined_results = []
        if field_name not in VALID_RANGES:
            return combined_results

        # Missing and unrealistic values are left out of the ranking.
        for product in self.products:
            nutrition = self.nutrition_lookup.get(product.code)

            if nutrition is None:
                continue

            value = getattr(nutrition, field_name)

            if self.is_valid_nutrition_value(field_name, value):
                combined_results.append({
                    "product": product,
                    "nutrition": nutrition,
                    "value": value,
                    "countries": self.country_lookup.get(product.code, [])
                })

        return sorted(combined_results, key=lambda item: item["value"], reverse=True)[:limit]

    def filter_trend_rows(self, rows, field_name, name):
        """Filter trend rows by country or region name."""
        name = str(name).strip().lower()

        if name == "":
            return []

        return [row for row in rows if row.get(field_name, "").strip().lower() == name]

    def get_country_report(self, country_name):
        """Return trend rows for one country."""
        return self.filter_trend_rows(self.country_trends, "country", country_name)

    def get_region_report(self, region_name):
        """Return trend rows for one region."""
        return self.filter_trend_rows(self.region_trends, "region", region_name)

    def format_trend_report(self, title, rows):
        """Format country or region trend rows as text."""
        if len(rows) == 0:
            return "No trend data found."

        report_lines = [title, "=" * len(title)]
        report_lines.extend(self.format_trend_row(row) for row in rows)
        return "\n".join(report_lines)
