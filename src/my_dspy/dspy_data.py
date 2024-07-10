import dspy
import pandas as pd


class CSVDataset:
    def __init__(self, file_path) -> None:

        # Load the CSV file
        df = pd.read_csv(file_path)

        # Change name of the columns
        df.columns = ["question", "answer"]

        df = df.drop(columns=["answer"])

        # df = df.sample(frac=1).reset_index(drop=True)

        self.train = self._change_input(df.iloc[:30].to_dict(orient="records"))
        self.dev = self._change_input(df.iloc[30:].to_dict(orient="records"))

    def _change_input(self, input_data):

        ds = []
        for d in input_data:
            ds.append(
                dict(
                    question=d["question"],
                )
            )
        d = [dspy.Example(**x).with_inputs("question") for x in ds]
        return d
