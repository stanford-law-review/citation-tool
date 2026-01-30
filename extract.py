import argparse
import os
import sys

sys.path.append(os.path.abspath("py"))
import extract_citations
import extract_text

# ------------------------------
# SLR Citation Tool: A Simple Article Draft Processing Tool for Law Journals
# © 2024 Kenny Chang (Executive Editor, Stanford Law Review Volume 77)
# All rights reserved.
# ------------------------------
# This script provides three main functionalities:
# 1. Body: Extracts body text.
# 2. Footnotes: Extracts footnotes.
# 3. Citations: Extracts citations into a tabular citechecking sheet.
#
# Example Usage:
#    python extract.py [body|footnotes|citations] input/INPUT_FILE.docx [--num_acknowledgment_footnotes=1] [--output_folder=output/] [--ai_config_file=ai_config.json] [--enable_markup]
#
# ------------------------------


def check_file_exists(file_path, description):
    """Helper function to ensure a file exists before proceeding."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"{description} file '{file_path}' does not exist.")


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="SLR Citation Tool: A Simple Article Draft Processing Tool for Law Journals"
    )

    # Modality argument: either body, footnotes, or citations
    parser.add_argument(
        "mode",
        choices=["body", "footnotes", "citations"],
        help="Choose the operation mode:\n"
        "'body' - Extract body text only.\n"
        "'footnotes' - Extract footnotes only.\n"
        "'citations' - Extract citations from footnotes into a TSV file.",
    )

    # Common argument: input file (Word document)
    parser.add_argument(
        "input_file", type=str, help="Path to the input Word document (.docx)"
    )

    # AI Config file (only for 'citations' mode)
    parser.add_argument(
        "--ai_config_file",
        type=str,
        default="ai_config.json",
        help="Path to the AI configuration file (default is 'ai_config.json'). "
        "Required for 'citations' mode.",
    )

    # Author acknowledgment footnote count
    parser.add_argument(
        "--num_acknowledgment_footnotes",
        type=int,
        default=1,
        help="Number of author acknowledgment footnotes to skip (default is 1).",
    )

    # Output folder
    parser.add_argument(
        "--output_folder",
        type=str,
        default="output",
        help="Output folder for the results (default is 'output').",
    )

    # Markup output option
    parser.add_argument(
        "--enable_markup",
        action="store_true",
        help="Optional: If present, extract citations in Wordpress markup format (default is plain text).",
    )

    # Parse the arguments provided in the command line
    args = parser.parse_args()

    # Check if the input file exists
    check_file_exists(args.input_file, "Input")

    # Ensure output folder exists, if not, create it
    if not os.path.isdir(args.output_folder):
        os.makedirs(args.output_folder)

    # MAIN FUNCTIONALITY: Execute based on the selected mode
    if args.mode in ["body", "footnotes"]:
        # For 'body' or 'footnotes' mode, call extract_text with appropriate parameters
        extract_type = "body" if args.mode == "body" else "footnotes"
        extract_text.extract_text(
            input_file=args.input_file,
            extract_type=extract_type,
            num_acknowledgment_footnotes=args.num_acknowledgment_footnotes,
            enable_markup=args.enable_markup,
            output_folder=args.output_folder,
        )

    elif args.mode == "citations":
        # For 'citations' mode, check if AI config file exists
        check_file_exists(args.ai_config_file, "AI configuration")

        # Extract citations from footnotes for cite-checking
        extract_citations.extract_citations(
            input_file=args.input_file,
            ai_config_file=args.ai_config_file,
            num_acknowledgment_footnotes=args.num_acknowledgment_footnotes,
            enable_markup=args.enable_markup,
            output_folder=args.output_folder,
        )


if __name__ == "__main__":
    main()
