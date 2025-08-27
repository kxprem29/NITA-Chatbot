import shutil
from google.colab import files

# --- 1. Define the folder you want to zip ---
# This should match the 'output_directory' from your script
folder_path = 'data/processed_webpages'

# --- 2. Define the name for your output zip file ---
output_filename = 'processed_webpages'

# --- 3. Create the zip file ---
print(f"Zipping the folder: {folder_path}...")
shutil.make_archive(output_filename, 'zip', folder_path)
print(f"✅ Successfully created {output_filename}.zip")

# --- 4. Trigger the download ---
print(f"Downloading {output_filename}.zip now...")
files.download(f'{output_filename}.zip')