import os
import sys
import unittest

sys.path.append(os.path.abspath(".."))
from citation import CitationType, classify_cite

# Sample usage: python3 citation_test.py [update]


class TestClassifyCite(unittest.TestCase):
    # This unit test stress-tests the regexp patterns in citation.py
    # and their ability to distinguish among different citation types.
    # It also checks that matched groups are correctly extracted.

    def setUp(self):
        # Directory for test data
        self.test_data_dir = os.path.join(os.getcwd(), "test_data", "citation_test")

        with open(
            os.path.join(self.test_data_dir, "citation_test_input.txt"), "r"
        ) as f:
            self.test_cases = f.readlines()

        with open(
            os.path.join(self.test_data_dir, "citation_test_output_type.txt"), "r"
        ) as f:
            self.expected_types = [CitationType[line.strip()] for line in f.readlines()]

        with open(
            os.path.join(self.test_data_dir, "citation_test_output_shortcite.txt"), "r"
        ) as f:
            self.expected_shortcites = [line.strip() for line in f.readlines()]

        with open(
            os.path.join(self.test_data_dir, "citation_test_output_reference.txt"), "r"
        ) as f:
            self.expected_references = [line.strip() for line in f.readlines()]

    def test_classify_cite(self):
        errors = {}
        lookback_errors = []

        for i, text in enumerate(self.test_cases):
            text = text.strip()
            expected_type = self.expected_types[i]
            expected_shortcite = (
                self.expected_shortcites[i]
                if self.expected_shortcites[i] != "None"
                else None
            )
            expected_reference = (
                self.expected_references[i]
                if self.expected_references[i] != "None"
                else None
            )

            citation_type, lookback = classify_cite(text)

            # Check citation type
            if citation_type != expected_type:
                error_key = (expected_type.name, citation_type.name)
                if error_key not in errors:
                    errors[error_key] = []
                errors[error_key].append(text)

            # Check lookback for SUPRA and LOOKBACK_5 types
            if citation_type == CitationType.SUPRA:
                if "reference" not in lookback:
                    lookback_errors.append(
                        f"Missing 'reference' in lookback for SUPRA: {text}"
                    )
                if "shortcite" not in lookback:
                    lookback_errors.append(
                        f"Missing 'shortcite' in lookback for SUPRA: {text}"
                    )
            elif citation_type == CitationType.LOOKBACK_5:
                if "shortcite" not in lookback:
                    lookback_errors.append(
                        f"Missing 'shortcite' in lookback for LOOKBACK_5: {text}"
                    )

            # Check lookback values
            if expected_shortcite and lookback.get("shortcite") != expected_shortcite:
                lookback_errors.append(
                    f"Expected shortcite '{expected_shortcite}' but got '{lookback.get('shortcite')}' for: {text}"
                )
            if expected_reference and lookback.get("reference") != expected_reference:
                lookback_errors.append(
                    f"Expected reference '{expected_reference}' but got '{lookback.get('reference')}' for: {text}"
                )

        if errors or lookback_errors:
            error_messages = []
            for (expected, actual), citations in errors.items():
                error_messages.append(
                    f"Expected {expected} but got {actual} for the following citations:\n"
                    + "\n".join(citations)
                )
            if lookback_errors:
                error_messages.append("Lookback errors:\n" + "\n".join(lookback_errors))
            self.fail("\n\n".join(error_messages))

    def update_output(self):
        with open(
            os.path.join(self.test_data_dir, "citation_test_output_type.txt"), "w"
        ) as f_type, open(
            os.path.join(self.test_data_dir, "citation_test_output_shortcite.txt"), "w"
        ) as f_shortcite, open(
            os.path.join(self.test_data_dir, "citation_test_output_reference.txt"), "w"
        ) as f_reference:
            for text in self.test_cases:
                text = text.strip()
                citation_type, lookback = classify_cite(text)
                f_type.write(f"{citation_type.name}\n")
                f_shortcite.write(f"{lookback.get('shortcite', 'None')}\n")
                f_reference.write(f"{lookback.get('reference', 'None')}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "update":
        test = TestClassifyCite()
        test.setUp()
        test.update_output()
    else:
        unittest.main()
