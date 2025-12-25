import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
from tqdm import tqdm
import json

# --- 1. Configuration ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file.")
genai.configure(api_key=api_key)

experiment_filepath = os.path.join('data', 'experiment_dataset.csv')
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. Define Rubrics for Meta-Analysis ---
BASE_PROMPT = """You are a research analyst. Your task is to classify a text based on a provided 3-point rubric.
Analyze the text and determine which of the three definitions it aligns with most closely.
Respond with a single JSON object containing two keys: "score" (an integer: 1, 2, or 3) and "reason" (a brief, one-sentence explanation for your choice)."""

RUBRICS = {
    "PDI": "Rubric (Power Distance): 1=Low PDI (challenges authority, prefers equality), 2=Balanced, 3=High PDI (respects hierarchy, follows chain of command).",
    "IDV": "Rubric (Individualism vs. Collectivism): 1=Individual-Centric (praises star performers, values individual reward), 2=Balanced, 3=Group-Centric (praises the team, values group harmony).",
    "MAS": "Rubric (Masculinity vs. Femininity): 1=Masculine (assertive, win-at-all-costs, competition-focused), 2=Balanced, 3=Feminine (cooperative, win-win, well-being-focused).",
    "UAI": "Rubric (Uncertainty Avoidance): 1=Low UAI (flexible, adaptable, embraces risk and new ideas), 2=Balanced, 3=High UAI (rule-oriented, sticks to the plan, avoids risk).",
    "LTO": "Rubric (Long-Term Orientation): 1=Short-Term (focus on immediate results, quarterly profits), 2=Balanced, 3=Long-Term (focus on future investment, root causes, perseverance).",
    "IVR": "Rubric (Indulgence vs. Restraint): 1=Indulgent (prioritizes personal enjoyment, fun, flexible life), 2=Balanced, 3=Restrained (prioritizes duty, social norms, strict policies)."
}

# --- 3. Load Data ---
try:
    df = pd.read_csv(experiment_filepath)
except FileNotFoundError:
    print(f"ERROR: File not found at {experiment_filepath}. Run previous scripts first.")
    exit()

# Filter for rows that need coding
df['Code'] = pd.to_numeric(df['Code'], errors='coerce')
rows_to_code = df[df['Code'].isnull() & df['Gemini_Response'].notna()]

if len(rows_to_code) == 0:
    print("All responses have already been coded.")
    exit()

print(f"Found {len(rows_to_code)} new responses to code.")

# --- 4. Run Automated Coding ---
for index, row in tqdm(rows_to_code.iterrows(), total=len(rows_to_code), desc="Automated Coding"):
    dimension = row['Target_Dimension']
    if dimension in RUBRICS:
        full_prompt = f"{BASE_PROMPT}\n\n{RUBRICS[dimension]}\n\nText to Classify:\n---\n{row['Gemini_Response']}"
        try:
            response = model.generate_content(full_prompt)
            json_str = response.text.strip().split('```json\n')[-1].split('```')[0]
            parsed_json = json.loads(json_str)

            df.loc[index, 'Code'] = int(parsed_json.get('score', 0))
            df.loc[index, 'Reason'] = parsed_json.get('reason', 'Parsing error.')
        except (json.JSONDecodeError, IndexError, ValueError, Exception) as e:
            print(f"\nError processing response for {row['Scenario_ID']}: {e}")
            df.loc[index, 'Reason'] = f"ERROR: {response.text}"

        time.sleep(6)

# --- 5. Save Final Coded Results ---
df.to_csv(experiment_filepath, index=False, encoding='utf-8')
print(f"\n--- Automated Coding Complete! ---")
print(f"Final coded results saved to: {experiment_filepath}")