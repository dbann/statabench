#!/usr/bin/env python3
"""
Analysis script for benchmark results.
Reads results.csv and generates plots showing model performance.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

def load_results(csv_file="results/results.csv"):
    """Load results from CSV file."""
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Run benchmark tests first.")
        return None
    
    try:
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} results from {csv_file}")
        return df
    except Exception as e:
        print(f"Error loading {csv_file}: {e}")
        return None

def plot_overall_accuracy(df, output_file="results/plot_overall_accuracy.png"):
    """Generate bar chart showing overall accuracy for each model."""
    plt.figure(figsize=(12, 6))
    
    # Calculate accuracy by model
    accuracy_by_model = df.groupby('model_name').apply(
        lambda x: (x['result'] == 'Correct').sum() / len(x) * 100
    ).sort_values(ascending=False)
    
    bars = plt.bar(range(len(accuracy_by_model)), accuracy_by_model.values)
    plt.xlabel('Model')
    plt.ylabel('Accuracy (%)')
    plt.title('Overall Model Accuracy')
    plt.xticks(range(len(accuracy_by_model)), accuracy_by_model.index, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved overall accuracy plot to {output_file}")

def plot_temperature_comparison(df, output_file="results/plot_temperature_comparison.png"):
    """Generate grouped bar chart comparing accuracy at different temperatures."""
    plt.figure(figsize=(14, 6))
    
    # Calculate accuracy by model and temperature
    accuracy_pivot = df.groupby(['model_name', 'temperature']).apply(
        lambda x: (x['result'] == 'Correct').sum() / len(x) * 100
    ).unstack(fill_value=0)
    
    ax = accuracy_pivot.plot(kind='bar', width=0.8)
    plt.xlabel('Model')
    plt.ylabel('Accuracy (%)')
    plt.title('Model Accuracy by Temperature Setting')
    plt.legend(title='Temperature', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', rotation=0, padding=3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved temperature comparison plot to {output_file}")

def plot_domain_performance(df, output_file="results/plot_domain_performance.png"):
    """Generate heatmap showing accuracy by model and domain."""
    plt.figure(figsize=(16, 8))
    
    # Calculate accuracy by model and domain
    domain_accuracy = df.groupby(['model_name', 'domain']).apply(
        lambda x: (x['result'] == 'Correct').sum() / len(x) * 100
    ).unstack(fill_value=0)
    
    # Create heatmap
    sns.heatmap(domain_accuracy, annot=True, fmt='.1f', cmap='RdYlGn', 
                cbar_kws={'label': 'Accuracy (%)'}, vmin=0, vmax=100)
    plt.title('Model Performance by Domain')
    plt.xlabel('Domain')
    plt.ylabel('Model')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved domain performance heatmap to {output_file}")

def print_summary(df):
    """Print a summary of the results to console."""
    print("\n" + "="*60)
    print("BENCHMARK RESULTS SUMMARY")
    print("="*60)
    
    # Overall statistics
    total_tests = len(df)
    unique_models = df['model_name'].nunique()
    unique_temps = df['temperature'].nunique()
    unique_domains = df['domain'].nunique()
    
    print(f"Total tests run: {total_tests}")
    print(f"Models tested: {unique_models}")
    print(f"Temperature settings: {unique_temps}")
    print(f"Question domains: {unique_domains}")
    print()
    
    # Overall accuracy by model
    print("OVERALL ACCURACY BY MODEL:")
    print("-" * 40)
    overall_accuracy = df.groupby('model_name').apply(
        lambda x: (x['result'] == 'Correct').sum() / len(x) * 100
    ).sort_values(ascending=False)
    
    for model, accuracy in overall_accuracy.items():
        total_questions = len(df[df['model_name'] == model])
        correct_answers = (df[df['model_name'] == model]['result'] == 'Correct').sum()
        print(f"{model:30} {accuracy:6.1f}% ({correct_answers}/{total_questions})")
    
    # Accuracy by temperature (if multiple temperatures tested)
    if unique_temps > 1:
        print("\nACCURACY BY TEMPERATURE:")
        print("-" * 40)
        temp_accuracy = df.groupby('temperature').apply(
            lambda x: (x['result'] == 'Correct').sum() / len(x) * 100
        ).sort_index()
        
        for temp, accuracy in temp_accuracy.items():
            total_questions = len(df[df['temperature'] == temp])
            correct_answers = (df[df['temperature'] == temp]['result'] == 'Correct').sum()
            print(f"Temperature {temp:4.1f}:        {accuracy:6.1f}% ({correct_answers}/{total_questions})")
    
    # Best performing model-temperature combinations
    if unique_temps > 1 and unique_models > 1:
        print("\nBEST MODEL-TEMPERATURE COMBINATIONS:")
        print("-" * 50)
        combo_accuracy = df.groupby(['model_name', 'temperature']).apply(
            lambda x: (x['result'] == 'Correct').sum() / len(x) * 100
        ).sort_values(ascending=False).head(5)
        
        for (model, temp), accuracy in combo_accuracy.items():
            subset = df[(df['model_name'] == model) & (df['temperature'] == temp)]
            total_questions = len(subset)
            correct_answers = (subset['result'] == 'Correct').sum()
            print(f"{model} (T={temp}): {accuracy:6.1f}% ({correct_answers}/{total_questions})")
    
    print("\nFiles generated in results/ folder:")
    print("- plot_overall_accuracy.png")
    print("- plot_temperature_comparison.png") 
    print("- plot_domain_performance.png")
    print("="*60)

def main():
    """Main function to analyze benchmark results."""
    # Check if pandas and matplotlib are available
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError as e:
        print("Error: Required libraries not found.")
        print("Please install them with: pip install pandas matplotlib seaborn")
        sys.exit(1)
    
    # Ensure results directory exists
    os.makedirs('results', exist_ok=True)
    
    # Set matplotlib style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Load results
    df = load_results("results/results.csv")
    if df is None:
        sys.exit(1)
    
    # Verify required columns exist
    required_columns = ['model_name', 'temperature', 'domain', 'result']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing required columns: {missing_columns}")
        sys.exit(1)
    
    # Generate plots
    print("\nGenerating analysis plots...")
    plot_overall_accuracy(df)
    plot_temperature_comparison(df)
    plot_domain_performance(df)
    
    # Print summary
    print_summary(df)

if __name__ == "__main__":
    main()