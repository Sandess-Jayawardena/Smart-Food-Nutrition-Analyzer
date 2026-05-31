class BaseRecord:
    
    def __init__(self, code):
        self.code = str(code).strip()

    def get_code(self):
        return self.code