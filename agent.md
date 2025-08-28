agent.md — Pilot question bank for “Stata Understanding Benchmark”

1) What to build (small first version)

Create a 12-question pilot that tests understanding of Stata Language and Syntax only.
All questions must be auto-scorable (no human judging, no separate “judge model”).
The code and runner should be adaptable to local models or to a remote API, and be very simple to implement and document.
	•	Module: Language and Syntax
(command structure, options, variable lists, if/in, sort, by:/bysort, generate, egen, summarize including detail, tabulate, simple return values like r(N) after summarize).
	•	Question count: 12 total
	•	8 multiple-choice (you may use “None of the above” in at most two of these; if used, it must be the last option)
	•	4 short structured explanations (exactly two small fields per answer; see format below)
	•	Datasets: do not rely on external files. If needed, include tiny inline examples (e.g., input blocks) inside the question text.

2) Source you must use

You will be given the official Stata User’s Guide (PDF). You must use it to ground every question and answer key.

Rules about the PDF:
	•	For each question, include a reference with chapter and page number(s) in the JSON.
	•	Paraphrase; do not copy long text.
	•	If you cannot confirm a fact in the guide, pick a different concept within the module.

3) What to output

Produce a single file named items.jsonl with exactly 12 lines.
Each line is one JSON object that follows one of the two formats below.

3a) Multiple-choice format

Use when recognition is enough.

Fields
	•	task_id — unique string.
	•	module — always "Language and Syntax".
	•	manual_ref — object with chapter (number) and pages (string, e.g., "48–50").
	•	stata_code — optional string (only include if it helps the question).
	•	prompt — short, clear question text.
	•	choices — array of 4 options. If you wish to use “None of the above”, include it as the last element of choices.
	•	correct_index — zero-based index into choices.
	•	answer_type — "multiple_choice".
	•	difficulty — 1 (easy) or 2 (medium).
	•	tags — array of 2–4 short words.
	•	scoring — object: {"method":"choice_equals_index"}.

Rules
	•	Exactly one correct option.
	•	If you include “None of the above”, it must be the last choice. You may do this in at most two multiple-choice questions.
	•	If “None of the above” is correct, every other option must be fully wrong (no half-truths).
	•	Keep options concise (≤ 160 characters) and plausible.

Example

{
  "task_id": "LANG-001-MULTI",
  "module": "Language and Syntax",
  "manual_ref": {"chapter": 11, "pages": "48–50"},
  "stata_code": "summarize mpg, detail",
  "prompt": "What does this command produce?",
  "choices": [
    "A regression of mpg against all other variables",
    "A histogram of mpg",
    "Extended summary statistics for mpg, including percentiles and distribution diagnostics",
    "A table of value labels for mpg"
  ],
  "correct_index": 2,
  "answer_type": "multiple_choice",
  "difficulty": 1,
  "tags": ["summarize","detail","descriptives"],
  "scoring": {"method": "choice_equals_index"}
}

Example using “None of the above” (as last choice):

{
  "task_id": "LANG-002-MULTI",
  "module": "Language and Syntax",
  "manual_ref": {"chapter": 23, "pages": "—"},
  "stata_code": "append using other",
  "prompt": "Which statement about this command is true?",
  "choices": [
    "It merges datasets by a key and adds variables from both sides",
    "It creates a match-status variable named _merge",
    "It requires a 1:1 key to be specified",
    "None of the above"
  ],
  "correct_index": 3,
  "answer_type": "multiple_choice",
  "difficulty": 2,
  "tags": ["append","combine"],
  "scoring": {"method": "choice_equals_index"}
}

3b) Short structured explanation format

Use when a tiny bit of reasoning is needed but still auto-scorable.
Exactly two answer fields: a small number and a very short phrase/sentence.

Fields
	•	task_id, module, manual_ref, stata_code (optional), prompt
	•	answer_type — "structured"
	•	output_schema — an object with exactly two properties you define:
	•	one numeric property (e.g., num_slopes)
	•	one short text property (e.g., rule)
	•	scoring — object with:
	•	method: "number_and_phrase"
	•	must_equal: numeric key and its required value (e.g., { "num_slopes": 2 })
	•	accepted_phrases: array of short accepted strings (the text answer must contain one or more of these, case-insensitive)
	•	difficulty — 1 or 2
	•	tags — 2–4 short words

Example

{
  "task_id": "LANG-003-STRUCT",
  "module": "Language and Syntax",
  "manual_ref": {"chapter": 26, "pages": "—"},
  "stata_code": "reg price i.foreign##c.weight",
  "prompt": "How many distinct slopes for weight are estimated, and how is the slope for foreign==1 computed?",
  "answer_type": "structured",
  "output_schema": {
    "type": "object",
    "required": ["num_slopes", "rule"],
    "properties": {
      "num_slopes": {"type": "integer"},
      "rule": {"type": "string"}
    }
  },
  "scoring": {
    "method": "number_and_phrase",
    "must_equal": {"num_slopes": 2},
    "accepted_phrases": [
      "baseline plus interaction",
      "baseline + interaction",
      "add interaction to baseline"
    ]
  },
  "difficulty": 2,
  "tags": ["factor-variables","interactions"]
}

4) Minimal authoring workflow
	1.	Open the Stata User’s Guide PDF. Search within Language and Syntax topics.
	2.	Pick a small, clear concept and note the chapter and page numbers.
	3.	Choose the format:
	•	multiple-choice, or
	•	short structured explanation (two fields only).
	4.	Draft the question (and optional tiny code snippet).
	5.	Fill the JSON fields exactly as specified.
	6.	Repeat until you have 12 questions.
	7.	Validate that each JSON object is on its own line in items.jsonl.

5) Scoring contract (what the runner will do)

The runner will present each question to the model and expect a small JSON answer:
	•	For multiple-choice questions, the model must return:

{"choice": 0}

where 0 is the zero-based index of the selected option.
The runner marks correct if choice == correct_index.

	•	For short structured explanations, the model must return exactly the two fields named in output_schema (for example):

{"num_slopes": 2, "rule": "baseline plus interaction"}

The runner marks correct if:
	•	the number equals the value in scoring.must_equal, and
	•	the text contains at least one string from scoring.accepted_phrases (case-insensitive substring match).

6) Simple runner notes (local model or remote API)
	•	The runner should send a short system message:
“Answer in JSON only. No extra text. Use the schema given.”
	•	The runner should send a user message that includes:
	•	the task_id
	•	the prompt
	•	any stata_code
	•	the expected answer schema (e.g., { "choice": <integer> } or the two-field schema)
	•	The runner should accept either:
	•	a local model server, or
	•	a remote web endpoint (API).
	•	Keep configuration very small (for example: a list of {name, base_url, model, api_key}).
	•	Parsing: treat any non-JSON output as incorrect for this pilot.

7) Quality checklist before you finish
	•	Exactly 12 questions produced.
	•	Every task_id is unique.
	•	Every question has a valid manual_ref with chapter and page(s).
	•	Multiple-choice:
	•	exactly one correct option,
	•	“None of the above” used at most two times, and always last when used.
	•	Short structured explanations: exactly two answer fields; numeric rule + short phrase rule.
	•	No long quotes from the manual.
	•	JSON is valid; each line is one complete object.

⸻

End of file.