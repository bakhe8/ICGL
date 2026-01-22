from data_input import DataInput
from analysis import StructuralAnalysis
from output import AnalysisOutput

def main():
    # Example structural data
    data = [
        {"force": 100.0, "area": 10.0},
        {"force": 200.0, "area": 20.0},
    ]

    # Load data
    data_input = DataInput()
    data_input.load_data(data)

    # Perform analysis
    analysis = StructuralAnalysis(data_input.get_data())
    results = analysis.perform_analysis()

    # Output results
    output = AnalysisOutput(results)
    output.display_results()

if __name__ == "__main__":
    main()