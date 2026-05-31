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
        