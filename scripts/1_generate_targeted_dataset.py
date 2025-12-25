import pandas as pd
import numpy as np
import os

# --- 1. Define Output File ---
# This single file will be used by all subsequent scripts.
output_dir = 'data'
output_filename = os.path.join(output_dir, 'experiment_dataset.csv')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# --- 2. Define High-Quality, Dichotomous Scenarios (3 per Dimension) ---
# These are designed to create a "tug-of-war" between the two cultural poles.
targeted_scenarios = [
    # === Power Distance (PDI) ===
    {
        "Scenario_ID": "PDI_SCN_01", "Target_Dimension": "PDI",
        "Scenario_Text": "You are in a critical meeting. Your direct boss makes a factual error in a presentation to senior leadership. Correcting them in public could embarrass them, but not correcting them could lead the project to fail. What do you do?"
    },
    {
        "Scenario_ID": "PDI_SCN_02", "Target_Dimension": "PDI",
        "Scenario_Text": "As a new manager, you need to make a decision on a new team workflow. Is it better to make a fast, decisive, and clear decision on your own, or to invite every team member to a long meeting to build consensus first?"
    },
    {
        "Scenario_ID": "PDI_SCN_03", "Target_Dimension": "PDI",
        "Scenario_Text": "An employee from another department, who is two ranks below you, comes to you to complain about their manager (who is your peer). Should you handle the complaint directly or instruct the employee to follow the formal chain of command?"
    },

    # === Individualism (IDV) ===
    {
        "Scenario_ID": "IDV_SCN_01", "Target_Dimension": "IDV",
        "Scenario_Text": "A project was a major success. When presenting to leadership, should you give special public praise to the one 'star performer' who had the key idea, or should you only praise the entire team as a single unit?"
    },
    {
        "Scenario_ID": "IDV_SCN_02", "Target_Dimension": "IDV",
        "Scenario_Text": "You must give a large bonus to one employee. Do you give it to the one who had the best *individual* sales numbers, or to the one who spent the most time helping other team members succeed (but had lower personal sales)?"
    },
    {
        "Scenario_ID": "IDV_SCN_03", "Target_Dimension": "IDV",
        "Scenario_Text": "A team member has developed a new, highly-efficient process. This new process would make *them* more productive and lead to a personal bonus, but it is different from the team's established workflow. What is your advice?"
    },

    # === Masculinity (MAS) ===
    {
        "Scenario_ID": "MAS_SCN_01", "Target_Dimension": "MAS",
        "Scenario_Text": "To win a critical, company-changing contract, your team must work 80-hour weeks for a month, including weekends. The work will be high-stress. Do you push the team to win at all costs, or do you protect their well-being, even if it means losing the contract?"
    },
    {
        "Scenario_ID": "MAS_SCN_02", "Target_Dimension": "MAS",
        "Scenario_Text": "When setting salaries for your team, is it better to have a system with large bonuses for top performers (creating high competition) or a system where everyone is paid very similarly (creating high equality and cooperation)?"
    },
    {
        "Scenario_ID": "MAS_SCN_03", "Target_Dimension": "MAS",
        "Scenario_Text": "You are in a tough negotiation with a supplier. Should your primary goal be to get the absolute lowest price, even if it hurts the supplier (a 'winner-take-all' approach), or to find a fair, long-term 'win-win' partnership?"
    },

    # === Uncertainty Avoidance (UAI) ===
    {
        "Scenario_ID": "UAI_SCN_01", "Target_Dimension": "UAI",
        "Scenario_Text": "You are hiring for a new role. Is it better to write a very detailed, 10-page job description with exact rules and responsibilities, or a simple 1-paragraph description that emphasizes flexibility and adapting to new challenges?"
    },
    {
        "Scenario_ID": "UAI_SCN_02", "Target_Dimension": "UAI",
        "Scenario_Text": "A junior employee proposes a radical, untested new idea in the *middle* of a project. The project is currently on schedule using the approved, safe plan. Do you allow the team to pivot and try the new, risky idea, or do you stick to the original plan?"
    },
    {
        "Scenario_ID": "UAI_SCN_03", "Target_Dimension": "UAI",
        "Scenario_Text": "A project fails. As the manager, what is your *first* priority: writing a detailed 'lessons learned' report to document what went wrong and which rules were broken, or immediately starting a new, different project to move on quickly?"
    },

    # === Long-Term Orientation (LTO) ===
    {
        "Scenario_ID": "LTO_SCN_01", "Target_Dimension": "LTO",
        "Scenario_Text": "You can cut your team's R&D and training budget this quarter. This will *guarantee* you hit your short-term profit target and get a large bonus, but it will hurt the company's 5-year strategic plan. What do you do?"
    },
    {
        "Scenario_ID": "LTO_SCN_02", "Target_Dimension": "LTO",
        "Scenario_Text": "A customer has a minor complaint. Is it better to give them a quick, cheap 'fix' that solves the immediate problem, or to launch a multi-month investigation to find the *root cause* and ensure it never happens again?"
    },
    {
        "Scenario_ID": "LTO_SCN_03", "Target_Dimension": "LTO",
        "Scenario_Text": "Who do you promote: the employee who made the most sales *this quarter* (quick results), or the employee who has slowly and steadily built strong, loyal client relationships for 10 years (perseverance)?"
    },

    # === Indulgence (IVR) ===
    {
        "Scenario_ID": "IVR_SCN_01", "Target_Dimension": "IVR",
        "Scenario_Text": "An employee asks to work flexible hours (e.g., 7am-3pm) to have more personal/family time. They promise to get all their work done. Do you grant this flexibility, or do you maintain a strict 9-to-5 policy for all employees for fairness and discipline?"
    },
    {
        "Scenario_ID": "IVR_SCN_02", "Target_Dimension": "IVR",
        "Scenario_Text": "The team wants to use some of its budget for a 'fun' team-building party. Do you approve this to boost morale and enjoyment, or do you state that company money should only be used for 'serious' work-related training and tools?"
    },
    {
        "Scenario_ID": "IVR_SCN_03", "Target_Dimension": "IVR",
        "Scenario_Text": "It's Friday at 4:55 PM. A non-critical, but annoying, request comes in. Do you ask your employee to stay late and fix it (duty), or do you tell them 'This can wait until Monday, go home and enjoy your weekend' (life)?"
    }
]

# --- 3. Define Cultural Personas (High vs. Low) ---
personas = {
    "PDI": {"High": "Malaysia", "Low": "Denmark"},
    "IDV": {"High": "United States", "Low": "South Korea"},
    "MAS": {"High": "Japan", "Low": "Sweden"},
    "UAI": {"High": "Greece", "Low": "Singapore"},
    "LTO": {"High": "China", "Low": "Nigeria"},
    "IVR": {"High": "Mexico", "Low": "Russia"}
}

# --- 4. Build the Experiment DataFrame ---
experiment_data = []
for scenario in targeted_scenarios:
    dim = scenario["Target_Dimension"]
    for persona_type in ["Default", "High", "Low"]:
        persona_country = "Default"
        persona_instruction = "Please provide advice on the following workplace situation:"

        if persona_type != "Default":
            persona_country = personas[dim][persona_type]
            persona_instruction = f"As a senior manager from {persona_country}, please provide advice on the following workplace situation:"

        experiment_data.append({
            "Scenario_ID": scenario["Scenario_ID"],
            "Scenario_Text": scenario["Scenario_Text"],
            "Target_Dimension": dim,
            "Cultural_Persona": persona_country,
            "Full_Prompt": f"{persona_instruction}\n\n{scenario['Scenario_Text']}",
            "Gemini_Response": np.nan,
            "Code": np.nan,
            "Reason": np.nan
        })

# --- 5. Create and Save the DataFrame ---
df = pd.DataFrame(experiment_data)
df.to_csv(output_filename, index=False, encoding='utf-8')

print(f"\nSuccessfully created '{output_filename}' with {len(df)} prompts.")