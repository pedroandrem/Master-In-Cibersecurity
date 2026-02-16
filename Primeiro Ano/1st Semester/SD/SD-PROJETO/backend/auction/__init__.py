__version__ = "2025.11.13"

C_END = '\033[0m'
C_GREEN = '\033[92m'
C_RED = '\033[91m'
C_YELLOW = '\033[93m'

try:
    from .item import Item
    print(C_GREEN + f"{__package__}: " + C_YELLOW + f"(version {__version__})" + C_END)
except ImportError as e:
    print(C_RED + f"Error importing baseCommand package: {e}" + C_END)