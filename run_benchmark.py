import json
import requests
import time

# --- Configuration ---
# 1. Add the names of all local models you want to test into this list.
MODELS_TO_TEST = ["hf.co/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:Q4_K_M", "gemma3:270m"] 

# 2. This is the standard API endpoint for local servers like Ollama.
#    Change it if your server uses a different address.
API_URL = "http://localhost:11434/v1/chat/completions"
BASE_URL = "http://localhost:11434" # For checking server status

# 3. The name of your question file.
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

def get_llm_response(prompt_text, model_name):
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
        # --- BEST PRACTICE ADDED HERE ---
        # Set a low temperature for consistent, deterministic results.
        "temperature": 0.1
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


def main():
    """Main function to run the benchmark."""
    print(f"--- Stata Benchmark Runner ---")
    
    if not check_server_status():
        return

    try:
        with open(ITEMS_FILE, 'r') as f:
            questions = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"Error: The file '{ITEMS_FILE}' was not found in this directory.")
        return

    all_results = {}
    total_questions = len(questions)

    for model_name in MODELS_TO_TEST:
        print(f"\n--- Starting Benchmark for model: {model_name} ---")
        total_correct = 0

        for i, question in enumerate(questions):
            task_id = question["task_id"]
            prompt = question["prompt"]
            
            if question['answer_type'] == 'multiple_choice':
                choices_text = "\n".join([f"{idx}) {choice}" for idx, choice in enumerate(question['choices'])])
                schema = '{"choice": <integer>}'
                full_prompt = f"{prompt}\n\nChoices:\n{choices_text}\n\nAnswer with JSON using this schema:\n{schema}"
            else: # structured_single
                schema = json.dumps({k: v['type'] for k, v in question['output_schema']['properties'].items()})
                full_prompt = f"{prompt}\n\nAnswer with JSON using this schema:\n{schema}"

            print(f"\n({i+1}/{total_questions}) Running Task: {task_id}...")
            
            llm_answer = get_llm_response(full_prompt, model_name)
            
            result, reason = score_response(question, llm_answer)

            if result == "Correct":
                total_correct += 1
            
            print(f"  > Result: {result} ({reason})")
            time.sleep(1)
        
        all_results[model_name] = {
            "correct": total_correct,
            "total": total_questions,
            "accuracy": f"{total_correct / total_questions:.2%}"
        }

    print("\n\n--- Benchmark Complete: Final Summary ---")
    for model_name, result in all_results.items():
        print(f"Model: {model_name}")
        print(f"  > Score: {result['correct']} / {result['total']}")
        print(f"  > Accuracy: {result['accuracy']}")
        print("-" * 20)


if __name__ == "__main__":
    main()
