"""Prompt context and topic choices; practice profiles are not official syllabus certification."""
PROFILES = {
    "ncdpi": ("North Carolina EOG", ["Number and Operations", "Fractions", "Geometry", "Reading", "Science"]),
    "neet": ("NEET medical entrance practice", ["Physics", "Chemistry", "Biology"]),
    "jee": ("JEE engineering entrance practice", ["Physics", "Chemistry", "Mathematics"]),
    "cbse": ("CBSE school curriculum practice", ["Mathematics", "Science", "English", "Social Studies"]),
    "icse": ("ICSE school curriculum practice", ["Mathematics", "Science", "English", "History and Geography"]),
    "tn_govt": ("Tamil Nadu State Board practice", ["Mathematics", "Science", "English", "Social Science"]),
    "sat": ("SAT practice", ["Algebra", "Advanced Mathematics", "Reading and Writing"]),
    "act": ("ACT practice", ["English", "Mathematics", "Reading", "Science"]),
}
def profile_prompt(exam_standard):
    key = getattr(exam_standard, "value", exam_standard).lower()
    if key not in PROFILES:
        raise ValueError("Unsupported examination")
    name, topics = PROFILES[key]
    return f"Examination: {name}. Relevant domains: {', '.join(topics)}. Produce practice material; do not claim official exam equivalence."
