class BaseRecord:
    """Provide the shared product code used to connect project datasets."""
    
    def __init__(self, code):
        """Store a cleaned product code."""
        self.code = str(code).strip()
