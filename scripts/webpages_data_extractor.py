import asyncio
import aiohttp
import os
import re
from bs4 import BeautifulSoup

def read_urls_from_file(filepath: str) -> list:
    """
    Reads a list of URLs from a text file, one URL per line.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Read lines and strip any leading/trailing whitespace
            urls = [line.strip() for line in f if line.strip()]
        print(f"✅ Successfully read {len(urls)} URLs from '{filepath}'.")
        return urls
    except FileNotFoundError:
        print(f"❌ Error: The file '{filepath}' was not found.")
        return []
    except Exception as e:
        print(f"❌ An unexpected error occurred while reading the file: {e}")
        return []

def extract_main_content(html: str) -> str:
    """
    Extracts the main text content from a webpage's HTML, filtering out common noise.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Remove common noisy elements like scripts, styles, navigation, etc.
    for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
        element.decompose()

    # Try to find a specific main content tag for better accuracy
    main_content = soup.find('main') or soup.find('article') or soup.find(role='main')

    # If a main content tag is found, use it. Otherwise, fall back to the whole body.
    target_element = main_content if main_content else soup.body

    if not target_element:
        return "" # Return empty string if no body tag is found

    # Get text and clean it up for better readability
    text = target_element.get_text(separator='\n', strip=True)
    # Collapse multiple blank lines into a maximum of two
    return re.sub(r'\n\s*\n', '\n\n', text)

async def process_url(session: aiohttp.ClientSession, url: str, output_dir: str):
    """
    Asynchronously fetches a URL, extracts its content, and saves it to a file.
    """
    # Create a safe and valid filename from the URL
    filename = re.sub(r'[^a-zA-Z0-9_-]', '_', url) + '.txt'
    filepath = os.path.join(output_dir, filename)

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        async with session.get(url, timeout=20, headers=headers) as response:
            if response.status == 200 and 'text/html' in response.headers.get('content-type', ''):
                html = await response.text()
                content = extract_main_content(html)
                if content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Processed and saved: {url}")
                else:
                    print(f"⚠️ No content extracted from: {url}")
            else:
                print(f"❗️ Failed to fetch (Status: {response.status}): {url}")
    except Exception as e:
        print(f"❗️ Error processing {url}: {e}")

async def async_data_processor(urls: list, output_dir: str):
    """
    Main function to coordinate the asynchronous processing of all URLs.
    """
    print(f"\n--- Starting to asynchronously process {len(urls)} URLs ---")
    print(f"✅ Saving extracted text to the '{output_dir}' directory.")

    os.makedirs(output_dir, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        # Use a semaphore to limit concurrent requests to 50 to avoid overwhelming the server
        semaphore = asyncio.Semaphore(50)

        async def sem_task(url):
            async with semaphore:
                await process_url(session, url, output_dir)

        # Create and run all the tasks
        tasks = [sem_task(url) for url in urls]
        await asyncio.gather(*tasks)

    print(f"\n✅ All processing tasks are complete.")

# --- Get the input file from the user ---
input_file = input("Enter the path to your .txt file containing the URLs: ")

if not os.path.exists(input_file):
    print(f"❌ Error: Input file not found at '{input_file}'")
else:
    # --- Read URLs from the specified file ---
    urls_to_process = read_urls_from_file(input_file)

    if urls_to_process:
        # --- Define where to save the output files ---
        output_directory = "data/processed_webpages"

        # --- Run the asynchronous processor ---
        # Use await instead of asyncio.run() in environments like Colab that have a running event loop
        async_data_processor(urls_to_process, output_directory)