# Benchmark Runner & Result Analyzer

A simple Python toolkit for testing language models and analyzing their performance across different temperature settings and question domains.

## Quick Start

### 1. Setup API Keys (Optional)

For external API models, copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run Benchmark Tests

Test local models (Ollama):
```bash
python3 run_benchmark.py --model_name "gemma3:270m" --temperature 0.1
```

Test API models (auto-detected):
```bash
python3 run_benchmark.py --model_name "gpt-4" --temperature 0.1
python3 run_benchmark.py --model_name "deepseek-chat" --temperature 0.1
```

Specify API provider explicitly:
```bash
python3 run_benchmark.py --model_name "custom-model" --temperature 0.1 --api_provider openai
```

### 3. Analyze Results

Generate plots and summary:

```bash
python3 analyze_results.py
```

## Requirements

- Python 3.x
- For local models: LLM server (e.g., Ollama) running on `localhost:11434`
- For API models: Valid API keys in `.env` file
- Python packages: `pip install -r requirements.txt`

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
- `--api_provider` - API provider (openai, deepseek, anthropic) - auto-detected if not specified

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