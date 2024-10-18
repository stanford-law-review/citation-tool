import spacy
import titlecase
import unidecode
import re
from citation import Citation, CitationType

# Load the spaCy NLP model
nlp = spacy.load("en_core_web_sm")

def preprocess(text):
    """
    Preprocesses text by removing symbols, non-breaking spaces, and special characters.
    
    Parameters:
    - text (str): Input text to preprocess.
    
    Returns:
    - str: Preprocessed text.
    """
    text = unidecode.unidecode(text)  # Convert to ASCII
    text = text.replace("&", "and")  # Replace problematic ampersand
    text = text.strip()  # Remove leading/trailing spaces
    return text

def postprocess(text):
    """
    Postprocesses text by converting punctuation to spaces, capitalizing, and formatting.
    
    Parameters:
    - text (str): Input text to postprocess.
    
    Returns:
    - str: Postprocessed text.
    """
    text = re.sub(r'[ \.\/\\:"_]+', ' ', text)  # Replace problematic punctuation with spaces
    text = text.strip(' ')  # Remove leading and trailing spaces
    text = titlecase.titlecase(text)  # Apply title case formatting
    text = re.sub(r'\b(Infra|Supra)(?:\s+\w+)*\s+(Ii|Iii|Iv|v)\b',
                  lambda match: f"{match.group(0).rsplit(' ', 1)[0]} {match.group(2).upper()}", text)  # Capitalize Roman numerals I-V
    text = re.sub(r'(\b[A-Z]\b(?:\s+\b[A-Z]\b)+)', lambda match: match.group(0).replace(' ', ''), text)  # Join single-letter capitalized words
    return text

def unprocessed_name(text):
    """
    Extracts a name from preprocessed citation text using NLP.
    
    Parameters:
    - text (str): Citation text.
    
    Returns:
    - str: Extracted unprocessed name or identifier.
    """
    # Preprocess and tokenize the text
    doc = nlp(preprocess(text))

    # Identify the initial segment (before commas or semicolons)
    initial_segment = ""
    for token in doc:
        if token.text in ',:;':
            break
        initial_segment += token.text_with_ws.lower()

    # Check for case citations (e.g., 'v.' or 'in re')
    if " v " in initial_segment or " v. " in initial_segment or initial_segment.startswith("in re"):
        return initial_segment

    # Check for cross-references (infra/supra)
    if initial_segment.startswith("infra") or initial_segment.startswith("supra"):
        return initial_segment

    # For less clear cut cases, analyze the initial segment using NLP
    doc_segment = nlp(initial_segment.strip())
    full_name = ""
    
    # Look for an author name
    for ent in doc_segment.ents:
        if ent.label_ == "PERSON":
            full_name = ent.text
            break

    # Return the surname if found
    if full_name:
        surname = full_name.split()[-1]
        return surname

    # If no author name, return the text up to and including the first noun or proper noun
    for token in doc_segment:
        if token.pos_ in ["PROPN", "NOUN"]:
            return initial_segment[:token.idx + len(token.text)].strip()

    # If all else fails, return the entire initial segment
    return initial_segment


class Source:
    """
    Class representing a source.
    """
    def __init__(self, text):
        """
        Initializes a Source object.
        
        Parameters:
        - text (str): Full citation text.
        """
        self.name = postprocess(unprocessed_name(text))  # Extract and postprocess the name
        self.fullcite = text  # Store the full citation
        self.tokens = [preprocess(token.text.lower()) for token in nlp(text) if not token.is_punct and not token.is_stop]  # Tokenize citation text
        self.warnings = []  # Initialize an empty list for warnings


def disambiguate_source_names(sources):
    """
    Disambiguates source names by appending unique tokens or apostrophes to resolve duplicate names.
    
    Parameters:
    - sources (list): List of Source objects.
    """
    sources_by_name = {}

    # Group sources by name
    for source in sources:
        if source.name in sources_by_name:
            sources_by_name[source.name].append(source)
        else:
            sources_by_name[source.name] = [source]

    # Resolve name conflicts among similar sources that were initially assigned the same name
    for base_name, similar_sources in sources_by_name.items():
        if len(similar_sources) == 1:
            continue

        for source in similar_sources:
            doc = nlp(preprocess(source.fullcite))
            unique_token = None
            ignore_words = {"and", "or", "but", "of", "in", "the", "a", "an", "with"}  # Common words to ignore

            # Find a unique token that differentiates this source from others
            for token in source.tokens:
                unique = all(token not in other.tokens for other in similar_sources if other is not source)
                if unique:
                    unique_token = token
                    break

            # Append the unique token to disambiguate
            new_source_name = postprocess(f"{base_name} {unique_token}") if unique_token else base_name

            # If there aren't unique tokens to disambiguate the source, the source is likely a duplicate
            source.warnings.append("This source may be a duplicate.") if not unique_token else None

            # Regardless of potential duplicate status caused by author error, we still need 
            # to ensure sources as identified by the program have distinct names. We do this
            # by adding different numbers of apostrophes.
            while new_source_name in [s.name for s in sources]:
                new_source_name += "'"

            source.name = new_source_name


def matches(subsequence, sequence):
    """
    In order to see if an abbreviated short-form source name matches a full citation,
    checks if all words in a subsequence appear in order in a sequence.
    
    Parameters:
    - subsequence (str): Subsequence of words.
    - sequence (str): Full sequence of words.
    
    Returns:
    - bool: True if the subsequence matches the sequence, False otherwise.
    """
    subsequence_words = re.findall(r'\b\w+\b', subsequence.lower())
    sequence_words = re.findall(r'\b\w+\b', sequence.lower())

    index = 0
    for word in subsequence_words:
        try:
            index = sequence_words.index(word, index) + 1
        except ValueError:
            return False
    return True


def assign_sources(citations):
    """
    Assigns sources to citations based on their type and context.
    
    Parameters:
    - citations (list): List of Citation objects.
    """
    prev_source = None

    for citation in citations:
        if citation.type == CitationType.NO_CITE:
            continue

        # Assign source for long form citations
        if citation.type == CitationType.LONG_FORM:
            citation.source = Source(citation.text)
            prev_source = citation.source

        # Assign source for "id." citations (reference to previous source)
        elif citation.type == CitationType.ID:
            citation.source = prev_source

        # Handle "supra" references
        elif citation.type == CitationType.SUPRA:
            shortcite = citation.lookback["shortcite"]
            reference = citation.lookback.get("reference", "")

            matched = False
            for candidate in citations:
                if candidate.type != CitationType.LONG_FORM:
                    continue

                if reference.isdigit() and int(reference) == int(candidate.footnote_num):
                    if matches(shortcite, candidate.text):
                        citation.source = candidate.source
                        matched = True
                        break

            if not matched:
                citation.warnings.append("Couldn’t find original source for this supra citation.")

        # Handle "lookback 5" citations (reference to recent citations)
        elif citation.type == CitationType.LOOKBACK_5:
            shortcite = citation.lookback["shortcite"]

            matched = False
            for candidate in citations:
                if candidate.source and int(citation.footnote_num) - int(candidate.footnote_num) <= 5:
                    if matches(shortcite, candidate.source.fullcite):
                        citation.source = candidate.source
                        matched = True
                        break

            if not matched:
                citation.warnings.append("Identified this as a potential \"look five footnotes back\" citation but couldn't identify the original source.")

        prev_source = citation.source
