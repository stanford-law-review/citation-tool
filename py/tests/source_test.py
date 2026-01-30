import os
import sys
import unittest

sys.path.append(os.path.abspath(".."))
from source import Source

# Sample usage: python3 source_test.py [update]


class TestSourceName(unittest.TestCase):
    # This unit test checks that the Source constructor generates logical
    # source names based on long form citations.

    def setUp(self):
        # Directory for test data
        self.test_data_dir = os.path.join(os.getcwd(), "test_data", "source_test")

        with open(os.path.join(self.test_data_dir, "source_test_input.txt"), "r") as f:
            self.test_cases = f.readlines()

        with open(os.path.join(self.test_data_dir, "source_test_output.txt"), "r") as f:
            self.expected_outputs = f.readlines()

    def test_source_constructor(self):
        errors = []

        for i, text in enumerate(self.test_cases):
            text = text.strip()
            expected_output = self.expected_outputs[i].strip()
            result = Source(text).name

            if result != expected_output:
                errors.append(
                    f"Expected '{expected_output}' but got '{result}' for input: {text}"
                )

        if errors:
            self.fail("\n".join(errors))

    def update_output(self):
        with open(os.path.join(self.test_data_dir, "source_test_output.txt"), "w") as f:
            for text in self.test_cases:
                text = text.strip()
                result = generate_source_name(text)
                f.write(f"{result}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "update":
        test = TestClassifyCite()
        test.setUp()
        test.update_output()
    else:
        unittest.main()
