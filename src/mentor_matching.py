import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests


logger = logging.getLogger(__name__)


def suggest_mentor_for_role(
    role: str,
    mentors: List[Dict[str, Any]],
    participant_data: Optional[Dict[str, Any]] = None,
    mentor_loads: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    role_norm = (role or "").strip()
    if not role_norm or not mentors:
        return {}

    ollama_model = os.getenv("OLLAMA_MODEL")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def get_fallback_mentor(reason_msg: str = "Most experienced mentor available") -> Dict[str, Any]:
        role_keywords = {
            "Data Scientist": ["data", "analytics", "statistics", "ml"],
            "ML Engineer": ["ml", "machine learning", "mlops", "deployment"],
            "AI Engineer": ["ai", "llm", "agent", "rag"],
            "Dev Ops Engineer": ["devops", "infrastructure", "kubernetes", "ci/cd"],
            "Software Engineer": ["software", "development", "architecture", "backend"],
            "Servicenow Platform Engineer": ["servicenow", "itsm", "workflow", "platform"],
        }

        keywords = role_keywords.get(role_norm, [])
        relevant_mentors = []

        for m in mentors:
            expertise = [str(e).lower() for e in (m.get("expertise") or [])]
            if any(kw in " ".join(expertise) for kw in keywords):
                relevant_mentors.append(m)

        candidates = relevant_mentors if relevant_mentors else mentors

        def _load_for(m: Dict[str, Any]) -> int:
            name = (m.get("name") or "").strip()
            if not name or not mentor_loads:
                return 0
            try:
                return int(mentor_loads.get(name, 0) or 0)
            except Exception:
                return 0

        # Prefer least-assigned mentors; then most experienced as a tie-breaker.
        top = min(
            candidates,
            key=lambda m: (_load_for(m), -(m.get("experience_years", 0) or 0)),
        )

        return {
            "name": top.get("name", "N/A"),
            "role": top.get("role", "N/A"),
            "expertise": top.get("expertise", []),
            "experience_years": top.get("experience_years", 0),
            "specialization": top.get("specialization", ""),
            "reason": f"{reason_msg}",
            "match_score": 70,
            "why_this_works": f"As a seasoned {top.get('role', 'professional')}, they can provide foundational mentorship.",
            "suggested_first_meeting": "Start with career goals discussion and map out a learning roadmap.",
            "growth_focus_areas": top.get("expertise", [])[:3]
            if top.get("expertise")
            else ["Career guidance", "Technical growth"],
            "current_assigned_count": (mentor_loads or {}).get(top.get("name", ""), 0),
        }

    if not ollama_model:
        return get_fallback_mentor("Fallback mentor (LLM not configured)")

    mentor_names = [m.get("name") for m in mentors if m.get("name")]
    mentors_json = json.dumps(mentors, ensure_ascii=False, indent=2)

    load_context = ""
    if mentor_loads:
        safe_loads = {str(k): int(v or 0) for k, v in mentor_loads.items()}
        load_context = f"\n\nCurrent mentor assignment counts (avoid overloading):\n{json.dumps(safe_loads, ensure_ascii=False, indent=2)}\n"

    participant_context = ""
    if participant_data:
        mentor_hints = participant_data.get("mentor_match_hints") if isinstance(participant_data, dict) else None
        mentor_hints = mentor_hints if isinstance(mentor_hints, dict) else {}

        skills = mentor_hints.get("skills") or []
        x_factors = mentor_hints.get("x_factors") or []
        secondary_role = participant_data.get("secondary_role") or ""

        if skills or x_factors or secondary_role:
            participant_context = f"""

Additional context about the mentee:
- Secondary role interest: {secondary_role or 'None specified'}
- Key skills: {', '.join(skills) if skills else 'Not specified'}
- Personality traits: {', '.join(x_factors) if x_factors else 'Not specified'}

Use this to find COMPLEMENTARY matches (mentor's strength = mentee's growth area).
"""

    prompt = f"""
You're an elite talent matchmaker finding the PERFECT mentor.

Your mission: Match a {role_norm} with their ideal mentor from the list below.

Mentors (JSON):
{mentors_json}
{participant_context}
{load_context}

Important: Prefer mentors with LOWER current assignment counts when there are multiple good fits.
Only pick a heavily assigned mentor if the fit is meaningfully better.

Return ONLY valid JSON (no markdown, no preamble):

{{
  "name": "<MUST be exactly one name from: {json.dumps(mentor_names, ensure_ascii=False)}>",
  "reason": "<2-4 sentences explaining why this match is great. Cite specific expertise or X Factor fields.",
  "match_score": <integer 60-100>,
  "why_this_works": "<1-2 sentences>",
  "suggested_first_meeting": "<1 sentence>",
  "growth_focus_areas": ["<area 1>", "<area 2>", "<area 3>"]
}}
""".strip()

    try:
        resp = requests.post(
            f"{ollama_base_url}/api/chat",
            json={
                "model": ollama_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.9},
            },
            timeout=60,
        )
    except requests.RequestException:
        logger.exception("Ollama HTTP error during mentor matching")
        return get_fallback_mentor("Connection error to LLM")

    if resp.status_code != 200:
        return get_fallback_mentor("LLM response error")

    data_json = resp.json()
    message = data_json.get("message") or {}
    text = (message.get("content") or "").strip()

    try:
        out = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                out = json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                logger.warning("Could not parse LLM response")
                return get_fallback_mentor("Failed to parse LLM response")
        else:
            return get_fallback_mentor("Malformed LLM response")

    if not isinstance(out, dict):
        return get_fallback_mentor("Invalid LLM response format")

    chosen_name = (out.get("name") or "").strip()
    if not chosen_name:
        return get_fallback_mentor("LLM did not select a mentor")

    chosen = next((m for m in mentors if m.get("name") == chosen_name), None)
    if not chosen:
        return get_fallback_mentor(f"LLM selected unavailable mentor ({chosen_name})")

    return {
        "name": chosen.get("name", "N/A"),
        "role": chosen.get("role", "N/A"),
        "expertise": chosen.get("expertise", []),
        "experience_years": chosen.get("experience_years", 0),
        "specialization": chosen.get("specialization", ""),
        "match_score": out.get("match_score", 85),
        "reason": (out.get("reason") or "Great mentor match!").strip(),
        "why_this_works": (out.get("why_this_works") or "Complementary skills and experience.").strip(),
        "suggested_first_meeting": (
            out.get("suggested_first_meeting") or "Discuss goals and create a learning plan."
        ).strip(),
        "growth_focus_areas": out.get("growth_focus_areas", chosen.get("expertise", [])[:3]),
        "current_assigned_count": (mentor_loads or {}).get(chosen.get("name", ""), 0),
    }
