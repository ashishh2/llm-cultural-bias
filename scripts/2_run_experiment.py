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

experiment_filepath = os.path.join('data', 'experiment_dataset.csv')

model = genai.GenerativeModel('gemini-3-flash')
safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in
                   ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "HARM_CATEGORY_DANGEROUS_CONTENT"]]

print("Configuration loaded. Starting experiment...")

# --- 2. Load the Experiment DataFrame ---
try:
    df = pd.read_csv(experiment_filepath)
    print(f"Reading and updating existing experiment file: {experiment_filepath}")
except FileNotFoundError:
    print(f"ERROR: Experiment file not found at {experiment_filepath}")
    print("Please run '1_generate_targeted_dataset.py' first to create it.")
    exit()

df['Gemini_Response'] = df['Gemini_Response'].astype(str)
prompts_to_run = df[df['Gemini_Response'].isnull() | (df['Gemini_Response'].str.lower() == 'nan')]

if len(prompts_to_run) == 0:
    print("All prompts have already been run. No new responses to fetch.")
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
        # Store only the raw text response
        df.loc[index, 'Gemini_Response'] = response.text

    except Exception as e:
        print(f"\n--- ERROR on Scenario_ID {row['Scenario_ID']} ---")
        print(f"Details: {e}")
        print("Saving partial results and stopping.")
        df.to_csv(experiment_filepath, index=False, encoding='utf-8')
        exit()

    # Rate limit compliance (e.g., 10 requests per minute)
    time.sleep(6)

# --- 4. Save Final Raw Results ---
df.to_csv(experiment_filepath, index=False, encoding='utf-8')

print("\n--- Experiment Complete! ---")
print(f"All raw responses have been collected and saved.")
print(f"Updated experiment file is at: {experiment_filepath}")
print("This file is now ready for '3_automate_coding_with_reason.py'.")