import re
import os

def replace_faculty_url(match):
    """
    This function is called for each URL match found by re.sub.
    It reconstructs the URL into the desired new format.
    """
    # The regex is now set up to capture the optional 'www.', nEmpID, and nDeptID.
    # group(1) will be 'www.' or None.
    # group(2) will be the value of nEmpID (e.g., 'cagac')
    # group(3) will be the value of nDeptID (e.g., 'caasq')
    emp_id = match.group(2)
    dept_id = match.group(3)

    # Construct the new URL using the captured values and the fixed domain.
    # nID in the new URL is the value from nEmpID in the old one.
    new_url = f"https://www.nita.ac.in/Department/Department_FacultyProfile.aspx?nID={emp_id}&nDeptID={dept_id}"
    
    return new_url

def process_file(input_filepath, output_filepath):
    """
    Reads the input file, performs the URL replacements, 
    and writes the result to the output file.
    """
    try:
        # Open the source file and read its entire content.
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # This is the core of the script. The regex looks for the specific URL pattern.
        # It now handles an optional 'www.' in the domain.
        # - (www\.)?: Optionally matches 'www.'.
        # - nita\.ac\.in: Matches the domain literally. We escape the dot with a '\'.
        # - /Department/faculty\.aspx\?: Matches the path.
        # - nEmpID=([^&"']+): Captures the employee ID. It matches any character
        #   that is NOT an ampersand, double quote, or single quote. This prevents
        #   it from running into the next parameter or the end of a string.
        # - &: Matches the ampersand separator.
        # - nDeptID=([^&"']+): Captures the department ID with the same logic.
        url_pattern = re.compile(r'https://(www\.)?nita\.ac\.in/Department/faculty\.aspx\?nEmpID=([^&"\'\s]+)&nDeptID=([^&"\'\s]+)')

        # re.sub finds all occurrences of the pattern and replaces them
        # by calling the replace_faculty_url function for each match.
        updated_content = url_pattern.sub(replace_faculty_url, content)

        # Open the destination file and write the modified content.
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
            
        print(f"✅ Success! File processed and saved as '{output_filepath}'")
        print(f"   - Found and replaced {len(url_pattern.findall(content))} URLs.")

    except FileNotFoundError:
        print(f"❌ Error: The file '{input_filepath}' was not found.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("--- URL Replacement Script ---")
    print("This script will find URLs like 'https://nita.ac.in/Department/faculty.aspx?nEmpID=...'")
    print("and convert them to 'https://www.nita.ac.in/Department/Department_FacultyProfile.aspx?nID=...'\n")

    # Get the input file path from the user.
    input_file = input("Enter the path to your input .txt file: ")

    # Check if the input file exists before proceeding.
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found at '{input_file}'")
    else:
        # Create a default output filename based on the input filename.
        # e.g., if input is 'my_urls.txt', output will be 'my_urls_updated.txt'.
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_updated{ext}"
        
        print(f"The updated file will be saved as: '{output_file}'")
        
        # Run the main processing function.
        process_file(input_file, output_file)
