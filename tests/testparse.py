import sys
sys.path.insert(0, '..')
from src.basic_builtins import UsingFormatter

formatter = UsingFormatter("(###) ###-####")
print("Fields:", formatter.fields)
