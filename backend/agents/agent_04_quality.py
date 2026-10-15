from llm.client import as_bool, call_llm_json


def run(context: dict) -> dict:
    """
    Agent-04: Quality Judge

    Checks correctness and whether the algorithm is asymptotically optimal
    for the task it solves.
    """
    prompt = f"""
Review this {context["language"]} code.

Task the code is meant to solve:
{context["problem"]}

Code:
```{context["language"].lower()}
{context["code"]}
```

Return a JSON object with:
- "is_correct": true if the code correctly solves the task for all valid inputs
  (including edge cases such as empty input, single element, duplicates, negatives), else false.
- "is_optimal": true only if no algorithm with a better worst-case time complexity exists
  for this task (ignore constant factors and style), else false.
- "issues": a list of short strings describing concrete bugs or inefficiencies (empty list if none).
"""
    result = call_llm_json(prompt)
    issues = result.get("issues") or []
    if not isinstance(issues, list):
        issues = [str(issues)]
    return {
        "is_correct": as_bool(result.get("is_correct")),
        "is_optimal": as_bool(result.get("is_optimal")),
        "issues": [str(i) for i in issues],
    }
