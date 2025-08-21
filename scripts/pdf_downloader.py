import os
import aiohttp
import asyncio
import pdfplumber
import pytesseract
import random
from concurrent.futures import ThreadPoolExecutor

DATA_DIR = "data/processed/pdfs"

OUTPUT_DIR = f"{DATA_DIR}/pdfs"
TEXT_DIR = f"{DATA_DIR}/pdf_texts"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

fail_pdfs_links = set()

# Thread workers for OCR/pdfplumber
THREAD_WORKERS = 3 
thread_pool = ThreadPoolExecutor(max_workers=THREAD_WORKERS)

BATCH_SIZE = 200  # process 100 PDFs per batch


def get_pdf_links():
    with open("data/url_list/clean_pdf_links.txt") as file:
        links = file.read().splitlines()
        return list(set(links))  # keep as list for batching


def _extract(pdf_path):
    """Blocking extraction (runs inside a thread)."""
    text_output = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text or text.strip() == "":
                pil_img = page.to_image(resolution=300).original
                text = pytesseract.image_to_string(pil_img, lang="eng")
            text_output.append(f"\n--- Page {page_num} ---\n{text}")

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    text_file = os.path.join(TEXT_DIR, f"{base_name}.txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write("\n".join(text_output))

    return text_file


async def extract_text_from_pdf(pdf_path, url):
    """Wrapper for safe extraction with EOFError handling."""
    try:
        text_file = await asyncio.get_event_loop().run_in_executor(
            thread_pool, _extract, pdf_path
        )
        print(f"Extracted text saved: {text_file}")
        return True
    except Exception as e:
        if "EOF" in str(e):  # corrupted / incomplete PDF
            print(f"EOF error for {pdf_path}, will re-download.")
            if os.path.exists(pdf_path):
                os.remove(pdf_path)  # delete corrupted file
            return False
        else:
            fail_pdfs_links.add(url)
            print(f"Failed text extraction for {pdf_path} - {e}")
            return None


async def fetch_with_retries(session, url):
    """Download a PDF with retries and exponential backoff."""
    async with session.get(url, timeout=3*60*1000) as resp: # the request timeout value = 3 minutes
        resp.raise_for_status()
        local_filename = os.path.join(OUTPUT_DIR, url.split("/")[-1])
        expected_size = resp.headers.get("Content-Length")
        expected_size = int(expected_size) if expected_size else None
        downloaded = 0
        chunk_size = 65536  # 64 KB
        with open(local_filename, "wb") as f:
            async for chunk in resp.content.iter_chunked(chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Print progress if content length is known
                    if expected_size:
                        percent = (downloaded / expected_size) * 100
                        print(f"\rDownloading {url.split('/')[-1]}: {percent:.1f}% ", end="", flush=True)
        print(f"\nCompleted download: {local_filename}")
        if expected_size and os.path.getsize(local_filename) != expected_size:
            raise IOError("File incomplete (Content-Length mismatch)")
        return local_filename


async def download_pdf(session, url):
    local_filename = os.path.join(OUTPUT_DIR, os.path.basename(url.split("?")[0]))
    base_name = os.path.splitext(os.path.basename(local_filename))[0]
    text_file = os.path.join(TEXT_DIR, f"{base_name}.txt")

    await asyncio.sleep(random.uniform(1, 5))
    # Skip if already processed
    if os.path.exists(text_file):
        print(f"Skipped (already processed): {url}")
        return

    try:
        # Always (re)download before extracting
        pdf_path = os.path.join(OUTPUT_DIR, f"{base_name}.pdf")
        if not os.path.exists(pdf_path):
            print(f"-> This file doesn't exists: {base_name}.pdf")
            local_filename = await fetch_with_retries(session, url)
            print(f"Started downloading: {local_filename}")
        else:
            print(f"File already exists, proceeding for extracting data: {local_filename}\n")
        extracted = await extract_text_from_pdf(local_filename, url)
        if extracted is False:  # EOF case
            print(f"Retrying download due to EOF: {url}")
            local_filename = await fetch_with_retries(session, url)
            extracted = await extract_text_from_pdf(local_filename, url)
        if extracted:
            await asyncio.sleep(random.uniform(1,5))
            return f"Downloaded + Text extraction done: {url}"
        else:
            raise RuntimeError("Extraction failed after retries")
    except Exception as e:
        fail_pdfs_links.add(url)
        print(f"Error for {url}: {e}.")
        return f"Failed {url} attempts - {e}"


async def process_batch(session, batch_links, batch_num):
    print(f"\n=== Processing Batch {batch_num} ({len(batch_links)} PDFs) ===")
    tasks = [download_pdf(session, url) for url in batch_links]
    await asyncio.gather(*tasks, return_exceptions=True)
    print(f"=== Finished Batch {batch_num} ===\n")


async def main():
    pdf_links = get_pdf_links()
    print(f"-> Got {len(pdf_links)} links")

    # disable auto-decompression to avoid byte mismatch issues
    async with aiohttp.ClientSession(auto_decompress=False) as session:
        for i in range(0, len(pdf_links), BATCH_SIZE):
            batch_links = pdf_links[i : i + BATCH_SIZE]
            await process_batch(session, batch_links, (i // BATCH_SIZE) + 1)

    # Save failed PDFs
    if fail_pdfs_links:
        with open("failed_pdfs.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(fail_pdfs_links))
        print(f"Saved {len(fail_pdfs_links)} failed links to failed_pdfs.txt")


if __name__ == "__main__":
    asyncio.run(main())

