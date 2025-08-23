import json
import re
from urllib.parse import urlparse, unquote
import os

# --- You can customize this dictionary ---
ABBREVIATION_MAP = {
    "cse": "Computer Science Engineering",
    "ee": "Electrical Engineering",
    "mech": "Mechanical Engineering",
    "it": "Information Technology",
    "btech": "Bachelor of Technology",
    "mtech": "Master of Technology",
    "ug": "Undergraduate",
    "pg": "Postgraduate",
    "faq": "Frequently Asked Questions",
    "cs": "Computer Science",
    "che": "Chemical Engineering",
    "ch": "Chemical Engineering",
    "pe": "Production Engineering",
    "me": "Mechanical Engineering",
    "ce": "Civil Engineering",
    "be": "Biotechnology Engineering",
    "crf": "central research facility"
}
# --- Words to ignore in the final title ---
IGNORE_WORDS = ['cpanel', 'uploads', 'sites', 'default', 'files', 'content']
# -----------------------------------------

def generate_metadata_from_url(url, doc_id):
    """
    Analyzes the entire URL path to generate a plausible title, description, and keywords.
    """
    try:
        # Decode the URL path to handle spaces and special characters (e.g., %20)
        path = unquote(urlparse(url).path)
        
        # Replace common separators with spaces to extract all words from the full path
        clean_text = re.sub(r'[\W_]+', ' ', path)
        
        # Split into individual words
        raw_keywords = clean_text.lower().split()
        
        # Remove file extension and other irrelevant words
        keywords = [word for word in raw_keywords if word not in ['pdf', 'html', 'aspx', 'php']]
        
        # Expand abbreviations and build a clean title
        title_parts = []
        for word in keywords:
            # Check for abbreviations
            expanded = ABBREVIATION_MAP.get(word, word.capitalize())
            # Add to title if not in ignore list
            if word.lower() not in IGNORE_WORDS:
                title_parts.append(expanded)
        
        # Remove duplicates while preserving order for a cleaner title
        seen = set()
        title = ' '.join([x for x in title_parts if not (x in seen or seen.add(x))])

        # Generate a more context-aware description
        description = f"This document provides information regarding the {title}. Please refer to the document for specific details."
        # Add more specific descriptions if possible
        if "syllabus" in keywords:
            description = f"This is the syllabus document for the {title}. It likely includes course structures, subjects, and curriculum details."
        elif "admissions" in keywords:
            description = f"This document provides information regarding admissions for {title}. It may contain details on the application process, eligibility, and important dates."

        # Create the final JSON object
        metadata_object = {
            "id": f"pdf_{doc_id}",
            "url": url.strip(),
            "title": title,
            "description": description,
            "keywords": keywords
        }
        return metadata_object
        
    except Exception as e:
        print(f"Could not process URL: {url.strip()}. Error: {e}")
        return None

def process_url_file(input_file="pdf_links.txt", output_file="pdf_metadata4.json"):
    """
_    Reads a list of URLs from a file and writes generated metadata to an output file.
_    """
    print(f"Reading URLs from '{input_file}'...")
    try:
        with open(input_file, 'r') as f:
            urls = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found. Please create it and add your URLs.")
        return

    all_metadata = []
    for i, url in enumerate(urls):
        if url.strip(): # Ensure the line is not empty
            metadata = generate_metadata_from_url(url, i + 1)
            if metadata:
                all_metadata.append(metadata)

    print(f"Generated metadata for {len(all_metadata)} URLs.")
    
    with open(output_file, 'w') as f:
        json.dump(all_metadata, f, indent=4)
        
    print(f"Successfully saved all metadata to '{output_file}'")

if __name__ == "__main__":
    process_url_file()