from llm.client import call_llm_json


def run(context: dict) -> dict:
    """
    Agent-01: Input Classifier

    Decides whether the input is source code or a problem statement,
    detects the programming language, and states the task being solved.
    """
    prompt = f"""
Classify the user input below.

Return a JSON object with these keys:
- "input_type": "code" if the input contains source code to analyze, otherwise "problem"
  (a plain-language programming question / problem statement).
- "language": for code, the exact programming language of the code
  (e.g. "Python", "Java", "C", "C++", "JavaScript", "Go", ...).
  For a problem, the language the user explicitly asks for, or null if none is mentioned.
- "problem_statement": a clear, self-contained statement of the task.
  For code, state the problem the code is INTENDED to solve (inputs, output, constraints),
  i.e. the correct version of the task — do not copy the code's bugs into the statement
  (e.g. if it is Two Sum, the two indices must be distinct).
  For a problem, restate the user's problem faithfully without changing its meaning.

User input:
<<<
{context["input"]}
>>>
"""
    result = call_llm_json(prompt)
    return {
        "input_type": "code" if str(result.get("input_type", "")).lower() == "code" else "problem",
        "language": (result.get("language") or "").strip() or None,
        "problem_statement": (result.get("problem_statement") or "").strip(),
    }
