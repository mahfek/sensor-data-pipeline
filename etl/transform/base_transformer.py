from abc import ABC,abstractmethod
import pandas as pd

class BaseTransformer(ABC):
    def __init__(self,data):
        self.data = data

    @abstractmethod
    def run_transformations(self) -> pd.DataFrame :
        pass