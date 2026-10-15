from llm.client import as_bool, call_llm_json

CATEGORIES = [
    "Array / String", "Linked List", "Stack / Queue", "Hash Table", "Tree", "Heap",
    "Graph", "Searching / Sorting", "Dynamic Programming", "Recursion / Backtracking",
    "Greedy", "Math", "Bit Manipulation", "Other",
]

STRATEGIES = [
    "Two Pointers", "Sliding Window", "Prefix Sum", "Hashing", "Binary Search",
    "DFS", "BFS", "Greedy", "Sorting", "Stack / Monotonic Stack", "Heap / Priority Queue",
    "Divide and Conquer", "Memoization", "Tabulation", "Backtracking",
    "Union-Find", "Bit Manipulation", "Mathematical Observation", "Direct Simulation",
]


def run(context: dict) -> dict:
    """
    Agent-06: Data Structure & Strategy Advisor

    Picks the problem category, the best data structure, and the strategy
    that gives the optimal solution.
    """
    code_part = ""
    if context.get("code"):
        code_part = f"\nUser's current code ({context['language']}):\n```\n{context['code']}\n```\n"

    prompt = f"""
Classify the programming problem below and choose the approach for the OPTIMAL solution.

Problem:
{context["problem"]}
{code_part}
Return a JSON object with:
- "category": the main problem category. Prefer one of: {", ".join(CATEGORIES)}.
- "data_structure": the key data structure(s) the optimal solution uses.
- "strategy": the algorithmic strategy of the optimal solution. Prefer one of: {", ".join(STRATEGIES)}.
  If none fits, give a short accurate name.
- "reason": 2-3 sentences explaining why this data structure and strategy give the best worst-case complexity.
- "better_than_bruteforce": true if the optimal solution has a strictly better time or space
  complexity than the most naive solution; false if the naive solution is already optimal
  (e.g. a simple traversal that must visit every element).
"""
    result = call_llm_json(prompt)
    return {
        "category": str(result.get("category") or "Other").strip(),
        "data_structure": str(result.get("data_structure") or "").strip(),
        "strategy": str(result.get("strategy") or "Direct Simulation").strip(),
        "reason": str(result.get("reason") or "").strip(),
        "better_than_bruteforce": as_bool(result.get("better_than_bruteforce")),
    }
