from base_record import BaseRecord
from constants import HIGH_SUGAR_LIMIT, HIGH_FAT_LIMIT, HIGH_SALT_LIMIT, HIGH_CALORIE_LIMIT

class ProductNutrition(BaseRecord):
    """Store nutrition values and calculate warnings and risk information."""

    def __init__(self, code, energy_kcal_100g, sugars_100g, fat_100g, salt_100g, proteins_100g, nova_group):
        """Create one product nutrition record."""
        super().__init__(code)
        # CSV values arrive as strings, so numeric fields are converted to floats.
        self.energy_kcal_100g = self.to_float(energy_kcal_100g)
        self.sugars_100g = self.to_float(sugars_100g)
        self.fat_100g = self.to_float(fat_100g)
        self.salt_100g = self.to_float(salt_100g)
        self.proteins_100g = self.to_float(proteins_100g)
        self.nova_group = self.to_float(nova_group)

    def to_float(self, value):
        """Convert a CSV value to a float when possible."""
        try:
            if value == "":
                return None
            return float(value)
        except ValueError:
            return None

    # Warning checks compare nutrition values with the limits in constants.py.
    def is_high_sugar(self):
        """Return whether sugar is above the warning limit."""
        return self.sugars_100g is not None and self.sugars_100g > HIGH_SUGAR_LIMIT

    def is_high_fat(self):
        """Return whether fat is above the warning limit."""
        return self.fat_100g is not None and self.fat_100g > HIGH_FAT_LIMIT

    def is_high_salt(self):
        """Return whether salt is above the warning limit."""
        return self.salt_100g is not None and self.salt_100g > HIGH_SALT_LIMIT

    def is_high_calorie(self):
        """Return whether calories are above the warning limit."""
        return self.energy_kcal_100g is not None and self.energy_kcal_100g >= HIGH_CALORIE_LIMIT
    
    # NOVA group 4 means ultra-processed food.
    def is_ultra_processed(self):
        """Return whether the product is ultra-processed."""
        return self.nova_group == 4
    
    def calculate_food_risk_score(self):
        """Calculate a simple nutrition-based risk score."""
        score = 0

        # Less healthy nutrition values add points using per-100g thresholds.
        if self.energy_kcal_100g is not None:
            if self.energy_kcal_100g >= 400:
                score += 3
            elif self.energy_kcal_100g >= 250:
                score += 2
            elif self.energy_kcal_100g >= 100:
                score += 1

        if self.sugars_100g is not None:
            if self.sugars_100g > 22.5:
                score += 4
            elif self.sugars_100g > 5:
                score += 2

        if self.fat_100g is not None:
            if self.fat_100g > 17.5:
                score += 4
            elif self.fat_100g > 3:
                score += 2

        if self.salt_100g is not None:
            if self.salt_100g > 1.5:
                score += 4
            elif self.salt_100g > 0.3:
                score += 2

        if self.nova_group == 4:
            score += 4
        elif self.nova_group == 3:
            score += 2

        # Protein lowers the score slightly but cannot make it negative.
        if self.proteins_100g is not None:
            if self.proteins_100g >= 20:
                score -= 2
            elif self.proteins_100g >= 10:
                score -= 1

        return round(max(score, 0), 1)

    def get_food_risk_level(self):
        """Convert the risk score into a clear risk level."""
        score = self.calculate_food_risk_score()

        if score <= 4:
            return "Low risk"

        if score <= 8:
            return "Medium risk"

        if score <= 13:
            return "High risk"

        return "Very high risk"

    def get_health_warnings(self):
        """Return all health warnings for the nutrition values."""
        checks = [
            (self.is_high_sugar(), "High sugar"),
            (self.is_high_fat(), "High fat"),
            (self.is_high_salt(), "High salt"),
            (self.is_high_calorie(), "High calorie"),
            (self.is_ultra_processed(), "Ultra-processed")
        ]
        messages = [message for warning, message in checks if warning]

        if self.proteins_100g is not None and self.proteins_100g >= 20:
            messages.append("Positive note: high protein")

        return messages or ["No major nutrition warnings"]
