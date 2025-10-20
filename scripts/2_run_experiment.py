import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
from tqdm import tqdm

# --- 1. Configuration and Setup ---

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")
genai.configure(api_key=api_key)

input_filepath = os.path.join('data', 'experiment_setup.csv')
output_filepath = os.path.join('data', 'results_raw.csv')

model = genai.GenerativeModel('gemini-2.5-flash')

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

print("Configuration loaded. Starting experiment...")

# --- 2. Load the Experiment DataFrame ---
try:
    df = pd.read_csv(input_filepath)
except FileNotFoundError:
    print(f"ERROR: Input file not found at {input_filepath}")
    print("Please run the '1_generate_experiment_file.py' script first.")
    exit()


# Explicitly cast the 'Gemini_Response' column to 'object' dtype
# This allows it to hold strings (the response text) without a warning.
df['Gemini_Response'] = df['Gemini_Response'].astype(object)

# Filter for rows that haven't been run yet
prompts_to_run = df[df['Gemini_Response'].isnull()]

if len(prompts_to_run) == 0:
    print("All prompts have already been run. Results are in 'results_raw.csv'.")
    exit()

print(f"Found {len(prompts_to_run)} prompts to run (out of {len(df)} total).")

# --- 3. Run the Experiment ---
for index, row in tqdm(prompts_to_run.iterrows(), total=len(prompts_to_run), desc="Querying Gemini API"):

    prompt = row['Full_Prompt']

    try:
        response = model.generate_content(
            prompt,
            safety_settings=safety_settings
        )

        # This line will no longer produce a warning
        df.loc[index, 'Gemini_Response'] = response.text

    except Exception as e:
        print(f"\n--- ERROR on Scenario_ID {row['Scenario_ID']} ---")
        print(f"Details: {e}")
        print("Saving partial results and stopping.")
        df.to_csv(output_filepath, index=False, encoding='utf-8')
        exit()

    # RATE LIMIT COMPLIANCE: 10 reqs/min = 6 seconds/req
    time.sleep(6)

# --- 4. Save Final Results ---
df.to_csv(output_filepath, index=False, encoding='utf-8')

print("\n--- Experiment Complete! ---")
print(f"All {len(df)} responses have been collected.")
print(f"Raw results saved to: {output_filepath}")