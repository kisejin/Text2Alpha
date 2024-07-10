import dspy

class FinanceStrategyGenerator(dspy.Signature):
    question = dspy.InputField(desc="Query of the finance strategy.")
    # answer = dspy.OutputField(desc="The ```python``` code block.")
    answer = dspy.OutputField(desc="The ```python``` code block. Answer appears along with the reasoning.")