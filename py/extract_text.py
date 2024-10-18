import os
from doc_reader import Doc

def extract_text(input_file, extract_type, num_acknowledgment_footnotes, enable_markup, output_folder):
    """
    Extracts either body text or footnotes from a Word document based on the specified type.

    Parameters:
    - input_file (str): Path to the input Word document.
    - extract_type (str): Type of text to extract. Options are 'body' or 'footnotes'.
    - num_acknowledgment_footnotes (int): Number of footnotes that are acknowledgments and should be skipped.
    - enable_markup (bool): Whether to include WordPress markup in the extraction.
    - output_folder (str): Folder where the output file will be saved.

    Raises:
    - ValueError: If the extract_type is invalid.
    - FileNotFoundError: If the input file does not exist.
    """

    # Check if the input file exists
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")

    # Ensure the output folder exists, creating it if necessary
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    # Initialize the document object
    doc = Doc(input_file, num_acknowledgment_footnotes, enable_markup)

    # Generate the output filename based on the input filename and extraction type
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_folder, f"{base_name}_{extract_type}.txt")

    try:
        # Handle extraction based on the specified type
        if extract_type == 'footnotes':
            # Extract numbered footnotes
            footnotes = doc.numbered_footnotes()
            with open(output_file, 'w') as f:
                for footnote in footnotes:
                    f.write(footnote + '\n')

        elif extract_type == 'body':
            # Extract the body text
            body = doc.body()
            with open(output_file, 'w') as f:
                f.write(body)

        else:
            # Raise an error if an invalid extract_type is provided
            raise ValueError(f"Invalid extract_type '{extract_type}'. Must be 'body' or 'footnotes'.")

    except Exception as e:
        # Raise any unexpected errors during processing
        raise RuntimeError(f"An error occurred while extracting {extract_type}: {e}")

    finally:
        # Perform any cleanup after extraction
        doc.cleanup()
