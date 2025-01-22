from gridstatusio import GridStatusClient
import pandas as pd
import os

class GridStatusClientMock(GridStatusClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, 'test_data.csv')
        self.data = load_test_data(file_path)

    def get_dataset(self, *args, **kwargs):
        return self.data



def load_test_data(file_path):
    return pd.read_csv(file_path)

