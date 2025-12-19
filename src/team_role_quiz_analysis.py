#!/usr/bin/env python3
import os
import sys
import logging
import json
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Any

import gspread
from google.oauth2.service_account import Credentials
import requests

from utils.prompts import build_individual_prompt_analysis, build_team_prompt_analysis


def _configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        )
    root.setLevel(level)


_configure_logging()
logger = logging.getLogger(__name__)


# -------------------------
# Configuration
# -------------------------

# Google Sheets
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "data/service_account.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_WORKSHEET_NAME = os.getenv("GOOGLE_WORKSHEET_NAME", "Form responses 1")

# Ollama (local LLM)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")  # e.g. "llama3" or "qwen2.5"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MAX_TOKENS = 1200
OUTPUT_MARKDOWN_FILE = os.getenv("OUTPUT_MARKDOWN_FILE", "team_role_report.md")

ANALYSIS_CACHE_FILE = os.getenv("ANALYSIS_CACHE_FILE", "data/analysis_cache.json")


Participant = Dict[str, Any]
TeamAnalysis = Dict[str, Any]


_OLLAMA_MODEL_VALIDATED = False


def get_gspread_client() -> gspread.Client:
    logger.info("Creating gspread client (service_account=%s)", GOOGLE_SERVICE_ACCOUNT_FILE)
    if not os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Google service account file not found: {GOOGLE_SERVICE_ACCOUNT_FILE}"
        )

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE, scopes=scopes
    )
    return gspread.authorize(creds)


def load_raw_responses() -> List[Participant]:
    """Load participants from responses_raw.json if it exists."""
    raw_path = os.getenv("RAW_RESPONSES_FILE", "data/responses_raw.json")
    logger.info("Loading raw responses (path=%s)", raw_path)
    if os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Assume the JSON structure matches the existing Participant dict
            logger.info("Loaded %d raw responses", len(data) if isinstance(data, list) else 0)
            return data
    logger.info("Raw responses file not found (path=%s)", raw_path)
    return []


def save_raw_responses(participants: List[Dict[str, Any]]) -> None:
    raw_path = os.getenv("RAW_RESPONSES_FILE", "data/responses_raw.json")
    try:
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(participants, f, ensure_ascii=False, indent=2)
        logger.info("Saved %d raw responses (path=%s)", len(participants), raw_path)
    except OSError:
        logger.exception("Failed to write raw responses cache (path=%s)", raw_path)


def fetch_responses() -> List[Participant]:
    """Fetch from Google Sheets and cache to responses_raw.json; fallback to local cache if needed."""
    if not GOOGLE_SHEET_ID:
        logger.info("GOOGLE_SHEET_ID is not set; falling back to local raw responses")
        return load_raw_responses()

    sheet_id = GOOGLE_SHEET_ID
    m = re.search(r"/spreadsheets/d/([^/]+)", sheet_id)
    if m:
        sheet_id = m.group(1)

    logger.info(
        "Fetching responses from Google Sheets (sheet_id=%s worksheet=%s)",
        sheet_id,
        GOOGLE_WORKSHEET_NAME,
    )
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet(GOOGLE_WORKSHEET_NAME)
        records = worksheet.get_all_records()
    except Exception:
        logger.exception("Failed to fetch from Google Sheets")
        allow_fallback = os.getenv("ALLOW_SHEETS_FALLBACK", "0").strip().lower() in {"1", "true", "yes"}
        if allow_fallback:
            logger.warning("ALLOW_SHEETS_FALLBACK enabled; falling back to local raw responses")
            return load_raw_responses()
        raise
    logger.info("Fetched %d rows from Google Sheets", len(records))

    participants: List[Participant] = []
    for row in records:
        name = row.get("Name") or row.get("Full Name") or row.get("Email Address")
        if not name:
            continue

        answers = {}
        for key, value in row.items():
            if key.lower() in ["timestamp", "name", "full name", "email address"] or value == "":
                continue
            answers[key] = value

        if len(answers) == 0:
            continue

        participants.append(
            {
                "raw_row": row,
                "name": name,
                "answers": answers,
            }
        )
    if participants:
        save_raw_responses(participants)
    return participants


def build_individual_prompt(participant: Participant) -> str:
    return build_individual_prompt_analysis(participant)


def _validate_ollama_model_exists() -> None:
    global _OLLAMA_MODEL_VALIDATED
    if _OLLAMA_MODEL_VALIDATED:
        return
    if not OLLAMA_MODEL:
        raise RuntimeError("OLLAMA_MODEL is not set.")

    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=30)
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to reach Ollama at {OLLAMA_BASE_URL}: {e}") from e

    if resp.status_code != 200:
        raise RuntimeError(
            f"Failed to query Ollama models at {OLLAMA_BASE_URL}/api/tags: {resp.status_code} {resp.text}"
        )

    data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
    models = data.get("models") if isinstance(data, dict) else None
    available = []
    if isinstance(models, list):
        for m in models:
            name = m.get("name") if isinstance(m, dict) else None
            if name:
                available.append(name)

    if OLLAMA_MODEL not in available:
        available_str = ", ".join(sorted(available)) if available else "<none>"
        raise RuntimeError(
            f"Ollama model '{OLLAMA_MODEL}' is not installed. "
            f"Install it with: ollama pull {OLLAMA_MODEL}. "
            f"Available models: {available_str}"
        )

    _OLLAMA_MODEL_VALIDATED = True


def analyze_participant_ollama(participant: Participant) -> Dict[str, Any]:
    _validate_ollama_model_exists()
    prompt = build_individual_prompt(participant)
    logger.info("Analyzing participant via Ollama (name=%s)", participant.get("name"))

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
            },
            timeout=120,
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Ollama HTTP error while analyzing {participant['name']}: {e}") from e

    if resp.status_code != 200:
        raise RuntimeError(
            f"Ollama returned status {resp.status_code} for {participant['name']}: {resp.text}"
        )

    data_json = resp.json()
    message = data_json.get("message") or {}
    text = (message.get("content") or "").strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(text[start : end + 1])
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Failed to parse JSON response for {participant['name']}: {text}"
                ) from e
        else:
            raise RuntimeError(
                f"Failed to parse JSON response for {participant['name']}: {text}"
            )

    return data


def build_team_prompt(individual_results: List[Dict[str, Any]]) -> str:
    return build_team_prompt_analysis(individual_results)


def analyze_team_ollama(individual_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    _validate_ollama_model_exists()
    prompt = build_team_prompt(individual_results)
    logger.info("Analyzing team via Ollama (n_participants=%d)", len(individual_results))

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
            },
            timeout=180,
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Ollama HTTP error during team analysis: {e}") from e

    if resp.status_code != 200:
        raise RuntimeError(
            f"Ollama returned status {resp.status_code} for team analysis: {resp.text}"
        )

    data_json = resp.json()
    message = data_json.get("message") or {}
    text = (message.get("content") or "").strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(text[start : end + 1])
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Failed to parse JSON response for team analysis: {text}"
                ) from e
        else:
            raise RuntimeError(
                f"Failed to parse JSON response for team analysis: {text}"
            )

    return data


def generate_markdown(
    individual_results: List[Dict[str, Any]], team_analysis: Dict[str, Any]
) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines: List[str] = []
    lines.append(f"# Team Role Discovery Report")
    lines.append("")
    lines.append(f"_Generated on {now}_")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Individual Results")
    lines.append("")

    for person in individual_results:
        name = person.get("name", "Unknown")
        primary = person.get("primary_role", "N/A")
        secondary = person.get("secondary_role", "").strip()
        role_fit = person.get("role_fit_explanation", "").strip()
        unique_strengths = person.get("unique_strengths", "").strip()
        ideal_position = person.get("ideal_team_position", "").strip()
        surprise = person.get("surprise_insight", "").strip()

        # Backward compatibility (older prompt schema)
        if not role_fit:
            role_fit = person.get("insights", "").strip()
        if not ideal_position:
            ideal_position = person.get("ideal_team_role", "").strip()

        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"- **Primary role:** {primary}")
        if secondary:
            lines.append(f"- **Secondary role:** {secondary}")
        lines.append("")
        if role_fit:
            lines.append("**Why this role**")
            lines.append("")
            lines.append(role_fit)
            lines.append("")
        if unique_strengths:
            lines.append("**Unique strengths**")
            lines.append("")
            lines.append(unique_strengths)
            lines.append("")
        if ideal_position:
            lines.append("**Ideal team position**")
            lines.append("")
            lines.append(ideal_position)
            lines.append("")
        if surprise:
            lines.append("**Surprise insight**")
            lines.append("")
            lines.append(surprise)
            lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Team Composition")
    lines.append("")
    role_counts = team_analysis.get("role_counts", {})
    total = sum(role_counts.values()) if isinstance(role_counts, dict) else 0

    if total > 0 and isinstance(role_counts, dict):
        lines.append("| Role | Count |")
        lines.append("|------|-------|")
        for role, count in role_counts.items():
            lines.append(f"| {role} | {count} |")
        lines.append("")
    else:
        lines.append("_No team composition data available._")
        lines.append("")

    strengths = team_analysis.get("team_strengths_and_risks", "").strip()
    gaps = team_analysis.get("role_gaps_or_overlaps", "").strip()
    mentorship = team_analysis.get("mentorship_recommendations") or []
    tips = team_analysis.get("collaboration_tips") or []

    lines.append("## Overall Team Insights")
    lines.append("")
    if strengths:
        lines.append("**Team strengths and risks**")
        lines.append("")
        lines.append(strengths)
        lines.append("")
    if gaps:
        lines.append("**Role gaps or overlaps**")
        lines.append("")
        lines.append(gaps)
        lines.append("")

    return "\n".join(lines)


def print_console_summary(
    individual_results: List[Dict[str, Any]], team_analysis: Dict[str, Any]
) -> None:
    print("=" * 70)
    print("TEAM ROLE DISCOVERY – SUMMARY")
    print("=" * 70)
    print()

    print("Individual primary roles:")
    for p in individual_results:
        print(f"- {p.get('name', 'Unknown')}: {p.get('primary_role', 'N/A')}")
    print()

    print("Team role counts:")
    role_counts = team_analysis.get("role_counts", {})
    if isinstance(role_counts, dict) and role_counts:
        for role, count in role_counts.items():
            print(f"- {role}: {count}")
    else:
        print("No role count data.")
    print()

    strengths = team_analysis.get("team_strengths_and_risks", "").strip()
    if strengths:
        print("Team strengths & risks:")
        print(strengths)
        print()

    gaps = team_analysis.get("role_gaps_or_overlaps", "").strip()
    if gaps:
        print("Role gaps / overlaps:")
        print(gaps)
        print()

    mentorship = team_analysis.get("mentorship_recommendations") or []
    if mentorship:
        print("Mentorship recommendations:")
        for m in mentorship:
            print(f"- {m}")
        print()

    tips = team_analysis.get("collaboration_tips") or []
    if tips:
        print("Collaboration tips:")
        for t in tips:
            print(f"- {t}")
        print()

    print("=" * 70)
    print(f"Full markdown report written to: {OUTPUT_MARKDOWN_FILE}")
    print("=" * 70)


def run_analysis_and_write_report() -> Dict[str, Any]:
    """Run the full analysis pipeline and write the markdown report.

    This function is safe to call from other Python entrypoints (e.g. Streamlit)
    because it raises exceptions instead of calling sys.exit().
    """
    logger.info("Starting team role quiz analysis (callable)")

    participants = fetch_responses()
    if not participants:
        raise RuntimeError("No valid participant responses found.")

    cache: Dict[str, Any] = {}
    try:
        if os.path.exists(ANALYSIS_CACHE_FILE):
            with open(ANALYSIS_CACHE_FILE, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                cache = json.loads(raw) if raw else {}
    except Exception:
        logger.exception("Failed to read analysis cache (path=%s)", ANALYSIS_CACHE_FILE)
        cache = {}

    if not isinstance(cache, dict):
        cache = {}
    cache.setdefault("individual", {})

    def _signature_for(p: Participant) -> str:
        answers = p.get("answers") or {}
        name = (p.get("name") or "").strip()
        stable = json.dumps(answers, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256((name + "|" + stable).encode("utf-8")).hexdigest()

    participant_signatures: Dict[str, str] = {}
    for p in participants:
        name = (p.get("name") or "Unknown").strip()
        participant_signatures[name] = _signature_for(p)

    team_signature = hashlib.sha256(
        json.dumps(sorted(participant_signatures.items()), ensure_ascii=False).encode("utf-8")
    ).hexdigest()

    if (
        cache.get("team_signature") == team_signature
        and os.path.exists(OUTPUT_MARKDOWN_FILE)
        and cache.get("last_output_markdown_file") == OUTPUT_MARKDOWN_FILE
    ):
        logger.info("No participant changes detected; reusing existing report (path=%s)", OUTPUT_MARKDOWN_FILE)
        with open(OUTPUT_MARKDOWN_FILE, "r", encoding="utf-8") as f:
            markdown = f.read()
        cached_individuals = cache.get("last_individual_results")
        cached_team = cache.get("last_team_analysis")
        return {
            "participants": participants,
            "individual_results": cached_individuals if isinstance(cached_individuals, list) else [],
            "team_analysis": cached_team if isinstance(cached_team, dict) else {},
            "markdown": markdown,
            "output_markdown_file": OUTPUT_MARKDOWN_FILE,
            "cache_hit": True,
        }

    if not OLLAMA_MODEL:
        raise RuntimeError("OLLAMA_MODEL is not set.")

    individual_results: List[Dict[str, Any]] = []
    for p in participants:
        name = p.get("name", "Unknown")
        sig = participant_signatures.get(name, "")
        cached = (cache.get("individual") or {}).get(name) if isinstance(cache.get("individual"), dict) else None
        cached_sig = cached.get("signature") if isinstance(cached, dict) else None
        cached_result = cached.get("result") if isinstance(cached, dict) else None

        if sig and cached_sig == sig and isinstance(cached_result, dict) and cached_result:
            logger.info("Reusing cached participant analysis (name=%s)", name)
            result = cached_result
        else:
            logger.info("Analyzing participant (name=%s)", name)
            result = analyze_participant_ollama(p)
            if isinstance(cache.get("individual"), dict) and sig:
                cache["individual"][name] = {"signature": sig, "result": result}

        if "name" not in result or not result["name"]:
            result["name"] = name
        individual_results.append(result)

    if not individual_results:
        raise RuntimeError("No participant analyses were successfully generated.")

    team_analysis = analyze_team_ollama(individual_results)
    markdown = generate_markdown(individual_results, team_analysis)

    logger.info("Writing markdown report (path=%s)", OUTPUT_MARKDOWN_FILE)
    with open(OUTPUT_MARKDOWN_FILE, "w", encoding="utf-8") as f:
        f.write(markdown)

    cache["team_signature"] = team_signature
    cache["last_output_markdown_file"] = OUTPUT_MARKDOWN_FILE
    cache["last_individual_results"] = individual_results
    cache["last_team_analysis"] = team_analysis
    try:
        os.makedirs(os.path.dirname(ANALYSIS_CACHE_FILE) or ".", exist_ok=True)
        with open(ANALYSIS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Failed to write analysis cache (path=%s)", ANALYSIS_CACHE_FILE)

    logger.info("Analysis complete (callable)")
    return {
        "participants": participants,
        "individual_results": individual_results,
        "team_analysis": team_analysis,
        "markdown": markdown,
        "output_markdown_file": OUTPUT_MARKDOWN_FILE,
        "cache_hit": False,
    }


def main() -> None:
    logger.info("Starting team role quiz analysis")
    try:
        participants = fetch_responses()
    except Exception as e:
        logger.exception("Error while reading participants")
        print(f"Error while reading Google Sheet: {e}", file=sys.stderr)
        sys.exit(1)

    if not participants:
        logger.info("No valid participant responses found")
        print("No valid participant responses found in the sheet.")
        sys.exit(0)

    # Data-only mode: if no OLLAMA_MODEL is set, just dump raw responses to JSON
    if not OLLAMA_MODEL:
        output_json = os.getenv("OUTPUT_JSON_FILE", "data/responses_raw.json")
        try:
            logger.info("OLLAMA_MODEL not set; writing raw responses (path=%s)", output_json)
            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(participants, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.exception("Failed to write JSON responses")
            print(f"Failed to write JSON responses file '{output_json}': {e}", file=sys.stderr)
            sys.exit(1)

        print(f"OLLAMA_MODEL not set. Skipped analysis and saved {len(participants)} responses to '{output_json}'.")
        sys.exit(0)

    try:
        for p in participants:
            name = p.get("name", "Unknown")
            print(f"Analyzing participant with Ollama: {name} ...")
        result = run_analysis_and_write_report()
    except Exception as e:
        logger.exception("Analysis failed")
        print(f"Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)

    print_console_summary(result["individual_results"], result["team_analysis"])


if __name__ == "__main__":
    main()
