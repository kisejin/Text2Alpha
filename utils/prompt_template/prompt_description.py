import sys
import os

sys.path.insert(1, '/'.join(os.path.realpath(__file__).split('/')[0:-2]))

from file_text_handler import load_file

current_path = '/'.join(os.path.realpath(__file__).split('/')[0:-1])
base_strategy_PATH = current_path + "/base_strategy_improved.py"
backtrader_examples_PATH = current_path + "/backtrader_examples.py"
custom_examples_PATH = current_path + "/custom_examples.py"
base_strats = load_file(base_strategy_PATH)
backtrader_examples = load_file(backtrader_examples_PATH)
custom_examples = load_file(custom_examples_PATH)
list_indicators = load_file(current_path + "/indicators.txt")


instruction = f"""
You are a python developer that intent to make a workable trading strategy. Your task is to create a `BackTestStrategy` class that inherit from the `BaseStrategy` class given below and you MUST ONLY modify the `execute` function to follow human requirements.
Here is the `BaseStrategy` class : 
```python\n{base_strats}```

You are provided with list of indicators and description:
{list_indicators}
Here are two situations you need to handle :
- SITUATION 1 : The provided list of indicators CONTAIN the indicator that human required, so you just use it follow this example :
```python\n{backtrader_examples}```

- SITUATION 2 : The provided list of indicantors DO NOT CONTAIN the indicator that human required, so you try your best to create custom indicator follow this example :
```python\n{custom_examples}```
"""
