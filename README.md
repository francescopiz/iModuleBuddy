# iModuleBuddy
A Hybrid AI-Based Academic Planning System

---

## Authors:
[![Research Paper](https://img.shields.io/badge/ResearchGate-Paper-blue)](https://www.researchgate.net/publication/395801729_iModuleBuddy_-A_Hybrid_AI-Based_Academic_Planning_System)  
**Authors:** Maja Spahic-Bogdanovic, Hans Friedrich Witschel, Daniele Porumboiu, Piermichele Rosati, Piero Canchari, Milan Kostic  
**Conference:** *HybridAIMS & CAI Workshops (co-located with CAiSE 2025)*  

---

## Overview
iModuleBuddy is a hybrid AI-based study planner that assists postgraduate students in creating personalized academic plans.
It integrates structured data from the ESCO ontology (European Skills, Competences, qualifications, and Occupations) with vector-based similarity search and Retrieval-Augmented Generation (RAG) powered by Large Language Models.

The system combines symbolic AI (ontologies & knowledge graphs) and sub-symbolic AI (LLMs + embeddings) to:
	
* Recommend courses aligned with students' professional experience and career goals
* Organize these courses into multi-semester study plans
* Generate career-focused, balanced or preference-based plans with natural language explanations

---

## System Architecture
The system follows a three-layer architecture:
1. **Data Layer**:
   * Stores structured and unstructured information (modules, ESCO skills, occupations, user profiles)
   * Neo4j hosts the knowledge graph linking occupations, skills, and FHNW courses
   * Supabase stores student data (personal information, preferences, etc.)
2. **Processing Layer**:
   * Computes semantic similarity between course learning outcomes and ESCO skill descriptions using mxbai-embed-large (via Ollama)
   * Implements the JobRanking algorithm, which evaluates a student's job history based on recency, duration, and job type
3. **Application Layer**:
   * Built with Streamlit (frontend + backend)
   * Orchestrates two AI agents:
     * careerAgent, which aligns the student's background with career-relevant courses
     * scheduleAgent, that organizes courses into feasible multi-semester and weekly study plans
   * Uses Claude 3.7 Sonnet (2025-02-19) via LlamaIndex for reasoning and plan generation

---

## Tech Stack  

| Component                | Technology                                                           |
|--------------------------|----------------------------------------------------------------------|
| **Frontend & Backend**   | Streamlit                                                            |
| **Framework**            | LlamaIndex                                                           |
| **LLM**                  | Claude 3.7 Sonnet (2025-02-19)                                       |
| **Embeddings Model**     | mxbai-embed-large (via Ollama)                                       |
| **Ontology**             | ESCO (European Skills, Competences, qualifications, and Occupations) |
| **Knowledge Graph**      | Neo4j                                                                |
| **Users Database**       | Supabase                                                             |
| **Programming Language** | Python 3.10+                                                         |

---

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- Git
- Neo4j Database (it's highly recommended to use Neo4j Aura for a managed cloud solution)
- Supabase Database (setup a new project on [Supabase](https://supabase.com/))
- Ollama (for embedding model)
- Anthropic API Key (for Claude LLM)

#### Neo4j Population [REQUIRED]
To populate the Neo4j database with the ESCO ontology and FHNW course data, please put yourself under the main repository and run:
```bash
python esco/graph.py
```

#### ESCO csv Generation [OPTIONAL/UNNECESSARY]
If you don't have the ESCO csv files, or if you want to update them, you can generate them by following the steps below.
To generate the ESCO csv files, please put yourself under the main repository and run:
```bash
python esco/esco.py
```

### 1. Clone the Repository  
```bash
git clone https://github.com/Piermuz7/iModuleBuddy.git
cd imodulebuddy
```

### 2. Create a Virtual Environment  
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### 3. Install Dependencies  
```bash
pip install -r requirements.txt
```

### 4. Create a `.streamlit`folder in the root directory and add the following files
- .streamlit/secrets.toml
```toml
SUPABASE_URL= '<YOUR_SUPABASE_URL>'
SUPABASE_KEY = '<YOUR_SUPABASE_KEY>'
NEO4J_URI = '<YOUR_NEO4J_URI>'
NEO4J_USERNAME = '<YOUR_NEO4J_USERNAME>'
NEO4J_PASSWORD = '<YOUR_NEO4J_PASSWORD>'
ANTHROPIC_KEY = '<YOUR_ANTHROPIC_API_KEY>'
```

### 5. Run Ollama locally
Follow the instructions on [Ollama's official website](https://ollama.com) to install and run Ollama on your local machine.

### 6. Run the Application  
```bash
streamlit run streamlit_app.py
```

---

## Usage
1. Open your web browser and navigate to `http://localhost:8501`.
2. Fill in your personal information, professional experience, and academic preferences.
3. Click on "Generate Study Plan" to receive a personalized academic plan along with explanations.
4. Explore different plan options by adjusting your preferences and regenerating the plan.
5. Save or export your study plan as needed.
---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details

---

## Citation
If you use iModuleBuddy in your research, please cite our paper:

Plain Text:
> Spahic-Bogdanovic, Maja & Witschel, Hans Friedrich & Porumboiu, Daniele & Rosati, Piermichele & Canchari, Piero & Kostic, Milan. (2025). iModuleBuddy -A Hybrid AI-Based Academic Planning System. 


BibTeX:
```
@inproceedings{inproceedings,
author = {Spahic-Bogdanovic, Maja and Witschel, Hans Friedrich and Porumboiu, Daniele and Rosati, Piermichele and Canchari, Piero and Kostic, Milan},
year = {2025},
month = {06},
pages = {},
title = {iModuleBuddy -A Hybrid AI-Based Academic Planning System}
}
```

---