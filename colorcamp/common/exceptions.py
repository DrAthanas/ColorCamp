"""Custom exceptions to help with specific error filtering"""


class NumericIntervalError(Exception):
    """Invalid interval error"""

    def __init__(self, message: str) -> None:
        """Initialize the exception"""
        super().__init__()
        self.message = message
