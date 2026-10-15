from llm.client import call_llm


def run(context: dict) -> str:
    """Agent-05: Root Cause Analyzer (runs only when the code is buggy or not optimal)"""
    issues = "\n".join(f"- {i}" for i in context["quality"]["issues"]) or "- (none listed)"

    prompt = f"""
The following {context["language"]} code was reviewed and found to be
{"incorrect" if not context["quality"]["is_correct"] else "correct but not optimal"}.

Reviewer notes:
{issues}

Explain the root cause(s):
- For each bug: the exact line/logic at fault, an input that triggers it, and the fix.
  If the bug causes undefined behaviour, say so; do not claim a specific output for it.
- Every fix must itself be correct for ALL inputs — check it when the bug happens at the
  first element, the last element, and on empty input. Never suggest a fix that has undefined
  behaviour (e.g. decrementing begin()). Prefer the simplest standard idiom.
- State the worst-case time complexity of each fix you propose. A fix that still repeats
  the same costly operation (e.g. erasing from the middle of an array in a loop) keeps the
  same complexity — do not call it faster. Keep this consistent everywhere in your answer.
- For each inefficiency: which part causes the extra cost, its complexity,
  and what idea removes the repeated work.
Be concise. Do not write the full corrected solution here.

Code:
```{context["language"].lower()}
{context["code"]}
```
"""
    return call_llm(prompt)
