from llm.client import call_llm


def run(context: dict) -> str:
    """
    Agent-09: Solution Explainer

    Explains the final (optimal) solution and dry-runs THAT exact code,
    so the walkthrough always matches the code shown to the user.
    """
    prompt = f"""
Explain the solution below and dry-run it.

Output format (Markdown):
### Core Idea
2-4 sentences.

### Why It Works
Key insight / invariant that guarantees correctness.

### Dry Run
Use the example input from the solution's driver code. Show each step as a numbered list
(or a small table) with the values of the important variables, then the final output.
The output MUST be exactly what this code prints for that input — trace it carefully.

### Edge Cases
Bullet list of the important edge cases and how the code handles them.

Problem:
{context["problem"]}

Solution ({context["language"]}):
{context["final_solution"]}
"""
    return call_llm(prompt)
