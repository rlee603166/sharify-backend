from enum import Enum

class SplitMethod(str, Enum):
    EQUAL = "equal"
    ITEMIZED = "itemized"