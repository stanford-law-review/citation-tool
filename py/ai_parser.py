import re
from openai import OpenAI
import json

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, HarmCategory, HarmBlockThreshold

from citation import Citation

def ai_parse_citations(footnote, ai_config_file):
    if footnote == "":
        return ["-"]

    with open(ai_config_file, 'r') as file:
        config = json.load(file)

    if config["platform"] == "Vertex AI":
        model = GenerativeModel(config["vertex_ai_endpoint"],
                                system_instruction=config["system_instruction"],
                                safety_settings={
                                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.OFF,
                                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.OFF,
                                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.OFF,
                                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.OFF,
                                    HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY: HarmBlockThreshold.OFF,
                                    },
                                generation_config=GenerationConfig(temperature=config["temperature"]))
        response = model.generate_content(footnote)
        return response.text.split('\n')
    elif config["platform"] == "OpenAI":
        client = OpenAI(api_key=config["openai_api_key"])
        return client.chat.completions.create(
                model=config["openai_model"],
                  messages=[
                    {"role": "system", "content": config["system_instruction"]},
                    {"role": "user", "content": footnote},
                  ],
                  temperature=config["temperature"]
        ).choices[0].message.content.strip().split("\n")
    elif config["platform"] == "Naive":
        return [footnote]
    else:
        return []


def get_footnote_citations(footnote, ai_config_file):
    print(f"Decomposing footnote into citations: {footnote}")

    citations = []
    footnote_text = " ".join(footnote.split()[1:]) # Shave off footnote number from beginning
    citation_texts = ai_parse_citations(footnote_text, ai_config_file)
    footnote_num = footnote.split()[0]

    for citation_index, citation_text in enumerate(citation_texts):
        citations += [Citation(footnote_num, citation_num=citation_index + 1, text=citation_text)]

    citations[0].footnote_text = footnote_text
    return citations

