"""Scoring service - IMPLEMENTED."""


def calculate_quality_score(results: list, rules: list) -> dict:
    """Calculate weighted quality score.

    Weighting by severity:
        HIGH = 3x weight
        MEDIUM = 2x weight
        LOW = 1x weight

    Args:
        results: List of check result dicts with 'rule_id' and 'passed' keys.
        rules: List of ValidationRule model instances.

    Returns:
        Dict with score, total_rules, passed_rules, failed_rules.
    """
    severity_weights = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

    if not rules:
        return {"score": 100.0, "total_rules": 0, "passed_rules": 0, "failed_rules": 0}

    # Build a lookup from rule_id -> rule for quick severity access
    rule_map = {rule.id: rule for rule in rules}

    total_weight = 0
    passed_weight = 0
    passed_count = 0
    failed_count = 0

    for result in results:
        rule = rule_map.get(result.get("rule_id"))
        weight = severity_weights.get(rule.severity, 1) if rule else 1

        total_weight += weight
        if result.get("passed"):
            passed_weight += weight
            passed_count += 1
        else:
            failed_count += 1

    score = (passed_weight / total_weight * 100) if total_weight > 0 else 0.0

    return {
        "score": round(score, 2),
        "total_rules": len(rules),
        "passed_rules": passed_count,
        "failed_rules": failed_count,
    }
