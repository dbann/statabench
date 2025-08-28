Spec Sheet: Iterative Benchmark Runner & Result Analyzer
1. Objective
To enhance the existing run_benchmark.py script to support automated, iterative testing of multiple language models at different temperature settings. A second script will be created to analyze and plot the results from the collected data.

The final product should be simple enough for a Python novice to use.

2. Required Modifications to run_benchmark.py
2a. Accept Command-Line Arguments
The script must be modified to accept parameters from the command line instead of using hard-coded configuration variables.

Remove: The hard-coded MODELS_TO_TEST list and the temperature value inside the get_llm_response function.

Implement argparse: Use Python's standard argparse library to accept the following arguments:

--model_name (string, required): The name of the model to test (e.g., "gemma3:270m").

--temperature (float, required): The temperature setting for the model (e.g., 0.1).

--output_file (string, optional, default: "results.csv"): The name of the file to save results to.

2b. Implement CSV Logging
The script must save the result of each individual question to a CSV file to create a persistent log for analysis.

File Handling:

If the output CSV file does not exist, create it and write a header row.

If the file already exists, append new results without writing a new header.

CSV Columns: Each row written to the CSV file must contain the following columns:

timestamp (The date and time the test was run)

model_name (From the command-line argument)

temperature (From the command-line argument)

task_id (From items.jsonl)

domain (From items.jsonl)

result (The string "Correct" or "Incorrect")

Logic: After each question is scored, a new row should be appended to the CSV file.

3. Create a New Analysis Script (analyze_results.py)
A new, separate Python script named analyze_results.py will be created to read the results.csv file and generate plots.

Dependencies: This script will require the pandas and matplotlib libraries.

Functionality: The script should:

Load results.csv into a pandas DataFrame.

Generate and save the following plots as PNG files:

plot_overall_accuracy.png: A bar chart showing the overall accuracy percentage for each model.

plot_temperature_comparison.png: A grouped bar chart comparing the accuracy of each model at different temperatures.

plot_domain_performance.png: A bar chart or heatmap showing the accuracy of each model for each question domain.

Print a summary of the results to the console.

4. Example Workflow (for documentation)
A user should be able to perform the following steps:

Run multiple tests automatically (e.g., from a shell script):

python run_benchmark.py --model_name "gemma3:270m" --temperature 0.1
python run_benchmark.py --model_name "gemma3:270m" --temperature 0.8
python run_benchmark.py --model_name "qwen-instruct" --temperature 0.1
python run_benchmark.py --model_name "qwen-instruct" --temperature 0.8

Analyze the results:

python analyze_results.py

View the output: Check the console for a summary and find the generated PNG plot files in the directory.