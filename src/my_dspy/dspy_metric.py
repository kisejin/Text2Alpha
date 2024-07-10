def validate_answer(example, prediction, trace=None):
    print("Example", prediction)
    return prediction.num_retry <= 5 and (prediction.answer != "")
