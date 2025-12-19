#!/usr/bin/env python3
import os
import sys
import logging
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from utils.prompts import build_individual_prompt_app, build_team_prompt_app
from src.team_role_quiz_analysis import run_analysis_and_write_report
from src.mentor_matching import suggest_mentor_for_role


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

GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "data/service_account.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_WORKSHEET_NAME = os.getenv("GOOGLE_WORKSHEET_NAME", "Form responses 1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OUTPUT_MARKDOWN_FILE = os.getenv("OUTPUT_MARKDOWN_FILE", "team_role_report.md")
OUTPUT_JSON_FILE = os.getenv("OUTPUT_JSON_FILE", "data/responses_raw.json")
MAX_TOKENS = 1200


Participant = Dict[str, Any]
TeamAnalysis = Dict[str, Any]


# -------------------------
# Data loading helpers (reuse from main script)
# -------------------------

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


def fetch_responses() -> List[Participant]:
    logger.info(
        "Fetching responses from Google Sheets (sheet_id=%s worksheet=%s)",
        GOOGLE_SHEET_ID,
        GOOGLE_WORKSHEET_NAME,
    )
    if not GOOGLE_SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID is not set.")
    client = get_gspread_client()
    sheet = client.open_by_key(GOOGLE_SHEET_ID)
    worksheet = sheet.worksheet(GOOGLE_WORKSHEET_NAME)
    records = worksheet.get_all_records()
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
    return participants


def save_raw_responses(participants: List[Dict[str, Any]]) -> None:
    raw_path = os.getenv("RAW_RESPONSES_FILE", "data/responses_raw.json")
    try:
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(participants, f, ensure_ascii=False, indent=2)
        logger.info("Saved %d raw responses (path=%s)", len(participants), raw_path)
    except OSError:
        logger.exception("Failed to write raw responses cache (path=%s)", raw_path)


def get_participants_with_cache() -> List[Dict[str, Any]]:
    try:
        participants = fetch_responses()
        if participants:
            save_raw_responses(participants)
        return participants
    except Exception:
        logger.warning("Falling back to local raw responses cache")
        return load_raw_responses()


def build_individual_prompt(participant: Participant) -> str:
    return build_individual_prompt_app(participant)


def analyze_participant_ollama(participant: Participant) -> Dict[str, Any]:
    prompt = build_individual_prompt(participant)
    logger.info("Analyzing participant via Ollama (name=%s)", participant.get("name"))
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
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
    return build_team_prompt_app(individual_results)


def analyze_team_ollama(individual_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    prompt = build_team_prompt(individual_results)
    logger.info("Analyzing team via Ollama (n_participants=%d)", len(individual_results))
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
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
        secondaries = person.get("secondary_roles") or []
        insights = person.get("insights", "").strip()
        recs = person.get("development_recommendations") or []
        ideal = person.get("ideal_team_role", "").strip()

        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"- **Primary role:** {primary}")
        if secondaries:
            lines.append(f"- **Secondary roles:** {', '.join(secondaries)}")
        lines.append("")
        if insights:
            lines.append("**Insights**")
            lines.append("")
            lines.append(insights)
            lines.append("")
        if recs:
            lines.append("**Development recommendations**")
            lines.append("")
            for r in recs:
                lines.append(f"- {r}")
            lines.append("")
        if ideal:
            lines.append("**Ideal team role**")
            lines.append("")
            lines.append(ideal)
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
    lines.append("## Mentorship Recommendations")
    lines.append("")
    if mentorship:
        for m in mentorship:
            lines.append(f"- {m}")
    else:
        lines.append("_No mentorship recommendations available._")
    lines.append("")
    lines.append("## Collaboration Tips")
    lines.append("")
    if tips:
        for t in tips:
            lines.append(f"- {t}")
    else:
        lines.append("_No collaboration tips available._")
    lines.append("")
    return "\n".join(lines)


# -------------------------
# Load raw responses from JSON (fallback when not using Google Sheets)
# -------------------------

def load_raw_responses() -> List[Dict[str, Any]]:
    raw_path = os.getenv("RAW_RESPONSES_FILE", "data/responses_raw.json")
    logger.info("Loading raw responses (path=%s)", raw_path)
    if os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info("Loaded %d raw responses", len(data) if isinstance(data, list) else 0)
            return data
    logger.warning("Raw responses file not found (path=%s)", raw_path)
    return []


# -------------------------
# Load mentors list
# -------------------------

def load_mentors() -> List[Dict[str, Any]]:
    mentors_path = os.getenv("MENTORS_LIST_FILE", "data/mentors_list.json")
    logger.info("Loading mentors list (path=%s)", mentors_path)
    if os.path.exists(mentors_path):
        with open(mentors_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info("Loaded mentors: %d", len(data.get("mentors", [])) if isinstance(data, dict) else 0)
            return data.get("mentors", [])
    logger.warning("Mentors list file not found (path=%s)", mentors_path)
    return []

def load_report_if_exists() -> str:
    if os.path.exists(OUTPUT_MARKDOWN_FILE):
        logger.info("Loading report markdown (path=%s)", OUTPUT_MARKDOWN_FILE)
        with open(OUTPUT_MARKDOWN_FILE, "r", encoding="utf-8") as f:
            return f.read()
    else:
        logger.info("Report markdown not found yet (path=%s)", OUTPUT_MARKDOWN_FILE)
        return "# No report yet.\n\nRun the analysis to generate a report."


def run_full_analysis_and_write_report() -> None:
    run_analysis_and_write_report()


# -------------------------
# Streamlit UI
# -------------------------

logger.info("Starting Streamlit app")
st.set_page_config(page_title="Team Role Discovery", layout="wide")
st.title("🧩 Team Role Discovery Dashboard")

# Load mentors once
mentors = load_mentors()
if mentors:
    st.sidebar.markdown("### Mentors Available")
    for m in mentors:
        st.sidebar.markdown(f"- {m.get('name', 'N/A')}")

# Sidebar: actions and info
st.sidebar.header("Actions & Info")

auto_run = st.sidebar.checkbox("Auto-run analysis on startup", value=True)
if auto_run and not st.session_state.get("_auto_ran_once") and not os.path.exists(OUTPUT_MARKDOWN_FILE):
    st.session_state["_auto_ran_once"] = True
    try:
        with st.spinner("Checking sheet & generating report if needed..."):
            result = run_analysis_and_write_report()
        if result.get("cache_hit"):
            st.sidebar.info("No changes detected — reused cached report.")
        else:
            st.sidebar.success("Report generated (analysis updated).")
    except Exception as e:
        logger.exception("Auto-run analysis failed")
        st.sidebar.error(f"Auto-run analysis failed: {e}")

if st.sidebar.button("🔄 Refresh & Re‑run Analysis", type="primary"):
    try:
        logger.info("User triggered re-run analysis from Streamlit")
        with st.spinner("Checking sheet & regenerating report if needed..."):
            result = run_analysis_and_write_report()

        if result.get("cache_hit"):
            st.sidebar.info("No changes detected — reused cached report.")
        else:
            st.sidebar.success("Report regenerated successfully!")
        logger.info("Report regenerated successfully")
    except Exception as e:
        logger.exception("Failed to regenerate report")
        st.sidebar.error(f"Failed to regenerate report: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### Environment")
st.sidebar.code(f"OLLAMA_MODEL: {OLLAMA_MODEL or 'Not set'}")
st.sidebar.code(f"GOOGLE_SHEET_ID: {GOOGLE_SHEET_ID or 'Not set'}")
st.sidebar.markdown(f"Report file: `{OUTPUT_MARKDOWN_FILE}`")

# Load report markdown for parsing
report_md = load_report_if_exists()

# Parse individual results from markdown (simple regex)
def parse_individuals(md: str) -> List[Dict[str, Any]]:
    individuals = []
    # Split by H3 headings
    parts = re.split(r"\n### (.+)\n", md)
    for i in range(1, len(parts), 2):
        name = parts[i].strip()
        content = parts[i+1] if i+1 < len(parts) else ""
        # Extract fields
        primary_match = re.search(r"- \*\*Primary role:\*\* (.+)", content)
        secondary_match = re.search(r"- \*\*Secondary role:\*\* (.+)", content)
        why_match = re.search(r"\*\*Why this role\*\*\n\n(.+?)(?=\n\n|\n\*\*)", content, re.S)
        strengths_match = re.search(r"\*\*Unique strengths\*\*\n\n(.+?)(?=\n\n|\n\*\*)", content, re.S)
        ideal_match = re.search(r"\*\*Ideal team position\*\*\n\n(.+?)(?=\n\n|\n\*\*)", content, re.S)
        surprise_match = re.search(r"\*\*Surprise insight\*\*\n\n(.+?)(?=\n\n|\n\*\*)", content, re.S)

        # Backward-compat (older report format)
        insights_match = re.search(r"\*\*Insights\*\*\n\n(.+?)(?=\n\n|\n\*\*)", content, re.S)
        ideal_old_match = re.search(r"\*\*Ideal team role\*\*\n\n(.+?)(?=\n\n|\n\*\*)", content, re.S)

        primary = primary_match.group(1).strip() if primary_match else "N/A"
        secondary = secondary_match.group(1).strip() if secondary_match else ""
        why = why_match.group(1).strip() if why_match else ""
        strengths = strengths_match.group(1).strip() if strengths_match else ""
        surprise = surprise_match.group(1).strip() if surprise_match else ""
        ideal = ideal_match.group(1).strip() if ideal_match else ""

        if not why and insights_match:
            why = insights_match.group(1).strip()
        if not ideal and ideal_old_match:
            ideal = ideal_old_match.group(1).strip()

        individuals.append({
            "name": name,
            "primary_role": primary,
            "secondary_role": secondary,
            "why_this_role": why,
            "unique_strengths": strengths,
            "surprise_insight": surprise,
            "ideal_team_position": ideal,
        })
    return individuals

individuals = parse_individuals(report_md)

st.markdown("---")

# Tabs: Profiles | Team Summary
tab1, tab2 = st.tabs(["👤 Individual Profiles", "🧩 Team Summary"])

with tab1:
    st.markdown("### Select a teammate to view their profile")
    if individuals:
        names = [p["name"] for p in individuals]
        selected = st.selectbox("Choose a person:", names)
        person = next(p for p in individuals if p["name"] == selected)

        # Profile card
        st.markdown(f"## 🧾 Profile: {person['name']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Primary Role", person["primary_role"])
        with col2:
            st.metric("Secondary Role", person["secondary_role"] if person["secondary_role"] else "None")
        with col3:
            mentor_cache = st.session_state.setdefault("_mentor_match_cache", {})
            mentor_loads = st.session_state.setdefault("_mentor_assignment_loads", {})
            person_assignments = st.session_state.setdefault("_person_to_mentor", {})
            cache_key = (person.get("name"), person.get("primary_role"), person.get("secondary_role"))
            mentor = mentor_cache.get(cache_key)

            if mentor:
                mentor_name = mentor.get("name", "N/A")
                assigned = mentor.get("current_assigned_count")
                if assigned is None and mentor_name:
                    assigned = mentor_loads.get(mentor_name, 0)
                st.metric("Suggested Mentor", mentor_name)
                if assigned is not None:
                    st.caption(f"Currently assigned mentees: {assigned}")
            else:
                st.metric("Suggested Mentor", "Not generated")

            if st.button("Find mentor", key=f"find_mentor_{person.get('name','')}"):
                with st.spinner("Finding best mentor via LLM..."):
                    mentor = suggest_mentor_for_role(
                        person["primary_role"],
                        mentors,
                        participant_data=person,
                        mentor_loads=mentor_loads,
                    )
                    if not mentor and person.get("secondary_role"):
                        mentor = suggest_mentor_for_role(
                            person["secondary_role"],
                            mentors,
                            participant_data=person,
                            mentor_loads=mentor_loads,
                        )
                    if isinstance(mentor, dict) and (mentor.get("name") or "").strip():
                        # Update load counts (avoid double counting per person; adjust if reassigned)
                        person_name = (person.get("name") or "").strip()
                        new_mentor_name = (mentor.get("name") or "").strip()
                        if person_name and new_mentor_name:
                            prev_mentor_name = (person_assignments.get(person_name) or "").strip()
                            if prev_mentor_name and prev_mentor_name != new_mentor_name:
                                mentor_loads[prev_mentor_name] = max(0, int(mentor_loads.get(prev_mentor_name, 0) or 0) - 1)
                            if prev_mentor_name != new_mentor_name:
                                mentor_loads[new_mentor_name] = int(mentor_loads.get(new_mentor_name, 0) or 0) + 1
                                person_assignments[person_name] = new_mentor_name

                        # Keep the assigned count on the mentor object for display
                        mentor["current_assigned_count"] = int(mentor_loads.get(new_mentor_name, 0) or 0)
                        mentor_cache[cache_key] = mentor
                    else:
                        mentor_cache.pop(cache_key, None)
                        mentor = None
                st.rerun()
        st.markdown("---")
        st.markdown("### ❓ Why this role")
        st.markdown(person.get("why_this_role") or "")
        st.markdown("### 💪 Unique strengths")
        st.markdown(person.get("unique_strengths") or "")
        st.markdown("### 🎯 Ideal team position")
        st.markdown(person.get("ideal_team_position") or "")
        if person.get("surprise_insight"):
            st.markdown("### ✨ Surprise insight")
            st.markdown(person.get("surprise_insight") or "")

        # Mentor suggestion with reasoning
        if mentor:
            st.markdown("### 🧑‍🏫 Suggested Mentor")
            st.markdown(f"{mentor['name']}")
            reason = (mentor.get("reason") or "").strip()
            why = (mentor.get("why_this_works") or "").strip()
            first = (mentor.get("suggested_first_meeting") or "").strip()
            if reason or why or first:
                with st.expander("Why this mentor?"):
                    if reason:
                        st.markdown(reason)
                    if why:
                        st.markdown(why)
                    if first:
                        st.markdown(f"First meeting suggestion: {first}")
        else:
            st.info("Click 'Find mentor' to generate a mentor suggestion.")
    else:
        st.warning("No individual profiles found. Run the analysis first.")

with tab2:
    st.markdown(report_md, unsafe_allow_html=False)
