# Team Role Matching

Team Role Matching is a lightweight Python-based tool designed to help teams understand individual strengths and map people to suitable roles using a short quiz-based assessment. The project is intended for quick internal use in workshops, team meetings, or leadership sessions — without requiring deployment or complex infrastructure.

## 🚀 What This Project Does

- Collects quiz responses related to working style, strengths, and preferences
- Analyzes responses to identify dominant team roles
- Generates a structured role-matching summary for each participant
- Produces simple, human-readable reports to support team discussions

This tool is ideal for:
- Team-building sessions
- Role alignment workshops
- Engineering or product team retrospectives
- Quick experiments without deploying an app

---

## 📁 Repository Structure

```

├── app.py                         # Main entry point to run the role matching flow
├── team_role_quiz_analysis.py     # Core logic for quiz analysis and role mapping
├── .env.example                   # Env var template (copy to .env locally)
├── README_TEAM_ROLE_QUIZ.md       # Quiz-specific explanation and context
├── requirements.txt               # Python dependencies
├── data/                          # Local inputs (gitignored PII) + samples/
├── data/samples/                  # Anonymized demo fixtures (safe to commit)
├── data/service_account.example.json
├── src/                           # Core processing modules
├── utils/                         # Helper utilities
├── TASK_LEFT.txt                  # Open tasks and improvements
└── allfiles.txt                   # File index / reference

````

---

## 🧠 How It Works (High Level)

1. Participants answer a short quiz focused on:
   - Collaboration style
   - Decision making
   - Ownership and execution
   - Communication preferences

2. The responses are processed and scored against predefined role signals.

3. Each participant is mapped to one or more **team roles** (e.g., executor, planner, facilitator, problem-solver).

4. A summary report is generated to help teams:
   - Discuss strengths
   - Balance roles across the group
   - Identify gaps or overloads

---

## 🛠️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/RohitJishtu/TeamRoleMatching.git
cd TeamRoleMatching
````

### 2. (Optional) Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### Run the main application

```bash
python app.py
```

### Run quiz analysis directly

```bash
python team_role_quiz_analysis.py
```

Input data is expected in the `data/` directory.
Outputs and reports are generated locally in markdown or text format.

---

## 📄 Output

* Individual role summaries
* Team-level role distribution insights
* Example anonymized output: `data/samples/team_role_report.sample.md`

Generated reports and raw responses stay local (gitignored) so participant PII is not committed.

---

## 🧩 Design Philosophy

* **No deployment required**
* **Local-first execution**
* **Readable over complex**
* **Easy to modify and extend**

The goal is fast feedback and discussion, not production-grade scoring.

---

## 🔮 Future Improvements

Planned or possible extensions (see `TASK_LEFT.txt`):

* Better scoring calibration
* Visualization of team role distribution
* Web or notebook-based UI
* LLM-assisted interpretation of results
* Export to slides or dashboards

---

## 🤝 Contributing

This is an experimental and evolving project.
Contributions, suggestions, and refactors are welcome via issues or pull requests.

---

## 📜 License

This project is currently shared for internal and experimental use.
Add a license if you plan to open-source it more broadly.

```

---

If you want, I can also:
- **Tighten this for open-source visibility**
- **Add screenshots / examples**
- **Rewrite it for a hackathon or internal demo**
- **Add an “AI-powered” angle if you plan to extend it with LLMs**

Just tell me the direction 👍
```
