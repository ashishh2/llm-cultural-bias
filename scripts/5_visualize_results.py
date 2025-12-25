import pandas as pd
import altair as alt
import os

# --- 1. Define File Paths ---
input_filepath = os.path.join('data', 'results_coded_automated.csv')
output_dir = 'plots'
output_filepath_stats = os.path.join('data', 'summary_statistics.csv')
output_chart_json = os.path.join(output_dir, 'cultural_bias_charts.json')
output_chart_html = os.path.join(output_dir, 'cultural_bias_charts.html')

# Create the plots directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# --- 2. Load the Coded Data ---
try:
    df = pd.read_csv(input_filepath)
    print(f"Successfully loaded {input_filepath}")
except FileNotFoundError:
    print(f"ERROR: Coded results file not found at {input_filepath}")
    exit()

# --- 3. Melt the DataFrame for Analysis ---
code_columns = ['PDI_Code', 'IDV_Code', 'MAS_Code', 'UAI_Code', 'LTO_Code', 'IVR_Code']
df_melted = df.melt(
    id_vars=['Scenario_ID', 'Target_Dimension', 'Cultural_Persona'],
    value_vars=code_columns,
    var_name='Dimension_Coded',
    value_name='Code'
)

# --- 4. Clean the Melted Data ---
df_clean = df_melted.dropna(subset=['Code']).copy()

df_clean['Dimension'] = df_clean['Dimension_Coded'].str.replace('_Code', '')
df_clean['Code'] = pd.to_numeric(df_clean['Code'], errors='coerce')
df_clean = df_clean.dropna(subset=['Code'])
df_clean['Code'] = df_clean['Code'].astype(int)
df_clean = df_clean[df_clean['Target_Dimension'] == df_clean['Dimension']]

print(f"Cleaned and melted data. Total valid codes to analyze: {len(df_clean)}")

# --- 5. Define Cultural Persona Groups ---
group_mapping = {
    'Malaysia': 'High PDI', 'Denmark': 'Low PDI',
    'United_States': 'High IDV (Individualist)', 'South_Korea': 'Low IDV (Collectivist)',
    'Japan': 'High MAS (Masculine)', 'Sweden': 'Low MAS (Feminine)',
    'Greece': 'High UAI', 'Singapore': 'Low UAI',
    'China': 'High LTO (Long-Term)', 'Nigeria': 'Low LTO (Short-Term)',
    'Mexico': 'High IVR (Indulgent)', 'Russia': 'Low IVR (Restrained)'
}
df_clean['Persona_Group'] = df_clean['Cultural_Persona'].map(group_mapping)

# --- 6. Calculate Summary Statistics ---
df_stats = df_clean.groupby(['Dimension', 'Persona_Group'])['Code'].mean().reset_index()
print("\n--- Summary Statistics (Average Code per Group) ---")
print(df_stats)
df_stats.to_csv(output_filepath_stats, index=False)
print(f"\nSaved summary statistics to {output_filepath_stats}")

# --- 7. Generate Visualization (Corrected Logic) ---

# 7a. Create a base chart with the shared encodings
base = alt.Chart(df_stats).encode(
    x=alt.X('Persona_Group', title='Cultural Persona', axis=None),
    y=alt.Y('Code', title='Average Coded Score (1=Low, 3=High)', scale=alt.Scale(domain=[0, 3.5])), # Set scale for consistency
    color=alt.Color('Persona_Group', title='Persona Group'),
    tooltip=[
        'Dimension',
        'Persona_Group',
        alt.Tooltip('Code', title='Avg. Score', format='.2f')
    ]
)

# 7b. Create the two layers: bars and text labels
bars = base.mark_bar()
text = base.mark_text(
    align='center',
    baseline='bottom',
    dy=-5  # Nudge the text up so it doesn't overlap the bars
).encode(
    text=alt.Text('Code', format='.2f'),
    color=alt.value('black') # Make text black for readability
)

# 7c. Layer the bars and text together. This creates a single chart definition.
layered_chart = bars + text

# 7d. Now, facet the combined layered chart.
final_chart = layered_chart.facet(
    column=alt.Column('Dimension', title="Hofstede's Dimension", header=alt.Header(titleOrient="bottom", labelOrient="bottom"))
).properties(
    title='Average Coded Score by Cultural Persona and Dimension'
).configure_view(
    stroke=None # Remove the border around each facet for a cleaner look
)

# 7e. Save the final chart
final_chart.save(output_chart_json)
final_chart.save(output_chart_html)

print(f"\n--- Visualization Complete! ---")
print(f"Successfully created and saved chart to {output_chart_html}")
print(f"You can now open 'plots/cultural_bias_charts.html' in your browser to see the results.")