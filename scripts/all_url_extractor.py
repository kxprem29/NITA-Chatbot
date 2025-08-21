import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from collections import deque
import re

def transform_faculty_url(url):
    """
    Checks if a URL matches the old faculty format and transforms it.
    If it doesn't match, it returns the original URL.
    """
    # This is the regex pattern from the previous script to find old faculty URLs.
    # It handles both 'www.' and non-'www.' versions.
    url_pattern = re.compile(r'https://(www\.)?nita\.ac\.in/Department/faculty\.aspx\?nEmpID=([^&"\'\s]+)&nDeptID=([^&"\'\s]+)')
    match = url_pattern.match(url)

    if match:
        # If the URL matches, we extract the IDs and build the new URL.
        emp_id = match.group(2)
        dept_id = match.group(3)
        new_url = f"https://www.nita.ac.in/Department/Department_FacultyProfile.aspx?nID={emp_id}&nDeptID={dept_id}"
        print(f"    -> Transformed faculty URL to: {new_url}")
        return new_url
    
    # If the URL doesn't match the pattern, return it unchanged.
    return url

def discover_links_with_depth(start_url, max_depth=4):
    """
    Crawls a website to a specific depth, transforming specific URLs on the fly.
    """
    # The queue stores tuples of (URL, current_depth)
    queue = deque([(start_url, 0)])
    
    # This set stores every unique URL string we've already decided to visit
    visited_urls = {start_url}
    
    # This set will store the final list of all URLs found (already transformed)
    all_discovered_urls = set()

    # Get a clean base domain to compare against (e.g., 'nita.ac.in')
    base_domain = urlparse(start_url).netloc.replace('www.', '')

    # Define a tuple of file extensions to ignore
    ignored_extensions = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.docx', '.xlsx', '.pptx', '.zip', '.rar')

    print(f"🚀 Starting crawl on domain: {base_domain} with max depth: {max_depth}")
    print("✅ Transforming faculty URLs in real-time.")
    print(f"ℹ️  Ignoring files ending in: {ignored_extensions}")

    while queue:
        current_url, current_depth = queue.popleft()
        all_discovered_urls.add(current_url)

        print(f"[{current_depth}]-> Crawling: {current_url}")

        # If we have reached the max depth, don't look for more links on this page
        if current_depth >= max_depth:
            print("    -> Max depth reached. Not exploring further from this page.")
            continue

        try:
            time.sleep(0.2) # A respectful delay between requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(current_url, timeout=10, headers=headers)
            response.raise_for_status()

            # Skip parsing if the content is not HTML
            if 'text/html' not in response.headers.get('content-type', ''):
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            for a_tag in soup.find_all('a', href=True):
                href = a_tag.get('href').strip()
                # Ignore empty, anchor, mail, or javascript links
                if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
                    continue

                absolute_url = urljoin(current_url, href)
                parsed_url = urlparse(absolute_url)

                # Rebuild the URL, keeping the essential query parameters
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                if parsed_url.query:
                    clean_url += f"?{parsed_url.query}"

                # *** INTEGRATION POINT ***
                # Here we call the function to transform the URL if it matches the pattern.
                final_url = transform_faculty_url(clean_url)

                # Check if the link is on the same domain and hasn't been seen before
                link_domain = urlparse(final_url).netloc.replace('www.', '')
                if link_domain == base_domain and final_url not in visited_urls:
                    visited_urls.add(final_url)
                    print(f"  [{current_depth + 1}] Discovered: {final_url}")

                    # Only add the URL to the queue if it's not a file
                    if not final_url.lower().endswith(ignored_extensions):
                        queue.append((final_url, current_depth + 1))
                    else:
                        all_discovered_urls.add(final_url) # Still record files
                        print(f"    -> It's a file. Recording, but not adding to crawl queue.")

        except requests.exceptions.RequestException as e:
            print(f"❗️ Could not fetch {current_url}: {e}")
        except Exception as e:
            print(f"❗️ An error occurred while processing {current_url}: {e}")

    print(f"\n✅ Crawl finished. Found {len(all_discovered_urls)} unique URLs.")
    return all_discovered_urls

if __name__ == '__main__':
    NITA_HOMEPAGE = "https://www.nita.ac.in/"
    
    # You can change the crawl depth here
    MAX_CRAWL_DEPTH = 4 
    
    all_site_urls = discover_links_with_depth(NITA_HOMEPAGE, max_depth=MAX_CRAWL_DEPTH)

    # Save the results to a file
    output_filename = "nita_discovered_urls_final.txt"
    with open(output_filename, "w", encoding='utf-8') as f:
        for url in sorted(list(all_site_urls)):
            f.write(f"{url}\n")
    
    print(f"All discovered and transformed URLs have been saved to {output_filename}")
