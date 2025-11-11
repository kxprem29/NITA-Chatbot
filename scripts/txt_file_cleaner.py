import os

def clean_files_in_directory(directory_path: str, lines_to_remove: list):
    """
    Iterates through all .txt files in a directory, removes specified lines,
    and overwrites the files with the cleaned content.
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

                # Filter out the unwanted lines
                cleaned_lines = [
                    line for line in lines
                    if line.strip() not in unwanted_lines
                ]

                # If the content has changed, write the cleaned content back to the file
                if len(cleaned_lines) < len(lines):
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

    # --- 2. Add the EXACT lines you want to remove here ---
    # The script will remove any line that perfectly matches one of these strings.
    # The matching is case-sensitive but ignores leading/trailing whitespace.
    lines_to_remove = [
        "Webmail", "MIS", "Login", "Old Website", "-", "font size", "decrease",
        "font size reset", "+", "increase", "default theme", "Dark mode",
        "National Institute of Technology Agartala", "राष्ट्रीय प्रौद्योगिकी संस्थान अगरतला",
        "Skip Navigation Links", "HOME", "ABOUT", "About NITA", "Facilities",
        "Strategic Plan 2020-2030", "Virtual Tour of NIT Agartala", "ADMINISTRATION",
        "Board of Governors", "The Senate Committee", "The Finance Committee",
        "Office of Director", "The Buildings and Works Committee", "Office of Registrar",
        "Office of Dean (Academic Affairs)", "Office of Dean(Planning & Development)",
        "Office of Dean(Students' Welfare)", "Office of Dean(Research & Consultancy)",
        "Office of Dean(Faculty Welfare)", "Office of Chairman (AR & IR)",
        "Chief Information Security Officer (CISO)", "Chief Vigilance Officer (CVO)",
        "Establishment Section", "Accounts Section", "Audit Section", "Purchase Section",
        "MIS Section", "Library Section", "Computing & ICT Unit", "Office of  Vehicle Section",
        "ACADEMICS", "Academic Calendar", "Academic Regulations", "UG Regulations (old)",
        "Regulations for M.tech Programme (2019)", "Regulations for M.tech Programme (Old)",
        "Regulations for Ph.D Programme (2018)", "Regulations for Ph.D Programme (Old)",
        "Admission", "UG Admission", "M.Tech Admission", "M.Sc Admission", "MCA Admission",
        "MBA Admission", "Ph.D Programme", "Visvesvaraya PhD Scheme", "DASA at NIT Agartala",
        "Prospectus", "First Year Syllabus", "B.Sc- B.Ed programme (4-Year ITEP)",
        "List of Holidays (July 2025 - June 2026)", "DEPARTMENT", "Bio Engineering",
        "Chemical Engineering", "Civil Engineering", "Computer Science and Engineering",
        "Electrical Engineering", "Electronics and Communication Engineering",
        "Electronics and Instrumentation Engineering", "Mechanical Engineering",
        "Production Engineering", "Management, Humanities & Social Sciences", "Physics",
        "Chemistry", "Mathematics", "STUDENT", "Center for Career Development",
        "Examination Section", "List of People", "Verification of Academic Credential",
        "DigiLocker", "SOP for acquiring Academic Documents", "Question Bank Link",
        "Hostel", "Office of the Chief Warden", "NITA Health Centre", "Sports at NIT Agartala",
        "Student Bodies and Clubs", "Student Discipline Manual", "Academic Bank of Credits (ABC)",
        "Anti-Ragging", "Study in India", "ALUMNI", "Message", "Chairman Alumni Affairs",
        "Alumni Database", "Alumni Portal", "Alumni Feedback Form", "NEWS EVENTS",
        "Newsletter of NIT Agartala", "Magazine \"UPSHIFT\" Edition 3",
        "Magazine \"UPSHIFT\" Edition 2", "Magazine \"UPSHIFT\" Edition 1", "Past Events",
        "Research", "Overview", "Project", "Sponsored Project", "Consultancy Project",
        "Patent", "Education/ Training", "Conference Organized", "Workshop/ Seminar Organized",
        "Research & Innovation Centre", "Documents", "Achievements", "LIBRARY",
        "E-Resource (Remote Access)", "OPAC", "One nation One Subscription (ONOS)",
        "Department Important Links", "Quick Links", "Skip Navigation Links.",
        "Jirania , West Tripura", "Pin - 799046", ": director@nita.ac.in, nita.director@gmail.com",
        ": (0381)2546630 & Fax:(0381)2546360", "Reports/Minutes", "NIRF", "ARIIA",
        "BOG Minutes", "BWC Minutes", "FC Minutes", "SENATE Minutes", "Annual Reports",
        "Annual Audited Report", "Other Links", "Institute Innovation Council & Startup",
        "Central Research Facility", "Disclaimer", "Holiday List", "Convocation",
        "GSTIN of NITA", "Space Technology Incubation Centre", "External links",
        "ICT Initiatives of MoE", "Ministry of Education", "JOSAA,", "CSAB", "DASA,",
        "ICCR", "CCMT", "CCMN", "National Career Service Portal", "BIS", "Contact",
        "How to Reach", "Telephone Directory", "Guest House", "RTI", "SC/ST/OBC Cell",
        "Internal Complaint Committee (ICC)", "Copyright. All rights reserved. © National Institute of Technology Agartala",
        "Designed by", "Mastersoft", "| Maintained by", "NIT Agartala",
        "Last updated on 20/08/2025", "Number of visitors on the website :"
    ]

    # --- 3. Run the cleaning function ---
    clean_files_in_directory(target_directory, lines_to_remove)