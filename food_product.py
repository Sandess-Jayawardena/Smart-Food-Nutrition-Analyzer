from base_record import BaseRecord

class FoodProduct(BaseRecord):
    """Store searchable product details linked by a shared product code."""

    def __init__(self, code, product_name, brands, main_category):
        """Create one food product record."""
        super().__init__(code)
        self.product_name = product_name or ""
        self.brands = brands or ""
        self.main_category = main_category or ""
        
    def matches_search(self, search_text):
        """Check whether the product matches search text."""
        search_text = search_text.lower()

        # A match in any of the three user-visible text fields is accepted.
        return (
            search_text in self.product_name.lower()
            or search_text in self.brands.lower()
            or search_text in self.main_category.lower()
        )
