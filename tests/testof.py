import sys
sys.path.insert(0, '..')
from src.basic_builtins import UsingFormatter

formatter = UsingFormatter("###-")
result = formatter.format_values([1234])
print(f"Result: '{result}'")
