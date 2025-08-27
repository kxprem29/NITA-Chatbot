import os

def clean_files_in_directory(directory_path: str, lines_to_remove: list):
    """
    Iterates through all .txt files in a directory. If a file is over 150 lines,
    it removes the first 126 lines. Then, it removes specified boilerplate lines
    from all files and overwrites them with the cleaned content.
    """
    print(f"--- Starting Cleanup Process for Directory: '{directory_path}' ---")
    
    # Create a set of the unwanted lines for faster checking.
    # We strip whitespace to make the matching more reliable.
    unwanted_lines = {line.strip() for line in lines_to_remove}
    
    # Check if the directory exists
    if not os.path.isdir(directory_path):
        print(f"❌ Error: Directory not found at '{directory_path}'")
        return

    cleaned_file_count = 0
    # Walk through all files in the specified directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory_path, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                original_line_count = len(lines)
                
                # --- New Logic: Check file size and remove the top 126 lines ---
                if original_line_count > 150:
                    print(f"    -> File '{filename}' has {original_line_count} lines. Removing top 126.")
                    lines = lines[126:] # Keep everything AFTER the 126th line

                # --- Existing Logic: Filter out specific unwanted lines ---
                cleaned_lines = [
                    line for line in lines 
                    if line.strip() not in unwanted_lines
                ]

                # If the content has changed, write the cleaned content back to the file
                if len(cleaned_lines) < original_line_count:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.writelines(cleaned_lines)
                    print(f"✅ Cleaned: {filename}")
                    cleaned_file_count += 1
                
            except Exception as e:
                print(f"❗️ Error processing file {filename}: {e}")
                
    if cleaned_file_count == 0:
        print("\nNo files needed cleaning or no matching lines were found.")
    else:
        print(f"\n✅ Cleanup complete. Cleaned a total of {cleaned_file_count} files.")


if __name__ == '__main__':
    # --- 1. Define the folder where your .txt files are located ---
    # This should match the 'output_directory' from your scraper script.
    target_directory = "data/processed_webpages"

    # --- 2. Define the specific footer/boilerplate lines to remove from all files ---
    # This runs AFTER the top 126 lines are removed from large files.
    lines_to_remove = [
        "Department Important Links",
        "Quick Links",
        "Skip Navigation Links.",
        "National Institute of Technology Agartala",
        "Jirania , West Tripura",
        "Pin - 799046",
        ": director@nita.ac.in, nita.director@gmail.com",
        ": (0381)2546630 & Fax:(0381)2546360",
        "Reports/Minutes",
        "NIRF",
        "ARIIA",
        "BOG Minutes",
        "BWC Minutes",
        "FC Minutes",
        "SENATE Minutes",
        "Annual Reports",
        "Annual Audited Report",
        "Other Links",
        "Institute Innovation Council & Startup",
        "Central Research Facility",
        "Disclaimer",
        "Holiday List",
        "Alumni",
        "Convocation",
        "GSTIN of NITA",
        "Space Technology Incubation Centre",
        "External links",
        "ICT Initiatives of MoE",
        "Ministry of Education",
        "JOSAA,",
        "CSAB",
        "DASA,",
        "ICCR",
        "Study in India",
        "CCMT",
        "CCMN",
        "National Career Service Portal",
        "BIS",
        "Contact",
        "How to Reach",
        "Telephone Directory",
        "Guest House",
        "RTI",
        "SC/ST/OBC Cell",
        "Internal Complaint Committee (ICC)",
        "Copyright. All rights reserved. © National Institute of Technology Agartala",
        "Designed by",
        "Mastersoft",
        "| Maintained by",
        "NIT Agartala",
        "Last updated on 20/08/2025",
        "Number of visitors on the website :"
    ]

    # --- 3. Run the cleaning function ---
    clean_files_in_directory(target_directory, lines_to_remove)
