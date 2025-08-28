# Benchmark Runner & Result Analyzer

A simple Python toolkit for testing language models and analyzing their performance across different temperature settings and question domains.

## Quick Start

### 1. Run Benchmark Tests

Test a single model with specific settings:

```bash
python3 run_benchmark.py --model_name "gemma3:270m" --temperature 0.1
```

Run multiple tests for comparison:

```bash
python3 run_benchmark.py --model_name "gemma3:270m" --temperature 0.1
python3 run_benchmark.py --model_name "gemma3:270m" --temperature 0.8
python3 run_benchmark.py --model_name "qwen-instruct" --temperature 0.1
python3 run_benchmark.py --model_name "qwen-instruct" --temperature 0.8
```

### 2. Analyze Results

Generate plots and summary:

```bash
python3 analyze_results.py
```

## Requirements

- Python 3.x
- Local LLM server (e.g., Ollama) running on `localhost:11434`
- For analysis: `pip install pandas matplotlib seaborn`

## Files

- `run_benchmark.py` - Main benchmark runner
- `analyze_results.py` - Results analysis and plotting
- `items.jsonl` - Question dataset
- `results/` - Output folder containing:
  - `results.csv` - Generated results (auto-created)
  - `plot_*.png` - Generated analysis plots

## Command Options

### run_benchmark.py
- `--model_name` - Model to test (required)
- `--temperature` - Temperature setting (required)  
- `--output_file` - CSV output file (default: results.csv)

### analyze_results.py
No arguments needed. Reads `results/results.csv` and generates plots in `results/`:
- `plot_overall_accuracy.png`
- `plot_temperature_comparison.png`
- `plot_domain_performance.png`

## Example Output

```
--- Stata Benchmark Runner ---
Model: gemma3:270m
Temperature: 0.1
Output file: results/results.csv

(1/12) Running Task: LANG-001-MULTI...
  > Result: Correct (Model chose index 1.)
...
--- Benchmark Complete ---
Score: 8 / 12
Accuracy: 66.67%
```