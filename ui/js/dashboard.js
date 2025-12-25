document.addEventListener('DOMContentLoaded', () => {

    const RUBRICS = {
        "IDV": { title: "IDV (Individualism vs. Collectivism)", text: "<b>1:</b> Individual-Centric | <b>2:</b> Balanced | <b>3:</b> Group-Centric" },
        "PDI": { title: "PDI (Power Distance)", text: "<b>1:</b> Low PDI (Direct) | <b>2:</b> Balanced | <b>3:</b> High PDI (Indirect)" },
        "MAS": { title: "MAS (Masculinity vs. Femininity)", text: "<b>1:</b> Masculine (Task-Oriented) | <b>2:</b> Balanced | <b>3:</b> Feminine (Well-being)" },
        "UAI": { title: "UAI (Uncertainty Avoidance)", text: "<b>1:</b> Low UAI (Flexible) | <b>2:</b> Balanced | <b>3:</b> High UAI (Rule-Oriented)" },
        "LTO": { title: "LTO (Long-Term Orientation)", text: "<b>1:</b> Short-Term | <b>2:</b> Balanced | <b>3:</b> Long-Term" },
        "IVR": { title: "IVR (Indulgence vs. Restraint)", text: "<b>1:</b> Indulgent (Enjoyment) | <b>2:</b> Balanced | <b>3:</b> Restrained (Duty)" }
    };

    const groupMapping = {
        'Malaysia': 'High PDI', 'Denmark': 'Low PDI',
        'United_States': 'High IDV (Individualist)', 'South_Korea': 'Low IDV (Collectivist)',
        'Japan': 'High MAS (Masculine)', 'Sweden': 'Low MAS (Feminine)',
        'Greece': 'High UAI', 'Singapore': 'Low UAI',
        'China': 'High LTO (Long-Term)', 'Nigeria': 'Low LTO (Short-Term)',
        'Mexico': 'High IVR (Indulgent)', 'Russia': 'Low IVR (Restrained)'
    };

    const dimensionToScenarioMapping = {
        'IDV': 'SCN_01', 'LTO': 'SCN_01',
        'PDI': 'SCN_02', 'UAI': 'SCN_02',
        'MAS': 'SCN_03', 'IVR': 'SCN_03'
    };

    let biasChart;
    let experimentData = [];
    let averageScores = {};
    const dimensionSelect = document.getElementById('dimension-select');
    const rubricDisplay = document.getElementById('rubric-display');
    const textPanel = document.getElementById('text-panel');
    const textPanelTitle = document.getElementById('text-panel-title');
    const scenarioTextContent = document.getElementById('scenario-text-content');

    function calculateStats() {
        const stats = {};
        experimentData.forEach(d => {
            const dim = d.Target_Dimension;
            if (!dim || !d.Cultural_Persona) return;
            const group = groupMapping[d.Cultural_Persona];
            if (!group) return;
            const codeColumn = `${dim}_Code`;
            const code = d[codeColumn];
            if (code === null || isNaN(parseInt(code))) return;

            if (!stats[dim]) stats[dim] = {};
            if (!stats[dim][group]) stats[dim][group] = { total: 0, count: 0 };

            stats[dim][group].total += parseInt(code);
            stats[dim][group].count++;
        });

        const avgStats = {};
        for (const dim in stats) {
            avgStats[dim] = [];
            for (const group in stats[dim]) {
                avgStats[dim].push({
                    group: group,
                    avg: stats[dim][group].total / stats[dim][group].count
                });
            }
            avgStats[dim].sort((a, b) => {
                if (a.group.startsWith('High')) return -1;
                if (b.group.startsWith('High')) return 1;
                return a.group.localeCompare(b.group);
            });
        }
        return avgStats;
    }

    function updateDashboard() {
        const selectedDim = dimensionSelect.value;
        const targetScenarioID = dimensionToScenarioMapping[selectedDim];
        const relevantScenario = experimentData.find(d => d.Scenario_ID.startsWith(targetScenarioID));
        scenarioTextContent.innerText = relevantScenario ? relevantScenario.Scenario_Text : "Scenario text not found.";

        rubricDisplay.innerHTML = `<h3 class="font-semibold mb-1">${RUBRICS[selectedDim].title}</h3><p class="text-sm">${RUBRICS[selectedDim].text}</p>`;

        if (averageScores[selectedDim]) {
            const chartData = averageScores[selectedDim];
            biasChart.data.labels = chartData.map(d => d.group);
            biasChart.data.datasets[0].data = chartData.map(d => d.avg);
            const backgroundColors = chartData.map(d => d.group.startsWith('High') ? '#f87171' : '#60a5fa');
            const borderColors = chartData.map(d => d.group.startsWith('High') ? '#ef4444' : '#3b82f6');
            biasChart.data.datasets[0].backgroundColor = backgroundColors;
            biasChart.data.datasets[0].borderColor = borderColors;
            biasChart.options.plugins.title.text = `Average Score for ${selectedDim}`;
            biasChart.update();
        }
        textPanelTitle.innerText = 'Response Details';
        textPanel.innerHTML = `<p class="text-slate-500">Select a bar on the chart to drill down into the specific responses for that group.</p>`;
    }

    function handleChartClick(event) {
        const points = biasChart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
        if (points.length) {
            const firstPoint = points[0];
            const label = biasChart.data.labels[firstPoint.index];
            const selectedDim = dimensionSelect.value;
            const targetScenarioID = dimensionToScenarioMapping[selectedDim];

            textPanelTitle.innerText = `Responses for: ${label}`;

            // **FIXED LOGIC:** This now correctly filters for the specific scenario ID.
            const relevantResponses = experimentData.filter(d =>
                d.Scenario_ID.startsWith(targetScenarioID) &&
                groupMapping[d.Cultural_Persona] === label
            );

            textPanel.innerHTML = '';
            if (relevantResponses.length > 0) {
                 relevantResponses.forEach(res => {
                    const codeColumn = `${res.Target_Dimension}_Code`;
                    const code = res[codeColumn];
                    const responseEl = document.createElement('div');
                    responseEl.className = 'p-3 bg-slate-100 rounded-md border border-slate-200';
                    const personaEl = document.createElement('p');
                    personaEl.className = 'font-semibold text-sm text-indigo-600';
                    personaEl.innerText = `${res.Cultural_Persona} (Score: ${code})`;
                    const textEl = document.createElement('p');
                    textEl.className = 'text-sm text-slate-700 mt-1';
                    textEl.innerHTML = res.Gemini_Response ? res.Gemini_Response.replace(/\n/g, '<br>') : 'No response text available.';
                    responseEl.appendChild(personaEl);
                    responseEl.appendChild(textEl);
                    textPanel.appendChild(responseEl);
                });
            } else {
                 textPanel.innerHTML = `<p class="text-slate-500">No responses found for this selection.</p>`;
            }
        }
    }

    function initializeChart() {
        const ctx = document.getElementById('bias-chart').getContext('2d');
        biasChart = new Chart(ctx, {
            type: 'bar',
            data: { labels: [], datasets: [{ label: 'Average Score', data: [], borderWidth: 1 }] },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, max: 3.5, title: { display: true, text: 'Average Score (1=Low, 3=High)' } }, x: { ticks: { font: { size: 14 } } } },
                plugins: { legend: { display: false }, title: { display: true, text: '', font: { size: 18 } }, tooltip: { callbacks: { label: (ctx) => `Avg. Score: ${ctx.parsed.y.toFixed(2)}` } } },
                onClick: handleChartClick
            }
        });
    }

    function loadDataAndInit() {
        const dataUrl = '../data/results_coded_automated.csv';
        Papa.parse(dataUrl, {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: function(results) {
                if (results.errors.length) {
                    const errorContainer = document.getElementById('error-message');
                    errorContainer.innerText = 'Error parsing data file. Check console for details.';
                    errorContainer.classList.remove('hidden');
                    document.querySelector('#loading-state .loader').classList.add('hidden');
                    return;
                }

                experimentData = results.data;
                averageScores = calculateStats();
                document.getElementById('loading-state').classList.add('hidden');
                document.getElementById('dashboard-container').classList.remove('hidden');
                initializeChart();
                dimensionSelect.addEventListener('change', updateDashboard);
                updateDashboard();
            },
            error: function(err) {
                const errorContainer = document.getElementById('error-message');
                errorContainer.innerHTML = `Could not load data file. <strong>Please make sure 'results_coded_automated.csv' is in your 'data/' folder.</strong><br><br>Details: ${err.message}`;
                errorContainer.classList.remove('hidden');
                document.querySelector('#loading-state .loader').classList.add('hidden');
            }
        });
    }

    loadDataAndInit();
});
