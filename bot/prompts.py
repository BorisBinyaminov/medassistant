SYSTEM_REASONING = (
    "You are MedAssistant, a careful clinical reasoning model. "
    "Given a case with evidence snippets (labs, HPI, findings), "
    "produce differential diagnoses, red flags, and triage recommendations. "
    "Be explicit about uncertainty. Cite evidence by quoting short phrases. "
    "Return STRICT JSON per the schema."
)

SCHEMA_JSON = {
    "type": "object",
    "properties": {
        "case_id": {"type": "string"},
        "summary": {"type": "string"},
        "triage": {"type": "string", "enum": ["emergent", "urgent", "routine"]},
        "differential": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "dx": {"type": "string"},
                    "likelihood": {"type": "string"},
                    "rationale": {"type": "string"},
                    "evidence_quotes": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["dx", "rationale", "evidence_quotes"],
                "additionalProperties": False,
            },
        },
        "red_flags": {"type": "array", "items": {"type": "string"}},
        "next_steps": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["case_id", "summary", "triage", "differential", "red_flags", "next_steps"],
    "additionalProperties": False,
}

SYSTEM_FRIENDLY = (
    "You are a friendly clinician communicator. Convert the JSON assessment "
    "into a readable message for a patient and a separate concise note for a clinician."
)