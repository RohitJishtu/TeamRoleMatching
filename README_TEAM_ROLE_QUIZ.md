# Team Role Discovery Quiz Analysis

This tool reads responses from a Google Form (linked to a Google Sheet), analyzes them using a local LLM via Ollama, and produces:

- Individual role insights and recommendations
- Team composition summary
- Mentorship recommendations
- Collaboration tips

## Setup

### 1. Google Form and Sheet

1. Create a Google Form with:
   - `Name` (Short answer, required)
   - The 8 multiple-choice questions from your spec.
2. In the **Responses** tab, click the Google Sheets icon and create a new spreadsheet.
3. Copy the spreadsheet ID from the URL (the long string between `/d/` and `/edit`).

### 2. Google API Credentials

1. In Google Cloud Console, enable **Google Sheets API** (and optionally **Drive API**).
2. Create a **Service account** and generate a **JSON key**.
3. Download it into this folder as `service_account.json`.
4. Share the Google Sheet with the service account's `client_email` as **Viewer**.

### 3. Ollama (local model)

1. Install **Ollama** from https://ollama.com (macOS / Linux / Windows).
2. Pull a model you like, for example:

   ```bash
   ollama pull llama3
   ```

3. Make sure the Ollama server is running (usually it starts automatically). It exposes an HTTP API on `http://localhost:11434` by default.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment

```bash
export GOOGLE_SERVICE_ACCOUNT_FILE="service_account.json"      # or full path
export GOOGLE_SHEET_ID="YOUR_SHEET_ID_HERE"
export GOOGLE_WORKSHEET_NAME="Form Responses 1"                # default form sheet name
export OUTPUT_MARKDOWN_FILE="team_role_report.md"              # optional
export OLLAMA_MODEL="llama3"                                  # or any model you pulled
# export OLLAMA_BASE_URL="http://localhost:11434"              # optional override
```

## Run

```bash
python team_role_quiz_analysis.py
```

The script will:

- Read responses from the Sheet
- Call Claude (Anthropic) for each participant
- Perform a team-level analysis
- Print a console summary
- Write a full report to `team_role_report.md`
