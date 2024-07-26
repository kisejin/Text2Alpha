import sys
import os

# Dynamically find the current file's directory
current_file_path = os.path.realpath(__file__)


parent_dir_utils = '/'.join(current_file_path.split('/')[0:-2])
# Construct the path to the 'utils' directory
utils_path = os.path.join(os.path.dirname(parent_dir_utils), 'utils')
# Add the 'utils' directory to the system path
sys.path.append(utils_path)


import dspy
from dspy_signature import FinanceStrategyGenerator
from prompt_template import prompt_error_template
from backtrader_cerebro import CelebroCreator
from file_text_handler import get_code_from_text
from errors_handler.clean_error_message import get_error
from prompt_template.base_strategy_improved import BaseStrategy
from prompt_template.prompt_description import instruction


import pandas as pd
import re
from dspy_signature import FinanceStrategyGenerator

import backtrader as bt

FinanceStrategyGenerator.__doc__= instruction
    

# Instrinsic Metric
def check_valid_code(strategy, list_data):

    obj = CelebroCreator(strategy, list_data)
    count = {}

    if obj.strats is not None:
        count["BuySignal"] = obj.strats[0].cbuy
        count["SellSignal"] = obj.strats[0].csell

    message = obj.message
    errors = get_error(message) if message else ["", ""]

    return errors, count


def check_valid_indicators(**kwargs):
    if kwargs["countBuy"] >= 2 or kwargs["countSell"] >= 2:
        return True
    return False


class GenerateCodeWithAssert(dspy.Module):
    def __init__(self, list_ohcl_data, max_retry):
        super().__init__()
        self.generate_result = dspy.ChainOfThought(FinanceStrategyGenerator)
        self.ohcl_data = list_ohcl_data
        self.num_retry = 0
        self.flag = 0
        self.complete = False
        self.still_errors = False
        self.max_retry = max_retry
        self.max_retry_error = 0

    def forward(self, question):

        ex = self.generate_result(question=question)
        print("Answer: \n", get_code_from_text(ex.answer))

        if self.flag == 0:
            self.flag = 1
        else:
            self.num_retry += 1

        # Get and execute code
        exec(get_code_from_text(ex.answer), globals())

        # Extract Error
        # #CURRENT -----------
        errors, count = check_valid_code(BackTestStrategy, self.ohcl_data)
        # -------------------
        check = True if errors[0] == "" else False

        # Concate 2 error
        if not check:
            p_error = (
                prompt_error_template(
                    errors=errors, include_my_code_error=False
                )
                if errors[-1] == ""
                else prompt_error_template(
                    errors=errors, include_my_code_error=True
                )
            )
        else:
            p_error = ""

        # Assertion 1: Check if code has error
        dspy.Suggest(check, f"{p_error}")

        self.max_retry_error = self.num_retry if check else self.max_retry

        # New
        check1 = False
        if count:
            check1 = check_valid_indicators(
                countBuy=count["BuySignal"], countSell=count["SellSignal"]
            )

            # Assertion 2: Check if less than 1 buy and 1 sell signal
            dspy.Suggest(
                check1,
                f"Please review and correct the formulas and conditions. Make sure the strategy includes at least one buy and one sell signal.",
            )
        # ---------

        ex["num_retry"] = self.num_retry

        self.complete = (
            True
            if ex["num_retry"] <= self.max_retry and check1 == True
            else False
        )
        self.still_errors = (
            True
            if ex["num_retry"] == self.max_retry and check == False
            else False
        )

        ex["Complete"] = self.complete
        ex["Still_Error"] = str(self.still_errors) + str(self.max_retry_error)

        #  Reset attribute values
        self.num_retry, self.flag = 0, 0
        self.still_errors, self.complete = False, False

        return ex
