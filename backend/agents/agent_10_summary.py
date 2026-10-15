from llm.client import call_llm


def run(context: dict) -> str:
    """
    Agent-10: Final Summary Agent

    Summarizes ONLY what earlier agents produced; complexities are copied
    from the generated solutions, not re-invented.
    """
    parts = [f"Mode: {context['mode']}", f"Language: {context['language']}",
             f"Problem:\n{context['problem']}"]

    if context.get("complexity"):
        parts.append(f"User code complexity analysis:\n{context['complexity']}")
    if context.get("quality"):
        q = context["quality"]
        parts.append(f"User code review: correct={q['is_correct']}, optimal={q['is_optimal']}, "
                     f"issues={q['issues'] or 'none'}")
    if context.get("classification"):
        c = context["classification"]
        parts.append(f"Category: {c['category']} | Data structure: {c['data_structure']} | "
                     f"Strategy: {c['strategy']}")
    if context.get("bruteforce"):
        parts.append(f"Brute-force solution:\n{context['bruteforce']}")
    if context.get("optimal"):
        parts.append(f"Optimal solution:\n{context['optimal']}")

    analysis = "\n\n".join(parts)

    rows = [name for name, key in (("User Code", "code"), ("Brute Force", "bruteforce"),
                                   ("Optimal", "optimal")) if context.get(key)]

    prompt = f"""
Write a short final summary of the analysis below.

Rules:
- Use ONLY the information in the analysis. Copy complexities exactly as stated there; do not invent new ones.
- If there is no separate optimal solution, say the brute-force / user approach is already optimal.

Output format (Markdown):
| | Time | Space |
|---|---|---|
exactly these rows, in this order: {", ".join(rows)}

**Strategy:** ...
**Key takeaway:** 1-2 sentences on what makes the best solution efficient
(or, for correct optimal user code, why it is already optimal).

Analysis:
{analysis}
"""
    return call_llm(prompt)
