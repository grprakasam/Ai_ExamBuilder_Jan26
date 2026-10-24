# Integrated learning and scoring: evidence and limits

This revision fixes app.database imports and registers concept/attempt models.
Generation validates model output before saving, preserves learning metadata,
passes the selected exam standard into the prompt and returns a generated
access code. Profiles cover the eight enum/UI choices; these are practice
contexts, not official syllabus certification.

Taking a test now validates its code, starts/resumes a session-bound attempt,
checks answer ownership and computes MCQ scores deterministically on the
server (NEET +4/-1/0; other profiles percentage correct). AI feedback is optional;
provider outages cannot replace or discard the computed MCQ result. Persisted
results and result PDFs use the server calculation. Open-ended responses still
require educator review; the displayed percentage covers MCQs only.

Practice submissions update mastery and review dates from checked answers,
reject duplicate updates, and select the next unanswered question by recommended
difficulty from the generated bank. The Learning page reads real mastery and
due reviews. This is a heuristic learning prototype, not validated adaptive
psychometrics or a CAT examination engine.

Access codes protect question retrieval, submissions, reports and learning
queries. Administrative attempt requests require a real JWT and the
ADMIN_EMAILS allowlist. The IP/user-agent hash is a lightweight anonymous
session heuristic; shared networks/browsers can collide, and changing clients
can bypass per-session attempt limits. This is not robust learner identity or
a secure high-stakes testing system. Question payloads include answers for
practice feedback.

Before using an existing database, back it up and run from backend:
python -m scripts.migrate_learning_scope
The additive migration creates missing registered tables and adds learner_key
to legacy mastery records. Legacy records retain learner_key=legacy rather than
being silently assigned to a new learner. Existing tests without a code must
receive one separately before access.

Local integration tests use an isolated SQLite database and mocked model calls.
They cover app startup, access checks/attempt limits, generation validation,
metadata persistence, deterministic scoring during a feedback outage, attempt
replay prevention and learner-isolated mastery. Frontend production compilation
also passes. Paid model quality, deployed concurrency/load and educational
outcomes have not been measured.
