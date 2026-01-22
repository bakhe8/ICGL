from typing import Dict

class AnalysisOutput:
    def __init__(self, results: Dict[str, float]):
        self.results = results

    def display_results(self) -> None:
        """
        Display the analysis results.
        """
        print("Structural Analysis Results:")
        for key, value in self.results.items():
            print(f"{key}: {value}")