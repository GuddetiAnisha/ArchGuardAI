# ArchGuardAI — Detailed Project Explanation

## 1. Project overview

ArchGuardAI is a Python application that helps a reviewer check whether a software architecture description provides evidence for a set of requirements. It reads the architecture document, examines requirements from a versioned catalogue, assigns a status to each requirement, and creates a report explaining the findings.

The main purpose is to make architecture reviews more organized and traceable. Instead of simply stating that a system is secure or compliant, the application shows what evidence it found, what is missing, and what a human reviewer should check next.

The repository uses **synthetic example requirements**, 

## 2. Why this project is useful

Architecture documents describe how software systems are designed: their components, data flows, interfaces, controls, and boundaries. Reviewing a document against many requirements manually can take time, and two reviewers may notice different details.

ArchGuardAI provides a consistent first-pass assessment. It is especially helpful for distinguishing three situations that are often confused: the document explicitly supports a requirement, the document explicitly contradicts it, or the document simply does not say enough to decide.

A finding based on documentation is **not proof that a control exists or works in the running system**. A qualified reviewer must still inspect the actual implementation and relevant evidence.

## 3. Example in simple language

Suppose a requirement says that communication between services must use encryption.

- If the document explicitly states that the communication uses an approved encrypted channel, the tool may mark the requirement **COMPLIANT** according to the configured evidence rules.
- If the document explicitly states that communication happens without encryption, the tool may mark it **NON_COMPLIANT**.
- If encryption is not discussed, the correct documentary finding is **NOT_ENOUGH_INFORMATION**, not an automatic failure.
- If the relevant communication is explicitly outside the described system scope, it may be **NOT_APPLICABLE**.

These examples illustrate the four labels; the actual program follows phrases defined in its requirement catalogue. A human still has to decide whether the supporting statements are true and sufficient.

## 4. How the architecture assessment works

The application follows this process:

1. **Read a document.** The user selects an included example, pastes an architecture description, or uploads a supported document.
2. **Normalize text.** The parser prepares the contents for analysis.
3. **Load requirements.** The application reads the versioned YAML catalogue, including criteria, evidence phrases, contradiction phrases, risks, and recommended actions.
4. **Retrieve relevant context.** TF-IDF-based retrieval can find passages related to a requirement, making the document easier to inspect.
5. **Apply evidence rules.** Deterministic checks look for explicit supporting phrases, contradictions, and applicability exclusions.
6. **Assign a status.** Each requirement receives one of the four classes explained below.
7. **Generate findings.** The report includes a requirement identifier, decision, evidence, explanation, risk, recommendation, confidence and human-review indication.
8. **Present results.** Streamlit shows counts, charts, and individual findings; reports can be exported as JSON.

A key design decision is that a retrieved passage is **context, not automatic proof**. If no configured evidence or contradiction rule is satisfied, a similar-sounding passage alone should not change the decision to compliant.

## 5. Understanding the four classifications

| Status | Meaning | Important distinction |
| --- | --- | --- |
| COMPLIANT | Explicit configured evidence supports the requirement | The documentation still needs real-world verification |
| NON_COMPLIANT | An explicit statement conflicts with the requirement | Missing text alone is not enough |
| NOT_ENOUGH_INFORMATION | The available description cannot establish the answer | An information gap is not a confirmed implementation failure |
| NOT_APPLICABLE | The document explicitly establishes that the requirement does not apply | Not inferred from absence of supporting evidence |

This separation is important because it reduces unsupported conclusions and makes a review easier to defend and reproduce.

## 6. Is this an ML project?

ArchGuardAI combines **natural language processing, statistical text retrieval, deterministic rules and optional LLM assistance**. It is not primarily a supervised machine-learning model trained to predict compliance from labelled examples.

Its TF-IDF retrieval converts words and documents into numerical representations and helps select relevant passages. This is a classical information-retrieval technique. The deterministic evaluator makes the main compliance decisions from configured textual evidence and contradictions.

The repository also includes optional code to request a grounded judgement from a local Ollama language model. That code should not be confused with the default Streamlit assessment: the current `app.py` calls the deterministic `assess()` workflow and does not expose an Ollama toggle.

## 7. Technologies used

| Technology | Role in this project |
| --- | --- |
| Python | Main implementation language |
| Streamlit | Browser-based user interface |
| scikit-learn / TF-IDF | Retrieval of text related to requirements |
| PyYAML | Loading requirement definitions from YAML |
| Pydantic | Validating structured requirement and result objects |
| pandas and Plotly | Tables, summaries and visualizations |
| requests / Ollama | Optional local LLM integration |
| pytest | Automated validation of code behavior |
| JSON | Storing or exchanging structured assessment results |

## 8. How findings are produced

The evaluator examines phrases provided by each requirement. Its logic prioritizes explicitly documented scope exclusions, then explicit contradictions, then positive evidence, and otherwise returns not enough information.

For example, a sentence saying that a control is *not* in place must not be treated as positive evidence simply because it contains the control's name. The implementation has basic negation handling for supporting phrase matches. This helps with simple examples but does not provide full human-level language understanding.

Each finding contains an explanation and suggested next action. The confidence shown is produced by the implemented rule logic; it should **not** be interpreted as a statistically calibrated probability that the system is actually compliant.

## 9. Evaluation and validation

ArchGuardAI includes scripts and reference-labelled synthetic scenarios for checking whether its predicted status matches an expected status.

Useful measurements include:

- **Precision:** Of the examples predicted as a particular class, how many were correctly classified?
- **Recall:** Of the reference examples belonging to a class, how many were found?
- **Macro F1:** A balanced summary of class performance that gives each class equal importance.
- **Confusion matrix:** A table showing which classes were predicted correctly and which were confused.
- **Cohen's kappa:** Agreement adjusted for agreement expected by chance.
- **False-positive rate:** Helps examine unsupported non-compliance predictions.

The README reports **15 passed** automated tests and perfect classification scores on an **eight-requirement, deliberately constructed four-class synthetic benchmark**. These results demonstrate the behavior of that controlled test case; they do not establish accuracy on unfamiliar production architectures, large real datasets, or proprietary requirements. They also should not be described as the accuracy of a newly trained ML model.

## 10. Main source files

| File or folder | Purpose |
| --- | --- |
| `app.py` | Streamlit interface and JSON report download |
| `archguard/parser.py` | Architecture document parsing and normalization |
| `archguard/catalogue.py` | Loading the versioned requirements |
| `archguard/retrieval.py` | Locating relevant architecture passages |
| `archguard/evaluator.py` | Evidence-based compliance decisions |
| `archguard/models.py` | Structured input, finding and report schemas |
| `archguard/llm.py` | Optional grounded Ollama judgement and validation |
| `archguard/neurosymbolic_mapper.py` | Research-metadata taxonomy and mapping extension |
| `requirements/synthetic_mars.yaml` | Synthetic example requirement catalogue |
| `examples/` | Sample architectures and reference labels |
| `scripts/assess.py` | Command-line assessment |
| `scripts/evaluate.py` | Comparison with reference assessments |
| `tests/` | Automated tests |
| `reports/` | Assessment result outputs |

## 11. How to run ArchGuardAI in VS Code on Windows

Install Python 3.12, Git, and Visual Studio Code. Open a PowerShell terminal and run:

```powershell
git clone https://github.com/GuddetiAnisha/ArchGuardAI.git
cd ArchGuardAI
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open **http://localhost:8501** in your browser.

For the easiest first experiment, choose **Example** and click **Run assessment**. The app reads `examples/sample_architecture.md`, checks it against `requirements/synthetic_mars.yaml`, and displays the findings. You can expand individual requirements and download the JSON assessment.

Other choices are **Paste text** and **Upload document**. Supported document formats include Markdown, text, JSON, and Mermaid.

### Run from the terminal without the dashboard

```powershell
.\.venv\Scripts\python.exe scripts/assess.py --document examples/sample_architecture.md --requirements requirements/synthetic_mars.yaml --output reports/sample_assessment.json
```

To compare the generated assessment with the included reference:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate.py --predictions reports/sample_assessment.json --reference examples/expert_reference.json
```

### Reproduce the four-class synthetic scenario

```powershell
.\.venv\Scripts\python.exe scripts/assess.py --document examples/four_class_architecture.md --requirements requirements/synthetic_mars.yaml --output reports/four_class_assessment.json
.\.venv\Scripts\python.exe scripts/evaluate.py --predictions reports/four_class_assessment.json --reference examples/four_class_reference.json
```

These commands use the bundled examples and do not require Ollama.

## 12. Optional local LLM integration

The repository contains code for requesting an additional evidence-grounded suggestion from a locally running Ollama model. The prompts tell the model to rely on supplied excerpts, not invent undocumented controls, and return structured JSON. Suggestions without a verifiable evidence quote are rejected for conclusive decisions, and explicit rule-detected contradictions are not overridden.

To use the Ollama module in a separate integration or experiment, install Ollama and an appropriate local model. However, the present Streamlit app uses the deterministic assessment path. Installing Ollama by itself will not change the dashboard's assessment behavior.

## 13. Neuro-symbolic research mapping extension

The file `archguard/neurosymbolic_mapper.py` is a separate research-support extension. It works with structured metadata for studies of neuro-symbolic AI: approaches combining neural techniques with symbolic knowledge or reasoning.

It can create descriptive taxonomies, identify sparsely represented tags, and compare the study metadata with user-supplied networking-standard concepts.

For example:

```python
import pandas as pd
from archguard.neurosymbolic_mapper import build_taxonomy, identify_research_gaps, map_standards

studies = pd.read_csv("examples/neurosymbolic_studies.csv")
standards = pd.read_csv("examples/networking_standards_map.csv")

print(build_taxonomy(studies))
print(identify_research_gaps(studies))
print(map_standards(studies, standards))
```

This module does not automatically search for research papers, verify the reliability of citations, or prove that an observed gap is a genuine gap in the scientific literature. Its findings depend on the metadata supplied.

## 14. Strengths and limitations

**Strengths:** traceable requirement identifiers, explicit evidence handling, a useful separation between contradictions and missing information, reproducible synthetic test scenarios, human-readable recommendations, automated tests, and a convenient browser interface.

**Limitations:** deterministic phrase rules can miss paraphrases and nuanced architecture decisions; document evidence cannot establish runtime implementation; confidence is not calibrated; the included evaluation set is small and intentionally designed; optional LLM outputs can be wrong; and the tool is not approved to assess confidential architecture data by default.

The system is therefore suitable for **assisted review and experimentation**, not automatic security approval or legal/regulatory compliance certification.

## 15. Possible future improvements

1. Compare TF-IDF retrieval with sentence embeddings, such as Sentence-BERT, on independently labelled examples.
2. Create a larger collection of realistic, diverse architecture descriptions and requirements.
3. Evaluate on held-out documents with multiple qualified human reviewers and measure disagreements.
4. Improve handling of negation, conditional language, conflicting statements, and requirement applicability.
5. Investigate a carefully integrated optional LLM-assisted workflow with grounded evidence checks.
6. Study confidence calibration, explanation usefulness, false positives, and reviewer time savings.
7. Add suitable security protections before handling sensitive real-world system descriptions.

## 16. Final summary

ArchGuardAI demonstrates how to turn a software architecture document and a requirement catalogue into structured, reviewable findings. Its current core is a combination of NLP-based retrieval and deterministic evidence checks, supported by a Streamlit interface and evaluation tools.

The most important idea is **evidence-based decision-making**: a system should not be declared non-compliant just because something was not documented, and a tool should not declare actual production compliance solely because a document contains the expected phrase.

For detailed implementation notes and reference commands, see [README.md](README.md).
