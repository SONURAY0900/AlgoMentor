from llm.client import call_llm


def run(context: dict) -> str:
    """
    Agent-08: Optimal Solution Agent

    Implements the optimal solution using the strategy chosen by Agent-06.
    """
    language = context["language"]
    plan = context["classification"]

    prompt = f"""
Write the OPTIMAL solution to the problem below in {language}.

Use this plan (decided by the analysis step):
- Strategy: {plan["strategy"]}
- Data structure: {plan["data_structure"] or "as needed"}
- Why: {plan["reason"]}

Rules:
- Solve exactly the given problem; keep the same inputs and output.
- The code must be complete, compile/run as written, and handle edge cases
  (empty input, single element, duplicates, negatives where relevant).
- Include a small `main` / driver with one example call and print its result
  (required for Java, C and C++; add a short `if __name__ == "__main__":` block for Python).
- Add brief comments on the key steps.
- The Approach text must describe exactly what the code does (what is stored, what is looked up).

Output format (Markdown):
**Approach:** 2-4 sentences describing the key idea.

```{language.lower()}
<code>
```

**Time Complexity:** O(...) – worst case, with a one-line justification.
**Space Complexity:** O(...) – auxiliary space, with a one-line justification.

Problem:
{context["problem"]}
"""
    return call_llm(prompt)
