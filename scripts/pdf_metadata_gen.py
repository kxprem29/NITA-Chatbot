import json
import re
from urllib.parse import urlparse
import os

# --- You can customize this dictionary ---
# Add common abbreviations found in your URLs to improve the output
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
    "be": "Biotechnology Engineering"
}
# -----------------------------------------

def generate_metadata_from_url(url, doc_id):
    """
    Analyzes a URL string to generate a plausible title, description, and keywords.
    """
    try:
        # Parse the URL to get the path
        path = urlparse(url).path
        
        # Get the filename (e.g., 'btech_handbook_2025-26.pdf')
        filename = os.path.basename(path)
        
        # Clean the filename to extract keywords
        # Removes extension, replaces separators with spaces
        clean_name = re.sub(r'[\W_]+', ' ', filename.split('.')[0])
        
        # Split into individual words
        keywords = clean_name.split()
        
        # Expand abbreviations and capitalize for the title
        title_parts = [ABBREVIATION_MAP.get(word.lower(), word.capitalize()) for word in keywords]
        title = ' '.join(title_parts)

        # Generate a description based on keywords
        if "syllabus" in keywords:
            description = f"This document contains the syllabus for {title}. It likely includes course structures, subjects, and curriculum details for the specified program and year."
        elif "admissions" in keywords:
            description = f"This document provides information regarding admissions for {title}. It may contain details on the application process, eligibility criteria, and important dates."
        elif "handbook" in keywords:
            description = f"The official student or program handbook for {title}. It likely contains rules, regulations, and essential information."
        else:
            description = f"This document provides information regarding {title}. Please refer to the document for specific details."

        # Create the final JSON object
        metadata_object = {
            "id": f"pdf_{doc_id}",
            "url": url.strip(),
            "title": title,
            "description": description,
            "keywords": [word.lower() for word in keywords]
        }
        return metadata_object
        
    except Exception as e:
        print(f"Could not process URL: {url.strip()}. Error: {e}")
        return None

def process_url_file(input_file="pdf_links.txt", output_file="pdf_metadata2.json"):
    """
    Reads a list of URLs from a file and writes generated metadata to an output file.
    """
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