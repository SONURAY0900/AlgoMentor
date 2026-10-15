from llm.client import call_llm


def run(context: dict) -> str:
    """
    Agent-07: Brute Force Agent

    Generates the simplest correct (naive) solution as a performance baseline.
    """
    language = context["language"]

    prompt = f"""
Write the simplest CORRECT brute-force solution to the problem below in {language}.

Rules:
- Use the most straightforward approach (plain loops / simple recursion). Do not optimize.
- The code must be complete, compile/run as written, and handle edge cases
  (empty input, single element, duplicates, negatives where relevant).
- Include a small `main` / driver with one example call and print its result
  (required for Java, C and C++; add a short `if __name__ == "__main__":` block for Python).

Output format (Markdown):
**Approach:** 2-3 sentences.

```{language.lower()}
<code>
```

**Time Complexity:** O(...) – worst case, with a one-line justification.
**Space Complexity:** O(...) – auxiliary space, with a one-line justification.

Problem:
{context["problem"]}
"""
    return call_llm(prompt)
