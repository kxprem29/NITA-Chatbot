import os
import sys
import json
import pathlib
import google.generativeai as genai

# --- Configuration ---

def configure_gemini():
    """
    Configures the Gemini API with the API key from environment variables.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set your API key: export GEMINI_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-pro')
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        sys.exit(1)

# --- Core Logic ---

def create_prompt(text_content):
    """
    Creates a specific prompt for the LLM to convert text to JSON.
    """
    # This prompt is engineered to force JSON-only output.
    # You can customize the example structure to fit your needs.
    return f"""
    You are a silent data extraction bot. Your only task is to convert the
    provided unstructured text into a valid JSON object.
    
    Do not provide any explanation, preamble, or markdown formatting (like ```json).
    Only output the raw, valid JSON.

    EXAMPLE STRUCTURE:
    {{
      "summary": "A brief summary of the text.",
      "key_topics": ["topic1", "topic2"],
      "sentiment": "Positive/Negative/Neutral",
      "entities": [
        {{"name": "Entity Name", "type": "Person/Organization/Location"}}
      ]
    }}

    ---
    TEXT TO CONVERT:
    {text_content}
    ---
    """

def clean_llm_output(llm_response_text):
    """
    Cleans the LLM output to ensure it's valid JSON.
    """
    # Remove potential markdown fences
    cleaned_text = llm_response_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
    
    return cleaned_text.strip()

def main():
    """
    Main function to run the file conversion.
    """
    # 1. Check command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python convert_to_json.py <input_file.txt> <output_file.json>")
        sys.exit(1)

    input_path = pathlib.Path(sys.argv[1])
    output_path = pathlib.Path(sys.argv[2])

    # 2. Configure Gemini Model
    print("Configuring Gemini...")
    model = configure_gemini()

    # 3. Read Input File
    try:
        print(f"Reading text from {input_path}...")
        text_content = input_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # 4. Generate JSON from text
    try:
        print("Calling Gemini API... (this may take a moment)")
        prompt = create_prompt(text_content)
        response = model.generate_content(prompt)
        
        json_string = clean_llm_output(response.text)
        
        # 5. Parse the JSON string
        json_data = json.loads(json_string)

    except json.JSONDecodeError:
        print("\n--- ERROR ---")
        print("Error: The LLM output was not valid JSON.")
        print("Received output:")
        print(response.text)
        print("---------------")
        sys.exit(1)
    except Exception as e:
        print(f"Error during API call or JSON parsing: {e}")
        sys.exit(1)

    # 6. Write Output File
    try:
        print(f"Writing JSON to {output_path}...")
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        print("\nSuccess! Conversion complete.")
    
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()