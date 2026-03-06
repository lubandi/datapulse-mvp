"""Validation engine - FULLY IMPLEMENTED."""

import json
import re
import pandas as pd


class ValidationEngine:
    """Runs data quality checks against a DataFrame."""

    def run_all_checks(self, df: pd.DataFrame, rules: list) -> list:
        """Run all validation checks. Returns list of result dicts."""
        results = []
        for rule in rules:
            params = json.loads(rule.parameters) if rule.parameters else {}
            if rule.rule_type == "NOT_NULL":
                result = self.null_check(df, rule.field_name)
            elif rule.rule_type == "DATA_TYPE":
                result = self.type_check(df, rule.field_name, params.get("expected_type", "str"))
            elif rule.rule_type == "RANGE":
                result = self.range_check(df, rule.field_name, params.get("min"), params.get("max"))
            elif rule.rule_type == "UNIQUE":
                result = self.unique_check(df, rule.field_name)
            elif rule.rule_type == "REGEX":
                result = self.regex_check(df, rule.field_name, params.get("pattern", ""))
            else:
                result = {"passed": False, "failed_rows": 0, "total_rows": len(df),
                    "details": f"Unknown rule_type: {rule.rule_type}"}
            result["rule_id"] = rule.id
            results.append(result)
        return results

    def null_check(self, df: pd.DataFrame, field: str) -> dict:
        """Check for null values in a field - IMPLEMENTED."""
        if field not in df.columns:
            return {"passed": False, "failed_rows": len(df), "total_rows": len(df),
                "details": f"Field {field} not found in dataset"}
        null_count = int(df[field].isnull().sum())
        return {
            "passed": null_count == 0,
            "failed_rows": null_count,
            "total_rows": len(df),
            "details": f"{null_count} null values found in {field}",
        }

    def type_check(self, df: pd.DataFrame, field: str, expected_type: str) -> dict:
        """Check data types by attempting coercion to the expected type.

        Supported expected_type values: 'int', 'float', 'numeric', 'str', 'datetime', 'bool'.
        """
        if field not in df.columns:
            return {"passed": False, "failed_rows": len(df), "total_rows": len(df),
                "details": f"Field {field} not found in dataset"}

        total = len(df)
        non_null = df[field].dropna()

        if expected_type in ("int", "float", "numeric"):
            converted = pd.to_numeric(non_null, errors="coerce")
            failed_count = int(converted.isna().sum())
            if expected_type == "int" and failed_count == 0:
                # additionally check that surviving values are whole numbers
                failed_count = int((converted != converted.round(0)).sum())
        elif expected_type == "datetime":
            converted = pd.to_datetime(non_null, errors="coerce")
            failed_count = int(converted.isna().sum())
        elif expected_type == "bool":
            valid_bools = {"true", "false", "1", "0", "yes", "no"}
            failed_count = int(~non_null.astype(str).str.lower().isin(valid_bools)).sum()
        elif expected_type == "str":
            # Everything is representable as string
            failed_count = 0
        else:
            return {"passed": False, "failed_rows": total, "total_rows": total,
                "details": f"Unsupported expected_type: {expected_type}"}

        return {
            "passed": failed_count == 0,
            "failed_rows": failed_count,
            "total_rows": total,
            "details": f"{failed_count} rows failed {expected_type} type check on {field}",
        }

    def range_check(self, df: pd.DataFrame, field: str, min_val, max_val) -> dict:
        """Check that numeric values fall within [min_val, max_val]."""
        if field not in df.columns:
            return {"passed": False, "failed_rows": len(df), "total_rows": len(df),
                "details": f"Field {field} not found in dataset"}

        total = len(df)
        numeric = pd.to_numeric(df[field], errors="coerce")
        non_numeric_count = int(numeric.isna().sum() - df[field].isna().sum())

        failed_count = non_numeric_count
        if min_val is not None:
            failed_count += int((numeric < float(min_val)).sum())
        if max_val is not None:
            failed_count += int((numeric > float(max_val)).sum())

        return {
            "passed": failed_count == 0,
            "failed_rows": failed_count,
            "total_rows": total,
            "details": f"{failed_count} rows out of range [{min_val}, {max_val}] on {field}",
        }

    def unique_check(self, df: pd.DataFrame, field: str) -> dict:
        """Check that all values in a field are unique (no duplicates)."""
        if field not in df.columns:
            return {"passed": False, "failed_rows": len(df), "total_rows": len(df),
                "details": f"Field {field} not found in dataset"}

        total = len(df)
        duplicate_count = int(df[field].duplicated(keep=False).sum())

        return {
            "passed": duplicate_count == 0,
            "failed_rows": duplicate_count,
            "total_rows": total,
            "details": f"{duplicate_count} duplicate values found in {field}",
        }

    def regex_check(self, df: pd.DataFrame, field: str, pattern: str) -> dict:
        """Check that all non-null values match the given regex pattern."""
        if field not in df.columns:
            return {"passed": False, "failed_rows": len(df), "total_rows": len(df),
                "details": f"Field {field} not found in dataset"}

        if not pattern:
            return {"passed": False, "failed_rows": len(df), "total_rows": len(df),
                "details": "No regex pattern provided"}

        total = len(df)
        non_null = df[field].dropna()
        matches = non_null.astype(str).str.fullmatch(pattern)
        failed_count = int((~matches).sum())

        return {
            "passed": failed_count == 0,
            "failed_rows": failed_count,
            "total_rows": total,
            "details": f"{failed_count} rows did not match pattern '{pattern}' on {field}",
        }

