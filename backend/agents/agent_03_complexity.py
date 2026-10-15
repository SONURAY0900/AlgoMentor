from llm.client import call_llm


def run(context: dict) -> str:
    """Agent-03: Complexity Analyzer"""
    prompt = f"""
Analyze the worst-case time and space complexity of this {context["language"]} code.

Output format (Markdown):
- **Time Complexity:** O(...) – one-line justification (which loops / recursion dominate)
- **Space Complexity:** O(...) – one-line justification (auxiliary space; mention recursion stack if any)

Define any variables you use (e.g. n = length of the array).

Code:
```{context["language"].lower()}
{context["code"]}
```
"""
    return call_llm(prompt)
