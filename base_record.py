class BaseRecord:
    # Parent class for records that share a product code.
    
    def __init__(self, code):
        self.code = str(code).strip()

    def get_code(self):
        return self.code
