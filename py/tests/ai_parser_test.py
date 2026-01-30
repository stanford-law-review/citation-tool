import os
import sys
import unittest

import unidecode

sys.path.append(os.path.abspath(".."))
from ai_parser import ai_parse_citations

# Sample usage: python3 ai_parser_test.py [update]


class TestAIParseCitations(unittest.TestCase):
    # This unit test does a basic sanity check on AI footnote parsing. Note
    # that unit tests are typically not used for generative AI outputs because
    # of non-deterministic behavior. Nevertheless, the test is included
    # since rather than serving as a stress test, it deals with sample inputs
    # that should almost always produce the correct result with a reasonably well-trained
    # model.

    def setUp(self):
        # Directory for test data
        self.test_data_dir = os.path.join(os.getcwd(), "test_data", "ai_parser_test")

        with open(
            os.path.join(self.test_data_dir, "ai_parser_test_input.txt"), "r"
        ) as f:
            self.test_cases = f.readlines()

        with open(
            os.path.join(self.test_data_dir, "ai_parser_test_output.txt"), "r"
        ) as f:
            self.expected_outputs = [line.rstrip() for line in f.read().split("\n\n")]

    def test_ai_parse_citations_function(self):
        errors = []

        for i, text in enumerate(self.test_cases):
            text = text.strip()
            expected_output = unidecode.unidecode(self.expected_outputs[i])
            result = unidecode.unidecode(
                "\n".join(ai_parse_citations(text, "../../ai_config.json"))
            )

            if result != expected_output:
                errors.append(
                    f"Expected '{expected_output}' but got '{result}' for input: {text}"
                )

        if errors:
            self.fail("\n".join(errors))

    def update_output(self):
        with open(
            os.path.join(self.test_data_dir, "ai_parser_test_output.txt"), "w"
        ) as f:
            for text in self.test_cases:
                text = text.strip()
                result = ai_parse(text)
                f.write(f"{result}\n\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "update":
        test = TestExtractFunction()
        test.setUp()
        test.update_output()
    else:
        unittest.main()
