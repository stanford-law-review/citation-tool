import re
from enum import Enum


class CitationType(Enum):
    """
    Enumeration for types of citations which are handled differently.
    """

    # "Long form" citation, the citation form *any* source
    # takes the first time the source is cited.
    LONG_FORM = 1

    # "Id." citation assumed to refer to the previously cited source.
    ID = 2

    # Short form citations that do not use a supra must have been cited
    # within the previous five footnotes, hence "Lookback 5."
    LOOKBACK_5 = 3

    # Short form citation that includes a supra reference to the source's
    # first citation. Not to be confused with cross-references.
    SUPRA = 4

    # If a footnote cites no sources, the program will create a
    # dummy citation with this citation type.
    NO_CITE = 5


# List of citation patterns and their corresponding types.
# This is a list of hardcoded patterns that represent how early-draft authors
# likely *intend* to cite rather than hardcoding actual legal citation rules.
# As a result, some of the decisions herein are somewhat arbitrary.
# For the brave, this is something which may be better suited for AI.
PATTERNS = [
    (r"^-?$", CitationType.NO_CITE),  # Dummy citation
    (r"^id\b", CitationType.ID),  # ID citation
    (
        r"^(?P<shortcite>[^()]+?)[, ]+supra.?( note (?P<reference>[^ ,]+|\. \. \.)([, ].*)?)?$",
        CitationType.SUPRA,
    ),  # Supra citation
    (
        r"^.+ \d+ (WL|LEXIS) \d+,? at [*n.\d\-, ]+ \(.+\d{4}\)",
        CitationType.LONG_FORM,
    ),  # LEXIS/WL full citation
    (
        r"^(?P<shortcite>.+?, ??\d+( [A-Z][^ ,]*| \d{1,2}[A-Z]{1,2})*)( \d+,?)?? at [*\d]",
        CitationType.LOOKBACK_5,
    ),  # Short case or journal citation
    (r"^(?P<shortcite>§.*)", CitationType.LOOKBACK_5),  # Short statute citation
    (r"^U\.S\. Const\.", CitationType.LONG_FORM),  # U.S. Constitution citation
    (
        r"^([^ ]{,25} )?(supra|infra)\b",
        CitationType.LONG_FORM,
    ),  # Internal cross-reference
    (
        r"^(?P<shortcite>[^,()]{,40}?)([, ]+(at)?( (sec\.|¶¶?|art\.|para\.)?[\d\-, ]+)*)?$",
        CitationType.LOOKBACK_5,
    ),  # Very short citation
]


def classify_cite(text):
    """
    Classifies a citation string into a CitationType using regular expressions.

    Parameters:
    - text (str): The citation text to be classified.

    Returns:
    - (CitationType, dict): A tuple where the first value is the citation type and the second is
                            a dictionary of matched groups, if any. The matched groups, produced during
                            the regular expression parsing, capture information such as the short form
                            of the source author or title and the footnote referenced in a supra clause.
    """
    text = re.sub(r"\s+", " ", text)  # Clean up whitespace
    lookback = {}
    citation_type = (
        CitationType.LONG_FORM
    )  # Default to LONG_FORM unless a match is found

    # Try matching the text with each pattern
    for pattern, candidate_type in PATTERNS:
        match = re.match(pattern, text.strip(), flags=re.IGNORECASE)
        if match:
            citation_type = candidate_type
            lookback = match.groupdict()  # Capture any named groups from the regex
            break

    return citation_type, lookback


class Citation:
    """
    Represents a single citation within a legal document footnote.

    Attributes:
    - footnote_num (int): The number of the footnote containing the citation.
    - citation_num (int): The number of the citation within the footnote.
    - text (str): The citation text.
    - footnote_text (str): The full text of the footnote (set externally).
    - warnings (list): A list of warnings or issues related to the citation.
    - source (Source): The source associated with the citation, if applicable.
    - type (CitationType): The type of citation determined by pattern matching.
    - lookback (dict): Dictionary of matched groups for citations requiring backward references.
    """

    def __init__(self, footnote_num, citation_num=0, text=""):
        self.footnote_num = footnote_num
        self.citation_num = citation_num
        self.text = text
        self.footnote_text = ""
        self.warnings = []
        self.source = (
            None  # Source will be assigned during the citation parsing process
        )

        # If the citation text is empty, this indicates no citations are present in the footnote
        if text == "":
            self.citation_num = 0
            self.lookback = {}
            self.type = None
        else:
            # Classify the citation type based on the provided text
            self.type, self.lookback = classify_cite(text)

        print(f"  Citation processed: {self.text}")

    def to_tsv_row(self):
        """
        Converts the citation into a tab-separated value (TSV) row format.

        Returns:
        - str: A TSV row containing the citation details.
        """
        # Append source-related warnings if this is a long-form citation
        warnings = self.warnings
        if self.type == CitationType.LONG_FORM and self.source:
            warnings += (
                self.source.warnings
            )  # Add source warnings only for long-form citations

        # Join warnings into a single string
        warnings_str = " ".join(warnings)

        # Return TSV row with or without a source name
        if self.source:
            return f"{self.footnote_num}\t{self.citation_num}\t{self.footnote_text}\t{self.text}\t{self.source.name}\t{warnings_str}\n"
        else:
            return f"{self.footnote_num}\t{self.citation_num}\t{self.footnote_text}\t{self.text}\t\t{warnings_str}\n"

    @staticmethod
    def header_tsv_row():
        """
        Returns the header row for the TSV file.

        Returns:
        - str: The TSV header row.
        """
        return "Fn#\tCite#\tFootnote Text\tCitation Text\tSource Name\tWarnings\n"
