# *Stanford Law Review* Citation Tool

## Overview

The *SLR* Citation Tool is a Python-based tool designed to assist law journal editors with citechecking. It extracts citations from footnotes and exports them into a tabular format for cite-checking.

## Repository Structure

```
/
├── extract.py                       # Main script for running the tool
├── input/
│   └── ...                          # Place your author drafts here in .docx form
├── output/
│   └── ...                          # Output files will be generated here
├── py/
│   ├── ai_parser.py                 # AI parsing functionality
│   ├── citation.py                  # Citation data structures and types
│   ├── doc_reader.py                # Docx processing logic
│   ├── extract_citations.py         # Script to extract citations
│   ├── extract_text.py              # Script to extract body or footnote text
│   ├── source.py                    # Source management and disambiguation
│   └── tests/                       # Directory containing unit tests
├── ai_config.json                   # AI configuration file
├── requirements.txt                 # List of required Python packages
└── README.md                        # Readme (this file)
```

## Installation and Setup

Ensure you have the following installed:

- **Python 3.x**

- **pip** (Python package manager)

Install the required Python libraries using `pip`. Run the following command in your terminal:

```bash
pip install -r requirements.txt
```

You'll also need the `en_core_web_sm` model for **spaCy**:

```bash
python -m spacy download en_core_web_sm
```

---

## Usage Instructions

### Setup

1. Place your document (`.docx`) that contains the article draft into the
`input/` folder.
2. Ensure that `ai_config.json` is correctly set up (See *AI Configuration*
below).
3. Determine the number of author acknowledgment footnotes. The tool assumes
that acknowledgment footnotes are marked by symbols (e.g., †, *, **) and substantive footnotes are numbered starting from 1.


### Running the Script

The `extract.py` script provides three different modes to process the document. The main functionality is the cite-checking table generator, which . `body` and `footnotes` extraction are provided as auxiliary functionalities.

1. **Citation Extraction (main functionality):**

    Extract citations from footnotes into a cite-checking sheet (TSV format). This mode requires an AI subscription for either OpenAI or Vertex AI.

    ```basxh
    python extract.py citations input/YOUR_INPUT_FILE.docx
    ```

2. **Body Text Extraction:**

    Extract the body text of the document and output it to a text file:

    ```bash
    python extract.py body input/YOUR_INPUT_FILE.docx
    ```

3. **Footnotes Extraction:**

    Extract the footnotes from the document and output them to a text file:

    ```bash
    python extract.py footnotes input/YOUR_INPUT_FILE.docx
    ```



### Optional Flags

- **--ai_config_file**  
  Sets the JSON config file. The default is `ai_config.json`.

- **--output_folder**  
  Specify a custom output folder for saving results. The default is the `output/` folder.
  
- **--num_acknowledgment_footnotes**  
  Set the number of footnotes to skip if they contain author acknowledgments. The default is `1`.

- **--enable_markup**  
  Use this flag if you want citation formatting to be incorporated using markup (default is plain text).


An example of a run with all possible flags specified is as follows:

```bash
python extract.py citations input/YOUR_INPUT_FILE.docx --ai_config_file=ai_config.json --output_folder=output/ --num_acknowledgment_footnotes=0 --enable_markup
```

## Output

All results will be saved in the specified `--output_folder` or the default `output/` folder. The output files will be named based on the input document name and the extraction mode (e.g., `YOUR_INPUT_FILE_body.txt`, `YOUR_INPUT_FILE_footnotes.txt`, `YOUR_INPUT_FILE_citations.tsv`).

### Citation Cite-checking Sheet

The output of "citations" mode is a TSV table containing information regarding each citation:

* **Fn#**: The footnote number.
* **Cite#**: The sequential position of the citation within the footnote.
* **Footnote Text**: The full text of the footnote. The column is only filled for the first citation of the footnote.
* **Source Name**: An auto-generated name for the source cited. The program makes an effort to ensure a source will be named consistently across all citations that cite that source.
* **Warnings**: Any warnings associated with generating the citation information.

The following is an example of table output from a sample author draft containing a few errors.

| Fn# | Cite# | Footnote Text                                                                                                                                                                                                                             | Citation Text                                          | Source Name               | Warnings |
|-----|-------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------|------------------------------|----------|
| 1   | 1     | Waller Peanut Co. v. Lee Cty. Peanut Co., 209 S.W.2d 405 (Tex. Civ. App. 1948). In dicta, the Supreme Court has discussed harm to a plaintiff arising “because the supermarket had run out of [the plaintiff’s] favorite brand of peanut butter.” Muldrow v. City of St. Louis, 144 S. Ct. 967, 979. See also Ann Phuong, The Magical Spread: Peanut Butter Throughout History 29 (1998). | Waller Peanut Co. v. Lee Cty. Peanut Co., 209 S.W.2d 405 (Tex. Civ. App. 1948)      | Waller Peanut Co v Lee Cty Peanut Co             |          |
| 1   | 2     |                                                                                                                                                                                                                                           | Muldrow v. City of St. Louis, 144 S. Ct. 967, 979      | Muldrow v City of St Louis |          |
| 1   | 3     |                                                                                                                                                                                                                                           | Ann Phuong, The Magical Spread: Peanut Butter Throughout History 29 (1998) | Phuong                       |          |
| 2   | 1     | See Waller Peanut Co., 209 S.W.2d at 406.                                                                                                                                                                                                            | Waller Peanut Co., 209 S.W.2d at 406                             | Waller Peanut Co v Lee Cty Peanut Co             |          |
| 3   | 1     | Id. at 407 ("The fraud was consummated by appellants' obtaining possession of the peanuts . . . .").                                                                                                                                                                                                  | Id. at 407                | Waller Peanut Co v Lee Cty Peanut Co             |          |
| 4   | 1     | Although its legal reasoning was seen as slightly stale at the time, the case has recently been revived for its articulation of the principle of sine gelata non procedo.                                                                                    | -                                                     |                           |          |



## AI Configuration

The `citations` mode relies on AI to parse footnotes and extract citations. The tool supports two different platforms for AI integration: **Vertex AI** and **OpenAI**. It also supports a **Naive** option for debugging purposes. The platform and corresponding parameters are defined in the `ai_config.json` file.

The citation extraction task performs the best using a supervised fine-tuned generative AI model rather than an off-the-shelf model. While this means you likely need to fine-tune your own model, *SLR* is currently exploring ways to make our internal fine-tuned models more accessible to the public.

1. **Vertex AI**  
   This option uses Google's Vertex AI for citation extraction. You'll need to provide the endpoint for your model, along with other configuration parameters like system instructions and generation settings.

   **Sample JSON Configuration for Vertex AI:**
   ```json
   {
       "platform": "Vertex AI",
       "vertex_ai_endpoint": "projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/models/YOUR_MODEL_ENDPOINT_ID",
       "system_instruction": "Extract all legal citations from the following footnote with one citation per line.",
       "temperature": 0.01 
   }
   ```
   We recommend a low temperature setting to ensure deterministic behavior.

2. **OpenAI**  
   This option uses OpenAI's GPT models for parsing citations. You need to provide your OpenAI API key, model, and system instructions.

   **Sample JSON Configuration for OpenAI:**
   ```json
   {
       "platform": "OpenAI",
       "openai_api_key": "your-openai-api-key",
       "openai_model": "your-finetuned-model",
       "system_instruction": "Extract all legal citations from the following footnote with one citation per line.",
       "temperature": 0.01
   }
   ```

   We recommend a low temperature setting to ensure deterministic behavior.


3. **Naive**  
   We have included support for a "Naive" approach for debugging purposes. It will simply return the footnote text as-is without decomposition into separate citations.

   **Sample JSON Configuration for Naive:**
   ```json
   {
       "platform": "Naive"
   }
   ```

## Troubleshooting

1. **File Not Found Error**: Ensure that your input file exists in the correct path (`input/` folder by default).
2. **Missing Dependencies**: If any required Python libraries are missing, run `pip install -r requirements.txt` to install them.
3. **AI Issues**: Make sure your `ai_config.json` is correctly formatted and that your credentials are valid.

## Future Updates

Stay tuned for future updates and enhancements to the *SLR* Citation Tool!