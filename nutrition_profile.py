from base_record import BaseRecord
from constants import( HIGH_SUGAR_LIMIT, HIGH_FAT_LIMIT, HIGH_SALT_LIMIT,HIGH_CALORIE_LIMIT )

class NutritionProfile(BaseRecord):

    def __init__(self, code, energy_kcal_100g, sugars_100g, fat_100g, salt_100g, proteins_100g, nutriscore_grade, nutriscore_score, nova_group):
        super().__init__(code)
        # CSV values arrive as strings, so numeric fields are converted to floats.
        self.energy_kcal_100g = self.to_float(energy_kcal_100g)
        self.sugars_100g = self.to_float(sugars_100g)
        self.fat_100g = self.to_float(fat_100g)
        self.salt_100g = self.to_float(salt_100g)
        self.proteins_100g = self.to_float(proteins_100g)
        self.nutriscore_grade = nutriscore_grade
        self.nutriscore_score = self.to_float(nutriscore_score)
        self.nova_group = self.to_float(nova_group)

    def to_float(self, value):
        try:
            if value == "":
                return None
            return float(value)
        except ValueError:
            return None

    # Warning checks compare nutrition values with the limits in constants.py.
    def is_high_sugar(self):
        return self.sugars_100g is not None and self.sugars_100g > HIGH_SUGAR_LIMIT

    def is_high_fat(self):
        return self.fat_100g is not None and self.fat_100g > HIGH_FAT_LIMIT

    def is_high_salt(self):
        return self.salt_100g is not None and self.salt_100g > HIGH_SALT_LIMIT

    def is_high_calorie(self):
        return self.energy_kcal_100g is not None and self.energy_kcal_100g > HIGH_CALORIE_LIMIT
    
    # NOVA group 4 means ultra-processed food.
    def is_ultra_processed(self):
        return self.nova_group == 4

    def get_health_warnings(self):
        warnings = []

        if self.is_high_sugar():
            warnings.append("High sugar")
        
        if self.is_high_fat():
            warnings.append("High fat")

        if self.is_high_salt():
            warnings.append("High salt")

        if self.is_high_calorie():
            warnings.append("High calorie")

        if self.is_ultra_processed():
            warnings.append("Ultra processed")

        if len(warnings) == 0:
            warnings.append("No major warnings")

        return warnings
    
    def display_nutrition(self):
        return (f"{self.code} | {self.energy_kcal_100g} kcal | {self.sugars_100g}g sugar | {self.salt_100g}g salt | Nutri-Score {self.nutriscore_grade} | NOVA {self.nova_group}")
