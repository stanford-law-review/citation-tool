import os

import ai_parser
import source
from citation import Citation, CitationType
from doc_reader import Doc


def extract_citations(
    input_file,
    ai_config_file,
    num_acknowledgment_footnotes,
    enable_markup,
    output_folder,
):
    """
    Extracts citations from the footnotes of a Word document and outputs them in a tab-separated values (TSV) format.

    Parameters:
    - input_file (str): Path to the input Word document.
    - ai_config_file (str): Path to the AI configuration file used for parsing citations.
    - num_acknowledgment_footnotes (int): Number of acknowledgment footnotes to skip during extraction.
    - enable_markup (bool): Whether to include WordPress markup in the extraction.
    - output_folder (str): Folder where the output file will be saved.

    Raises:
    - FileNotFoundError: If the input file or AI configuration file does not exist.
    - RuntimeError: If an error occurs during citation extraction or file writing.
    """

    # Check if the input and AI config files exist
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")
    if not os.path.isfile(ai_config_file):
        raise FileNotFoundError(
            f"AI configuration file '{ai_config_file}' does not exist."
        )

    # Ensure the output folder exists, creating it if necessary
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    # Initialize an empty list to store Citation objects
    citations = []

    # Initialize the document object
    doc = Doc(input_file, num_acknowledgment_footnotes, enable_markup)

    try:
        # Extract citations from each footnote in the document
        for footnote in doc.numbered_footnotes():
            citations += ai_parser.get_footnote_citations(footnote, ai_config_file)

        # Assign sources for each citation and disambiguate source names
        source.assign_sources(citations)
        sources = [
            citation.source
            for citation in citations
            if citation.type is CitationType.LONG_FORM
        ]
        source.disambiguate_source_names(sources)

        # Generate the output filename based on the input filename
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_filename = os.path.join(output_folder, f"{base_name}_citations.tsv")

        # Write the extracted citations to a TSV file
        with open(output_filename, "w") as file:
            # Write the header row to the TSV file
            file.write(Citation.header_tsv_row())

            # Write each citation as a TSV row
            for citation in citations:
                file.write(citation.to_tsv_row())

        print(f"Successfully outputted to {output_filename}.")

    except Exception as e:
        # Raise any unexpected errors during processing
        raise RuntimeError(f"An error occurred while extracting citations: {e}")

    finally:
        # Ensure cleanup of resources
        doc.cleanup()
