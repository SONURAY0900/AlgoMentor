from concurrent.futures import ThreadPoolExecutor

import config
from utils.response_formatter import format_response

from agents.agent_01_language import run as agent_01
from agents.agent_02_explain import run as agent_02
from agents.agent_03_complexity import run as agent_03
from agents.agent_04_quality import run as agent_04
from agents.agent_05_rootcause import run as agent_05
from agents.agent_06_ds import run as agent_06
from agents.agent_07_bruteforce import run as agent_07
from agents.agent_08_optimal import run as agent_08
from agents.agent_09_explain_opt import run as agent_09
from agents.agent_10_summary import run as agent_10


class PipelineError(Exception):
    """A user-facing error (bad input, unsupported language)."""


LANGUAGE_ALIASES = {"py": "Python", "python3": "Python", "cpp": "C++", "c plus plus": "C++"}


def normalize_language(name):
    """Map a language name to one of SUPPORTED_LANGUAGES, or None if unknown."""
    if not name:
        return None
    key = name.strip().lower()
    for lang in config.SUPPORTED_LANGUAGES:
        if key == lang.lower():
            return lang
    return LANGUAGE_ALIASES.get(key)


def run_parallel(context: dict, agents: dict) -> None:
    """Run independent agents concurrently and store each result in context[key]."""
    if not agents:
        return
    with ThreadPoolExecutor(max_workers=len(agents)) as pool:
        futures = {key: pool.submit(agent, context) for key, agent in agents.items()}
        for key, future in futures.items():
            context[key] = future.result()


# ---------------------------------
# MAIN PIPELINE
# ---------------------------------
def run_pipeline(request) -> dict:
    code = (request.code or "").strip()
    problem = (request.problem or "").strip()
    text = (request.input or "").strip() or "\n\n".join(p for p in (problem, code) if p)

    if not text:
        raise PipelineError("Please paste some code or describe a problem.")
    if len(text) > config.MAX_INPUT_CHARS:
        raise PipelineError(f"Input is too long (max {config.MAX_INPUT_CHARS} characters).")

    selected_language = normalize_language(request.language)
    if request.language and not selected_language:
        raise PipelineError(f"Unsupported language '{request.language}'. "
                            f"Choose one of: {', '.join(config.SUPPORTED_LANGUAGES)}.")

    context = {"input": text, "notes": []}

    # -------------------------------
    # INPUT CLASSIFICATION (Agent-01)
    # -------------------------------
    detected = agent_01(context)

    if code:
        mode = "CODE"            # caller explicitly sent code
    elif problem:
        mode = "PROBLEM"         # caller explicitly sent a problem
    else:
        mode = "CODE" if detected["input_type"] == "code" else "PROBLEM"

    context["mode"] = mode
    context["problem"] = detected["problem_statement"] or problem or text

    if mode == "CODE":
        language = normalize_language(detected["language"]) or selected_language
        if not language:
            raise PipelineError(f"Detected language: {detected['language'] or 'unknown'}. "
                                f"Only {', '.join(config.SUPPORTED_LANGUAGES)} code is supported.")
        if selected_language and selected_language != language:
            context["notes"].append(f"You selected {selected_language}, but the code is {language}; "
                                    f"analyzing it as {language}.")
        context["language"] = language
        context["code"] = code or text
        _run_code_mode(context)
    else:
        requested = detected["language"]
        language = selected_language or normalize_language(requested)
        if not language:
            if requested:
                raise PipelineError(f"'{requested}' is not supported yet. "
                                    f"Choose one of: {', '.join(config.SUPPORTED_LANGUAGES)}.")
            language = config.DEFAULT_LANGUAGE
        context["language"] = language
        _run_problem_mode(context)

    # -------------------------------
    # FINAL SUMMARY (Agent-10)
    # -------------------------------
    context["summary"] = agent_10(context)
    return format_response(context)


def _run_code_mode(context: dict) -> None:
    # Agents 02, 03, 04, 06 only need the code + problem statement
    run_parallel(context, {
        "explanation": agent_02,
        "complexity": agent_03,
        "quality": agent_04,
        "classification": agent_06,
    })

    quality = context["quality"]
    if quality["is_correct"] and quality["is_optimal"]:
        context["notes"].append("Your code is correct and already optimal.")
        return

    # Code is buggy or slow: explain why and generate correct solutions
    stage = {"root_cause": agent_05, "bruteforce": agent_07}
    if context["classification"]["better_than_bruteforce"]:
        stage["optimal"] = agent_08
    run_parallel(context, stage)

    _explain_final_solution(context)


def _run_problem_mode(context: dict) -> None:
    # Brute force does not depend on the strategy, so it runs alongside Agent-06
    run_parallel(context, {"classification": agent_06, "bruteforce": agent_07})

    if context["classification"]["better_than_bruteforce"]:
        context["optimal"] = agent_08(context)

    _explain_final_solution(context)


def _explain_final_solution(context: dict) -> None:
    if not context.get("optimal"):
        context["notes"].append("The brute-force approach is already optimal for this problem.")
    context["final_solution"] = context.get("optimal") or context["bruteforce"]
    context["solution_explanation"] = agent_09(context)
