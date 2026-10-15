def format_response(context: dict) -> dict:
    quality = context.get("quality")
    return {
        "mode": context.get("mode"),
        "language": context.get("language"),
        "problem_statement": context.get("problem"),
        "notes": context.get("notes", []),

        "analysis": {
            "code_explanation": context.get("explanation"),
            "complexity": context.get("complexity"),
            "quality": quality,
            "root_cause": context.get("root_cause"),
        } if context.get("mode") == "CODE" else None,

        "classification": context.get("classification"),

        "solutions": {
            "bruteforce": context.get("bruteforce"),
            "optimal": context.get("optimal"),
        },

        "solution_explanation": context.get("solution_explanation"),
        "summary": context.get("summary"),
    }
