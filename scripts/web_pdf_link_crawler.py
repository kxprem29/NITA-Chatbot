import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from collections import deque

def find_all_pdfs(start_url, max_depth=4):
    """
    Crawls a website to a specific depth to discover all PDF file links.
    """
    queue = deque([(start_url, 0)])
    visited_urls = {start_url}
    
    # This set will store only the PDF URLs we find
    pdf_urls = set()

    base_domain = urlparse(start_url).netloc.replace('www.', '')
    ignored_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.docx', '.xlsx', '.pptx', '.zip', '.rar')

    print(f"🚀 Starting PDF search on domain: {base_domain} with max depth: {max_depth}")

    while queue:
        current_url, current_depth = queue.popleft()
        print(f"[{current_depth}]-> Searching for links in: {current_url}")

        if current_depth >= max_depth:
            print("    -> Max depth reached. Not exploring further from this page.")
            continue

        try:
            time.sleep(0.2)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(current_url, timeout=10, headers=headers)
            response.raise_for_status()

            if 'text/html' not in response.headers.get('content-type', ''):
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            for a_tag in soup.find_all('a', href=True):
                href = a_tag.get('href').strip()
                if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
                    continue

                absolute_url = urljoin(current_url, href)
                parsed_url = urlparse(absolute_url)
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                if parsed_url.query:
                    clean_url += f"?{parsed_url.query}"

                link_domain = parsed_url.netloc.replace('www.', '')
                if link_domain == base_domain and clean_url not in visited_urls:
                    
                    # ### MODIFICATION IS HERE ###
                    # Check if the newly found link is a PDF
                    if clean_url.lower().endswith('.pdf'):
                        print(f"  ✅ Found PDF: {clean_url}")
                        pdf_urls.add(clean_url)
                        # Add to visited so we don't check it again, but don't add to queue
                        visited_urls.add(clean_url) 
                    
                    # If it's not a PDF and not another ignored file type, add it to the queue to explore
                    elif not clean_url.lower().endswith(ignored_extensions):
                        visited_urls.add(clean_url)
                        queue.append((clean_url, current_depth + 1))

        except requests.exceptions.RequestException as e:
            print(f"❗️ Could not fetch {current_url}: {e}")
        except Exception as e:
            print(f"❗️ An error occurred while processing {current_url}: {e}")

    print(f"\n✅ Crawl finished. Found {len(pdf_urls)} unique PDF links.")
    return pdf_urls

if __name__ == '__main__':
    NITA_HOMEPAGE = "https://www.nita.ac.in/"
    
    # Set your desired crawl depth here
    MAX_CRAWL_DEPTH = 4 
    
    all_pdf_links = find_all_pdfs(NITA_HOMEPAGE, max_depth=MAX_CRAWL_DEPTH)

    # Save the results to a file
    output_filename = "pdf_links.txt"
    with open(output_filename, "w") as f:
        for url in sorted(list(all_pdf_links)):
            f.write(f"{url}\n")
    
    print(f"A list of all discovered PDF links has been saved to {output_filename}")