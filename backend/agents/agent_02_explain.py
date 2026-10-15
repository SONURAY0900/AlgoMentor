from llm.client import call_llm


def run(context: dict) -> str:
    """Agent-02: Code Explainer"""
    prompt = f"""
Explain the following {context["language"]} code in simple terms.

Include:
1. **Purpose** – what the code does, in one or two sentences.
2. **How it works** – a short step-by-step walkthrough of the logic.
3. **Example** – one small concrete input and the EXACT output this code produces for it
   (trace the code mentally; if the code has a bug, show what it really outputs).
   If the code has undefined or implementation-dependent behaviour (e.g. C/C++ invalidated
   iterators, out-of-bounds access, signed overflow, uninitialized variables), say so explicitly
   and do NOT claim an exact output — explain what may happen instead.

Code:
```{context["language"].lower()}
{context["code"]}
```
"""
    return call_llm(prompt)
