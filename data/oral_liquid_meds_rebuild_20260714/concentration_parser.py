"""Reusable parser for official TFDA ingredient-strength rows.

The parser preserves the official display basis (for example 250 mg/5 mL)
and separately calculates a per-mL value only when the denominator is an
explicit liquid volume.  Container totals are never converted to per mL.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any


UNIT_MAP = {
    "MCG": "mcg",
    "UG": "mcg",
    "ΜG": "mcg",
    "ΜG": "mcg",
    "MG": "mg",
    "GM": "g",
    "G": "g",
    "I.U.": "IU",
    "I.U": "IU",
    "IU": "IU",
    "U (UNIT)": "unit",
    "UNIT": "unit",
    "UNITS": "unit",
    "U": "unit",
    "USP-U (USP UNIT)": "unit",
    "MEQ": "mEq",
    "MMOL": "mmol",
    "ML": "mL",
    "UL": "uL",
}

RECONSTITUTION_MARKERS = (
    "配製後",
    "調製後",
    "復溶後",
    "加水後",
    "AFTER RECONSTITUTION",
    "WHEN RECONSTITUTED",
    "RECONSTITUTED",
)


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _decimal(value: Any) -> Decimal | None:
    text = _clean(value).replace(",", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        match = re.search(r"[-+]?\d+(?:\.\d+)?", text)
        if not match:
            return None
        try:
            return Decimal(match.group(0))
        except InvalidOperation:
            return None


def _fmt(value: Decimal | str | None) -> str:
    if value is None or value == "":
        return ""
    number = value if isinstance(value, Decimal) else Decimal(str(value))
    text = format(number.normalize(), "f")
    return "0" if text in {"-0", ""} else text


def _normalize_unit(raw_unit: str) -> tuple[str, str]:
    unit = _clean(raw_unit).upper().replace("Μ", "Μ")
    if "/" in unit:
        left, right = (x.strip() for x in unit.split("/", 1))
        if left in UNIT_MAP and right in {"ML", "CC"}:
            return UNIT_MAP[left], "embedded_per_ml"
    return UNIT_MAP.get(unit, ""), ""


def _denominator(label: str, unit_hint: str) -> tuple[Decimal | None, str, str]:
    upper = _clean(label).upper().replace("ＭＬ", "ML")

    # Container totals take precedence over a parenthetical fill volume.
    if any(token in upper for token in ("BOTTLE", "VIAL", "AMPOULE", "BTL", "每瓶")):
        return Decimal("1"), "bottle", "container_total_bottle"
    if any(token in upper for token in ("SACHET", "PACKET", "PACKAGE", "EACH PACK", "PER PACK", "每包")):
        return Decimal("1"), "sachet", "container_total_sachet"
    if any(token in upper for token in ("EACH DOSE", "PER DOSE", "每劑", "每次劑量")):
        return Decimal("1"), "dose", "dose_basis"
    if any(token in upper for token in ("EACH DROP", "PER DROP", "每滴")):
        return Decimal("1"), "drop", "drop_basis"

    chinese = re.search(r"每\s*(\d+(?:\.\d+)?)?\s*(?:毫升|公撮)", upper)
    if chinese:
        return Decimal(chinese.group(1) or "1"), "mL", "explicit_volume_basis"

    volumes = re.findall(r"(\d+(?:\.\d+)?)?\s*(ML|CC)\b", upper)
    if volumes:
        value = next((v for v, _ in volumes if v), "1")
        return Decimal(value), "mL", "explicit_volume_basis"

    if "MILLILITER" in upper or "MILLILITRE" in upper:
        match = re.search(r"(\d+(?:\.\d+)?)?\s*MILLILIT(?:ER|RE)", upper)
        return Decimal(match.group(1) if match and match.group(1) else "1"), "mL", "explicit_volume_basis"

    mass_basis = re.search(r"(?:EACH|PER)\s*(\d+(?:\.\d+)?)?\s*(?:GM|G)\b", upper)
    if mass_basis:
        return Decimal(mass_basis.group(1) or "1"), "g", "explicit_mass_basis"

    if unit_hint == "embedded_per_ml":
        return Decimal("1"), "mL", "unit_embedded_per_ml"
    return None, "", "denominator_not_identified"


def parse_concentration(
    *,
    prescription_label: str,
    amount_description: str,
    amount_value: Any,
    amount_unit: str,
    ingredient_name: str = "",
    preparation_type: str = "ready_to_use",
    source_id: str = "",
) -> dict[str, str]:
    """Parse one official TFDA ingredient row without guessing."""
    label = _clean(prescription_label)
    description = _clean(amount_description)
    unit_raw = _clean(amount_unit)
    official_amount_text = description or _clean(amount_value)
    joined = " ".join(x for x in (label, ingredient_name, official_amount_text, unit_raw) if x)
    strength_raw = joined
    upper = joined.upper()

    result = {
        "strength_raw": strength_raw,
        "numerator_value": "",
        "numerator_unit": "",
        "denominator_value": "",
        "denominator_unit": "",
        "display_concentration": "",
        "normalized_value_per_ml": "",
        "concentration_normalized": "",
        "normalization_status": "unresolved",
        "concentration_status": "unresolved",
        "parsing_rule": "unparsed",
        "confidence": "low",
        "source_id": source_id,
    }

    # Percentage conversion is allowed only when w/v is explicit.
    percent_is_the_quantity = unit_raw.upper() in {"%", "PERCENT"} or (
        amount_value in {None, ""} and ("W/V" in upper or "W／V" in upper)
    )
    if percent_is_the_quantity:
        percent = _decimal(description) or _decimal(label)
        if "W/V" not in upper and "W／V" not in upper:
            result["parsing_rule"] = "percentage_basis_unclear"
            return result
        if percent is None:
            result["parsing_rule"] = "percentage_value_missing"
            return result
        per_ml = percent / Decimal("100")
        result.update(
            {
                "numerator_value": _fmt(percent),
                "numerator_unit": "g",
                "denominator_value": "100",
                "denominator_unit": "mL",
                "display_concentration": f"{_fmt(percent)} g/100 mL",
                "normalized_value_per_ml": _fmt(per_ml),
                "concentration_normalized": f"{_fmt(per_ml)} g/mL",
                "normalization_status": "parsed_per_ml",
                "concentration_status": "parsed",
                "parsing_rule": "explicit_percent_wv",
                "confidence": "high",
            }
        )
        return result

    numerator = _decimal(amount_value)
    if numerator is None:
        numerator = _decimal(description)
    unit, unit_hint = _normalize_unit(unit_raw)
    if numerator is None:
        result["parsing_rule"] = "numerator_value_missing"
        return result
    if not unit:
        result["numerator_value"] = _fmt(numerator)
        result["parsing_rule"] = "unsupported_numerator_unit"
        return result

    denominator, denominator_unit, denominator_rule = _denominator(label, unit_hint)
    result.update({"numerator_value": _fmt(numerator), "numerator_unit": unit})
    if denominator is None:
        result["parsing_rule"] = denominator_rule
        return result

    result["denominator_value"] = _fmt(denominator)
    result["denominator_unit"] = denominator_unit
    basis = denominator_unit if denominator == 1 else f"{_fmt(denominator)} {denominator_unit}"
    result["display_concentration"] = f"{_fmt(numerator)} {unit}/{basis}"

    # Reconstituted products require explicit post-reconstitution wording.
    if preparation_type == "requires_reconstitution" and not any(
        marker in upper for marker in RECONSTITUTION_MARKERS
    ):
        result.update(
            {
                "display_concentration": "",
                "normalization_status": "unresolved",
                "concentration_status": "unresolved",
                "parsing_rule": "reconstitution_context_missing",
                "confidence": "low",
            }
        )
        return result

    if denominator_unit == "mL":
        per_ml = numerator / denominator
        result.update(
            {
                "normalized_value_per_ml": _fmt(per_ml),
                "concentration_normalized": f"{_fmt(per_ml)} {unit}/mL",
                "normalization_status": "parsed_per_ml",
                "concentration_status": "parsed",
                "parsing_rule": (
                    "explicit_post_reconstitution_volume"
                    if preparation_type == "requires_reconstitution"
                    else denominator_rule
                ),
                "confidence": "high",
            }
        )
    else:
        result.update(
            {
                "normalization_status": "parsed_non_volume_basis",
                "concentration_status": "parsed",
                "parsing_rule": denominator_rule,
                "confidence": "high",
            }
        )
    return result
