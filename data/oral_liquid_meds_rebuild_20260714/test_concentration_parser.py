import unittest

from concentration_parser import parse_concentration


def parse(label, value, unit, *, desc="", prep="ready_to_use"):
    return parse_concentration(
        prescription_label=label,
        amount_description=desc,
        amount_value=value,
        amount_unit=unit,
        ingredient_name="TEST INGREDIENT",
        preparation_type=prep,
        source_id="test",
    )


class ConcentrationParserTests(unittest.TestCase):
    def test_mg_per_ml(self):
        out = parse("EACH ML CONTAINS:", "10", "MG")
        self.assertEqual(out["display_concentration"], "10 mg/mL")
        self.assertEqual(out["normalized_value_per_ml"], "10")

    def test_mg_per_5_ml_preserves_display_basis(self):
        out = parse("EACH 5 ML CONTAINS:", "250", "MG")
        self.assertEqual(out["display_concentration"], "250 mg/5 mL")
        self.assertEqual(out["normalized_value_per_ml"], "50")

    def test_mcg_per_ml(self):
        out = parse("PER ML", "125", "MCG")
        self.assertEqual(out["display_concentration"], "125 mcg/mL")

    def test_iu_per_ml(self):
        out = parse("EACH 1 ML CONTAINS:", "400", "I.U.")
        self.assertEqual(out["display_concentration"], "400 IU/mL")

    def test_per_100_ml(self):
        out = parse("EACH 100ML CONTAINS:", "2", "GM")
        self.assertEqual(out["display_concentration"], "2 g/100 mL")
        self.assertEqual(out["normalized_value_per_ml"], "0.02")

    def test_milliliter_spelling(self):
        out = parse("EACH MILLILITER CONTAINS:", "0.48", "MG")
        self.assertEqual(out["display_concentration"], "0.48 mg/mL")

    def test_mass_basis_is_not_converted_to_per_ml(self):
        out = parse("EACH GM CONTAINS:", "200", "MG")
        self.assertEqual(out["display_concentration"], "200 mg/g")
        self.assertEqual(out["normalized_value_per_ml"], "")

    def test_bottle_total_not_converted(self):
        out = parse("EACH BOTTLE (60 ML) CONTAINS:", "500", "MG")
        self.assertEqual(out["display_concentration"], "500 mg/bottle")
        self.assertEqual(out["normalized_value_per_ml"], "")

    def test_sachet_total_not_converted(self):
        out = parse("EACH SACHET CONTAINS:", "100", "MG")
        self.assertEqual(out["display_concentration"], "100 mg/sachet")
        self.assertEqual(out["normalized_value_per_ml"], "")

    def test_reconstituted_without_explicit_marker_is_unresolved(self):
        out = parse("EACH 5 ML CONTAINS:", "125", "MG", prep="requires_reconstitution")
        self.assertEqual(out["normalization_status"], "unresolved")
        self.assertEqual(out["parsing_rule"], "reconstitution_context_missing")

    def test_reconstituted_explicit_post_concentration(self):
        out = parse("AFTER RECONSTITUTION EACH 5 ML CONTAINS:", "125", "MG", prep="requires_reconstitution")
        self.assertEqual(out["display_concentration"], "125 mg/5 mL")
        self.assertEqual(out["normalized_value_per_ml"], "25")

    def test_compound_syrup_components_are_independent(self):
        a = parse("EACH 5 ML CONTAINS:", "15", "MG")
        b = parse("EACH 5 ML CONTAINS:", "2", "MG")
        self.assertEqual((a["normalized_value_per_ml"], b["normalized_value_per_ml"]), ("3", "0.4"))

    def test_explicit_percent_wv(self):
        out = parse("0.2% W/V", "", "%", desc="0.2")
        self.assertEqual(out["display_concentration"], "0.2 g/100 mL")
        self.assertEqual(out["normalized_value_per_ml"], "0.002")

    def test_unclear_percent_is_not_guessed(self):
        out = parse("0.2%", "", "%", desc="0.2")
        self.assertEqual(out["normalization_status"], "unresolved")
        self.assertEqual(out["parsing_rule"], "percentage_basis_unclear")

    def test_percent_in_ingredient_name_does_not_override_mg_per_ml(self):
        out = parse("EACH ML CONTAINS:", "600", "MG", desc="600")
        self.assertEqual(out["display_concentration"], "600 mg/mL")

    def test_unidentifiable_format_remains_unresolved(self):
        out = parse("FORMULA A", "unknown", "MG")
        self.assertEqual(out["normalization_status"], "unresolved")


if __name__ == "__main__":
    unittest.main()
