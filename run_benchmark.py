import json
import requests
import time

# --- Configuration ---
# 1. Update this with the name of the local model you are running (e.g., via Ollama)
LOCAL_MODEL_NAME = "gemma3:4b" 

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

def get_llm_response(prompt_text):
    """Sends a prompt to the local LLM and gets a JSON response."""
    system_message = "Answer in JSON only. No extra text. Use the schema given."
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": LOCAL_MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_text}
        ],
        "format": "json", # This tells Ollama to ensure the output is valid JSON
        "stream": False
    }

    raw_response_text = ""
    try:
        # Added a 60-second timeout to give the model enough time to respond
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        response_data = response.json()
        raw_response_text = response_data['choices'][0]['message']['content']

        # --- FIX ADDED HERE ---
        # Clean the response in case the model wraps it in a markdown block
        cleaned_text = raw_response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:] # Remove ```json
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3] # Remove ```
        
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
            if expected_index == actual_choice:
                return "Correct", f"Model chose index {actual_choice}."
            else:
                return "Incorrect", f"Model chose index {actual_choice}, expected {expected_index}."

    elif answer_type == "structured":
        if scoring_rules.get("method") == "number_and_phrase":
            must_equal_rule = scoring_rules.get("must_equal", {})
            num_key = list(must_equal_rule.keys())[0]
            expected_num = must_equal_rule[num_key]
            actual_num = llm_answer.get(num_key)

            # Be more flexible with numeric types (e.g., model might return "4" instead of 4)
            if str(actual_num) != str(expected_num):
                return "Incorrect", f"Numeric check failed. Expected '{num_key}': {expected_num}, got {actual_num}."

            accepted_phrases = scoring_rules.get("accepted_phrases", [])
            text_keys = [k for k in question['output_schema']['properties'].keys() if k != num_key]
            if not text_keys:
                 return "Scoring Error", "Could not find text key in schema."
            text_key = text_keys[0]
            actual_text = str(llm_answer.get(text_key, "")).lower()

            if any(phrase.lower() in actual_text for phrase in accepted_phrases):
                return "Correct", f"Numeric and phrase checks passed."
            else:
                return "Incorrect", f"Phrase check failed. Text '{actual_text}' did not contain any accepted phrases."

    return "Scoring Error", "Could not determine how to score this question type."


def main():
    """Main function to run the benchmark."""
    print(f"--- Starting Stata Benchmark for model: {LOCAL_MODEL_NAME} ---")
    
    if not check_server_status():
        return # Stop if the server isn't running

    try:
        with open(ITEMS_FILE, 'r') as f:
            questions = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"Error: The file '{ITEMS_FILE}' was not found in this directory.")
        return

    total_correct = 0
    total_questions = len(questions)

    for i, question in enumerate(questions):
        task_id = question["task_id"]
        prompt = question["prompt"]
        
        if question['answer_type'] == 'multiple_choice':
            choices_text = "\n".join([f"{idx}) {choice}" for idx, choice in enumerate(question['choices'])])
            schema = '{"choice": <integer>}'
            full_prompt = f"{prompt}\n\nChoices:\n{choices_text}\n\nAnswer with JSON using this schema:\n{schema}"
        else: # structured
            schema = json.dumps({k: v['type'] for k, v in question['output_schema']['properties'].items()})
            full_prompt = f"{prompt}\n\nAnswer with JSON using this schema:\n{schema}"

        print(f"\n({i+1}/{total_questions}) Running Task: {task_id}...")
        
        llm_answer = get_llm_response(full_prompt)
        
        result, reason = score_response(question, llm_answer)

        if result == "Correct":
            total_correct += 1
        
        print(f"  > Result: {result} ({reason})")
        time.sleep(1) # Pause for 1 second to avoid overwhelming the server

    print("\n--- Benchmark Complete ---")
    print(f"Final Score: {total_correct} / {total_questions} Correct")
    print(f"Accuracy: {total_correct / total_questions:.2%}")


if __name__ == "__main__":
    main()
