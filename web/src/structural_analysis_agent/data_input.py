from typing import List, Dict

class DataInput:
    def __init__(self):
        self.structural_data = []

    def load_data(self, data: List[Dict[str, float]]) -> None:
        """
        Load structural data for analysis.
        
        :param data: List of dictionaries containing structural data.
        """
        self.structural_data = data

    def get_data(self) -> List[Dict[str, float]]:
        """
        Retrieve the loaded structural data.
        
        :return: List of dictionaries containing structural data.
        """
        return self.structural_data