from abc import ABC,abstractmethod
import pandas as pd


class BaseFile(ABC):
    def __init__(self,path:str):
        self.path =path

    @abstractmethod
    def read(self) -> pd.DataFrame:
        pass

