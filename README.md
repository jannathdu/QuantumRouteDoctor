# QuantumRoute Doctor

**Diagnostic and Research Framework for Fidelity-Aware Quantum Network Routing**

QuantumRoute Doctor is a Streamlit-based application for diagnosing quantum network link conditions, evaluating route quality, and recommending routes based on fidelity and network health. It also includes a research framework for comparing baseline, memory-aware, and temporal routing algorithms under controlled synthetic network scenarios.

## Features

### Interactive Application

- Quantum network visualization
- Link fidelity and noise monitoring
- Automatic fault detection and severity classification
- Route ranking and safe-route recommendations
- Network fault simulation and link restoration
- Diagnosis history
- Report export in CSV, TXT, and HTML formats
- Browser-based printing and PDF saving

### Research Framework

- Fidelity-constrained baseline routing
- Memory-aware routing with memory-adjusted fidelity
- Temporal routing with Age of Information (AoI) constraints
- Reproducible synthetic network generation
- Paired experiments using common random seeds
- Feasibility-rate and route-quality evaluation
- Wilson confidence intervals
- Exact McNemar tests for paired feasibility outcomes
- Global Holm-Bonferroni correction for multiple comparisons
- JSON and CSV research data exports

## Routing Algorithms

| Algorithm | Description |
|---|---|
| Baseline | Selects the highest-fidelity route that satisfies the minimum fidelity threshold. |
| Memory-aware | Evaluates routes using memory-adjusted fidelity while accounting for storage and decoherence effects. |
| Temporal | Considers predicted memory fidelity and link-state freshness, rejecting routes that violate the configured AoI or end-to-end fidelity constraints. |

The algorithms are evaluated under common network scenarios to support paired comparisons. Their behavior and feasibility depend on the network configuration and evaluation thresholds.

## Technology Stack

- Python 3.13
- Streamlit
- NetworkX
- NumPy
- Pandas
- Matplotlib
- Python `unittest`
- JSON and CSV for research data and reports

## Requirements

- Python 3.13 or a compatible Python environment
- Git
- Windows, macOS, or Linux
- A terminal with access to the project directory

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/jannathdu/QuantumRouteDoctor.git
cd QuantumRouteDoctor
```

Create and activate a virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If your virtual environment is already active, you do not need to create another one.

## Run the Application

Start the Streamlit application from the repository root:

```powershell
python -m streamlit run app.py
```

Streamlit will display the local application address in the terminal. Open that address in your browser.

The application provides an interactive environment for examining link conditions, diagnosing faults, comparing route quality, and generating reports.

## Research Experiment Configuration

The three-algorithm research framework uses synthetic quantum network scenarios.

| Parameter | Configuration |
|---|---|
| Network nodes | 10 |
| Network links | 15 |
| Random seeds | 100 to 199 |
| Number of seeds | 100 |
| AoI thresholds | 2, 4, 6, 8 |
| Minimum fidelity thresholds | 0.5, 0.6, 0.7, 0.8 |
| Evaluation time | 10.0 |
| Algorithms | Baseline, memory-aware, temporal |

The complete parameter sweep contains:

- 16 parameter combinations
- 100 paired scenarios per combination
- 3 algorithms per scenario

This produces **4,800 algorithm-level experiment records**.

### Experiment Reproduction

The research experiment function can be called from the repository root:

```python
from backend.core.three_algorithm_experiments import (
    run_three_algorithm_experiments,
)

records = run_three_algorithm_experiments(
    seeds=list(range(100, 200)),
    aoi_thresholds=[2.0, 4.0, 6.0, 8.0],
    minimum_fidelity_thresholds=[0.5, 0.6, 0.7, 0.8],
)

print("Experiment records:", len(records))
```

The expected number of records is 4,800.

The experiment function returns the records in memory. Use the project's statistics and export modules to summarize and save the results.

## Statistical Analysis

The research framework includes descriptive and paired statistical analysis.

### Descriptive statistics

The summary reports algorithm-level feasibility counts and rates, confidence intervals, and paired feasibility outcomes across the parameter combinations.

### Paired inference

For each parameter combination, the analysis compares all three algorithm pairs:

1. Baseline vs. memory-aware
2. Baseline vs. temporal
3. Memory-aware vs. temporal

The exact McNemar test evaluates paired binary feasibility outcomes. Holm-Bonferroni correction is applied globally across the 48 pairwise tests.

To regenerate the inference report from an existing summary file, run:

```powershell
python .\run_three_algorithm_inference.py
```

The runner expects the summary file at:

`results/research_reports/three_algorithm_aoi_fidelity_sensitivity/three_algorithm_summary.json`

It writes the statistical inference report to the same directory.

## Research Artifacts

The research output directory is:

`results/research_reports/three_algorithm_aoi_fidelity_sensitivity/`

The principal artifacts are:

| File | Purpose |
|---|---|
| `quantum_routing_experiments.json` | Algorithm-level experiment records |
| `three_algorithm_summary.json` | Descriptive statistics and paired comparisons |
| `three_algorithm_statistical_inference.json` | Exact McNemar tests and Holm-adjusted p-values |

The corresponding CSV export is also supported by the research export module. Generated output files may be subject to repository ignore rules.

## Testing

Run the complete test suite from the repository root:

```powershell
python -m unittest discover -s tests -v
```

To test the three-algorithm experiment and inference modules individually:

```powershell
python -m unittest discover -s tests -p "test_three_algorithm_experiments.py" -v
python -m unittest discover -s tests -p "test_three_algorithm_statistics.py" -v
python -m unittest discover -s tests -p "test_three_algorithm_inference.py" -v
```

The test suite covers routing behavior, input validation, reproducibility, paired comparisons, statistical calculations, and related API functionality.

## Research Limitations

- The reported experiments use synthetic network scenarios, not measurements from a deployed quantum network or real quantum hardware.
- Results depend on the network generator, fidelity model, decoherence assumptions, random seeds, and configured thresholds.
- Statistical significance does not, by itself, establish practical significance or generalization to other network settings.
- The three algorithms use different selection criteria. Their feasibility and route-quality metrics should be interpreted alongside their respective constraints.
- Further validation with additional network configurations, independently justified physical models, and, where available, experimental data is needed before making claims about real-world performance.

## Project Structure

```text
QuantumRouteDoctor/
├── app.py
├── main.py
├── requirements.txt
├── backend/
│   ├── api/
│   ├── core/
│   │   ├── fidelity_routing.py
│   │   ├── memory_aware_routing.py
│   │   ├── temporal_routing.py
│   │   ├── route_evaluation.py
│   │   ├── research_experiments.py
│   │   ├── research_scenarios.py
│   │   ├── research_statistics.py
│   │   ├── three_algorithm_experiments.py
│   │   ├── three_algorithm_statistics.py
│   │   └── three_algorithm_inference.py
│   └── models/
├── tests/
└── results/
    └── research_reports/
        └── three_algorithm_aoi_fidelity_sensitivity/
```

## License

Add the applicable license and attribution information before distributing the project publicly.
