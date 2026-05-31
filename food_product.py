from base_record import BaseRecord

class FoodProduct(BaseRecord):

    def __init__(self, code, product_name, brands, main_category, created_year):
        super().__init__(code)
        self.product_name = product_name
        self.brands = brands
        self.main_category = main_category 
        self.created_year = self.to_int(created_year)

    def to_int(self, value):
        try:
            if value == "":
                return None
            return int(value)
        except ValueError:
            return None
        
    def matches_search(self, search_text):
        search_text = search_text.lower()

        return(search_text in self.product_name.lower() or search_text in self.brands.lower() or search_text in self.main_category.lower() )

    def display_product(self):
        return f"{self.code} | {self.product_name} | {self.brands} | {self.main_category} | {self.created_year}"
