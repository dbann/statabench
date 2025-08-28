import json
import requests
import time
import argparse
import csv
from datetime import datetime
import os

# --- Configuration ---
# API endpoint for local servers like Ollama
API_URL = "http://localhost:11434/v1/chat/completions"
BASE_URL = "http://localhost:11434" # For checking server status

# The name of your question file
ITEMS_FILE = "items.jsonl"
# --- End of Configuration ---

def check_server_status():
    """Checks if the local LLM server is running before starting."""
    try:
        requests.get(BASE_URL, timeout=5)
        print(f"Successfully connected to the server at {BASE_URL}")
        return True
    except requests.exceptions.RequestException:
        print(f"--- Connection Error ---")
        print(f"Could not connect to the server at {BASE_URL}.")
        print(f"Please make sure your local LLM server (e.g., Ollama) is running.")
        return False

def get_llm_response(prompt_text, model_name, temperature):
    """Sends a prompt to the local LLM and gets a JSON response."""
    system_message = "Answer in JSON only. No extra text. Use the schema given."
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_text}
        ],
        "format": "json",
        "stream": False,
        "temperature": temperature
    }

    raw_response_text = ""
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        response_data = response.json()
        raw_response_text = response_data['choices'][0]['message']['content']

        cleaned_text = raw_response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        
        return json.loads(cleaned_text.strip())

    except requests.exceptions.RequestException as e:
        print(f"\n--- API Error ---")
        print(f"An error occurred while communicating with the model API.")
        print(f"Error details: {e}")
        return None
    except json.JSONDecodeError:
        print(f"\n--- Model Output Error ---")
        print(f"The model did not return valid JSON. Raw response was:")
        print(f"'{raw_response_text}'")
        return {"error": "Invalid JSON response from model"}
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        return None


def score_response(question, llm_answer):
    """Scores the LLM's answer based on the rules in the question JSON."""
    if not llm_answer or "error" in llm_answer:
        return "Incorrect", "Model did not provide a valid answer."

    answer_type = question.get("answer_type")
    scoring_rules = question.get("scoring", {})

    if answer_type == "multiple_choice":
        if scoring_rules.get("method") == "choice_equals_index":
            expected_index = question.get("correct_index")
            actual_choice = llm_answer.get("choice")
            
            try:
                if int(expected_index) == int(actual_choice):
                    return "Correct", f"Model chose index {actual_choice}."
                else:
                    return "Incorrect", f"Model chose index {actual_choice}, expected {expected_index}."
            except (ValueError, TypeError):
                return "Incorrect", f"Model returned a non-integer choice: '{actual_choice}'."

    elif answer_type == "structured_single":
        answer_key = list(llm_answer.keys())[0]
        actual_value = llm_answer.get(answer_key)

        if scoring_rules.get("method") == "numeric_match":
            expected_value = scoring_rules.get("expected_value")
            if str(actual_value) == str(expected_value):
                return "Correct", f"Model answered {actual_value}."
            else:
                return "Incorrect", f"Numeric check failed. Expected {expected_value}, got {actual_value}."
        
        elif scoring_rules.get("method") == "phrase_match":
            accepted_phrases = scoring_rules.get("accepted_phrases", [])
            actual_text = str(actual_value).lower()
            if any(phrase.lower() in actual_text for phrase in accepted_phrases):
                return "Correct", f"Phrase check passed."
            else:
                return "Incorrect", f"Phrase check failed. Text '{actual_text}' did not contain any accepted phrases."

    return "Scoring Error", f"Could not determine how to score this question type: '{answer_type}'"


def write_csv_header(output_file):
    """Write the CSV header if the file doesn't exist."""
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'model_name', 'temperature', 'task_id', 'domain', 'result']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

def append_result_to_csv(output_file, model_name, temperature, task_id, domain, result):
    """Append a single result to the CSV file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'model_name', 'temperature', 'task_id', 'domain', 'result']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({
            'timestamp': timestamp,
            'model_name': model_name,
            'temperature': temperature,
            'task_id': task_id,
            'domain': domain,
            'result': result
        })

def main():
    """Main function to run the benchmark."""
    parser = argparse.ArgumentParser(description='Run language model benchmark')
    parser.add_argument('--model_name', type=str, required=True, help='Name of the model to test')
    parser.add_argument('--temperature', type=float, required=True, help='Temperature setting for the model')
    parser.add_argument('--output_file', type=str, default='results.csv', help='Output CSV file name')
    
    args = parser.parse_args()
    
    # Ensure results directory exists and prepend to output file
    results_dir = 'results'
    os.makedirs(results_dir, exist_ok=True)
    
    # If output_file doesn't already include the results directory, prepend it
    if not args.output_file.startswith('results/'):
        args.output_file = os.path.join(results_dir, args.output_file)
    
    print(f"--- Stata Benchmark Runner ---")
    print(f"Model: {args.model_name}")
    print(f"Temperature: {args.temperature}")
    print(f"Output file: {args.output_file}")
    
    if not check_server_status():
        return

    try:
        with open(ITEMS_FILE, 'r') as f:
            questions = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"Error: The file '{ITEMS_FILE}' was not found in this directory.")
        return

    # Initialize CSV file if it doesn't exist
    if not os.path.exists(args.output_file):
        write_csv_header(args.output_file)
        print(f"Created new CSV file: {args.output_file}")
    else:
        print(f"Appending to existing CSV file: {args.output_file}")

    total_questions = len(questions)
    total_correct = 0

    print(f"\n--- Starting Benchmark for model: {args.model_name} ---")

    for i, question in enumerate(questions):
        task_id = question["task_id"]
        domain = question["domain"]
        prompt = question["prompt"]
        
        if question['answer_type'] == 'multiple_choice':
            choices_text = "\n".join([f"{idx}) {choice}" for idx, choice in enumerate(question['choices'])])
            schema = '{"choice": <integer>}'
            full_prompt = f"{prompt}\n\nChoices:\n{choices_text}\n\nAnswer with JSON using this schema:\n{schema}"
        else: # structured_single
            schema = json.dumps({k: v['type'] for k, v in question['output_schema']['properties'].items()})
            full_prompt = f"{prompt}\n\nAnswer with JSON using this schema:\n{schema}"

        print(f"\n({i+1}/{total_questions}) Running Task: {task_id}...")
        
        llm_answer = get_llm_response(full_prompt, args.model_name, args.temperature)
        
        result, reason = score_response(question, llm_answer)

        if result == "Correct":
            total_correct += 1
        
        # Append result to CSV immediately after scoring
        append_result_to_csv(args.output_file, args.model_name, args.temperature, task_id, domain, result)
        
        print(f"  > Result: {result} ({reason})")
        time.sleep(1)

    accuracy = total_correct / total_questions
    print(f"\n--- Benchmark Complete ---")
    print(f"Model: {args.model_name}")
    print(f"Temperature: {args.temperature}")
    print(f"Score: {total_correct} / {total_questions}")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Results saved to: {args.output_file}")


if __name__ == "__main__":
    main()
