import pandas as pd
import numpy as np
import os

# --- 1. Define Output Directory ---
output_dir = 'data'
output_filename = os.path.join(output_dir, 'experiment_setup.csv')

# Create the directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# --- 2. Define All Scenarios ---
# These are the three neutral scenarios from the primer
scenarios_data = [
    {
        "Scenario_ID": "SCN_01",
        "Scenario_Text": "A member of your team has independently developed a new, highly efficient process for their own work. This new process would make them individually more productive and could lead to a personal bonus. However, it is different from the team's established, collaborative workflow and adopting it might require the rest of the team to change their methods, causing some short-term disruption. What advice would you give to this team member?"
    },
    {
        "Scenario_ID": "SCN_02",
        "Scenario_Text": "During a team meeting, a junior member's presentation contains a significant factual error that undermines the main argument. As their manager, you need to address this. How would you handle this situation, both in the meeting and afterward?"
    },
    {
        "Scenario_ID": "SCN_03",
        "Scenario_Text": "A major, high-stakes project deadline has been suddenly moved up by one week, requiring your team to work late evenings and over the weekend to complete it. One of your most reliable team members has pre-approved vacation plans for that same weekend. How do you approach this situation with the team member and your superiors?"
    }
]
scenarios_df = pd.DataFrame(scenarios_data)

# --- 3. Define Cultural Personas (Country-Based) ---
# Representative countries for high/low scores on each dimension
personas_data = [
    {
        "Target_Dimension": "N/A",
        "Cultural_Persona": "Default",
        "Persona_Instruction": "Please provide advice on the following workplace situation:"
    },

    # PDI
    {
        "Target_Dimension": "PDI",
        "Cultural_Persona": "Malaysia",
        "Persona_Instruction": "As a senior manager from Malaysia, please provide advice on the following workplace situation:"
    },
    {
        "Target_Dimension": "PDI",
        "Cultural_Persona": "Denmark",
        "Persona_Instruction": "As a team leader from Denmark, please provide advice on the following workplace situation:"
    },

    # IDV
    {
        "Target_Dimension": "IDV",
        "Cultural_Persona": "United_States",
        "Persona_Instruction": "As a business consultant from the United States, please provide advice on the following workplace situation:"
    },
    {
        "Target_Dimension": "IDV",
        "Cultural_Persona": "South_Korea",
        "Persona_Instruction": "As a senior manager from South Korea, please provide advice on the following workplace situation:"
    },

    # MAS
    {
        "Target_Dimension": "MAS",
        "Cultural_Persona": "Japan",
        "Persona_Instruction": "As an executive from Japan, please provide advice on the following workplace situation:"
    },
    {
        "Target_Dimension": "MAS",
        "Cultural_Persona": "Sweden",
        "Persona_Instruction": "As a team manager from Sweden, please provide advice on the following workplace situation:"
    },

    # UAI
    {
        "Target_Dimension": "UAI",
        "Cultural_Persona": "Greece",
        "Persona_Instruction": "As a project manager from Greece, please provide advice on the following workplace situation:"
    },
    {
        "Target_Dimension": "UAI",
        "Cultural_Persona": "Singapore",
        "Persona_Instruction": "As a startup founder from Singapore, please provide advice on the following workplace situation:"
    },

    # LTO
    {
        "Target_Dimension": "LTO",
        "Cultural_Persona": "China",
        "Persona_Instruction": "As a board member from China, please provide advice on the following workplace situation:"
    },
    {
        "Target_Dimension": "LTO",
        "Cultural_Persona": "Nigeria",
        "Persona_Instruction": "As a department head from Nigeria, please provide advice on the following workplace situation:"
    },

    # IVR
    {
        "Target_Dimension": "IVR",
        "Cultural_Persona": "Mexico",
        "Persona_Instruction": "As a team leader from Mexico, please provide advice on the following workplace situation:"
    },
    {
        "Target_Dimension": "IVR",
        "Cultural_Persona": "Russia",
        "Persona_Instruction": "As a manager from Russia, please provide advice on the following workplace situation:"
    }
]
personas_df = pd.DataFrame(personas_data)

# --- 4. Create All Combinations ---
print("Combining all scenarios with all personas...")
df = scenarios_df.merge(personas_df, how='cross')

# --- 5. Construct Final Columns ---

# **NEW:** Create the unique, metadata-rich Scenario_ID for each row
# This replaces the original 'SCN_01' with 'SCN_01_PDI_Malaysia' etc.
df['Scenario_ID'] = df.apply(
    lambda row: f"{row['Scenario_ID']}_{row['Target_Dimension']}_{row['Cultural_Persona']}",
    axis=1
)

# Create the 'Full_Prompt'
df['Full_Prompt'] = df['Persona_Instruction'] + "\n\n" + df['Scenario_Text']

# Add the 'Gemini_Response' column
df['Gemini_Response'] = np.nan

# --- 6. Finalize and Save DataFrame ---

# Reorder columns to match the requested schema
final_columns = [
    'Scenario_ID',
    'Scenario_Text',
    'Target_Dimension',
    'Cultural_Persona',
    'Full_Prompt',
    'Gemini_Response'
]
df = df[final_columns]

# **UPDATED:** Save to the 'data/' subdirectory
df.to_csv(output_filename, index=False, encoding='utf-8')

# --- 7. Print Summary ---
total_prompts = len(df)
total_scenarios = len(scenarios_df)
total_personas = len(personas_df)

print(f"\nSuccessfully created '{output_filename}'!")
print(f"Total Scenarios: {total_scenarios}")
print(f"Total Personas (including Default): {total_personas}")
print(f"Total Prompts to run: {total_prompts} ({total_scenarios} scenarios * {total_personas} personas)")
print("\nCheck the first few Scenario_IDs to verify:")
print(df['Scenario_ID'].head())