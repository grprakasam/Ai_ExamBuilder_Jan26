"""Authoritative MCQ scoring. Model feedback never changes these results."""
def score_questions(questions, answers, exam_standard):
    standard = getattr(exam_standard, "value", exam_standard)
    correct = wrong = total = 0
    for i, q in enumerate(questions):
        if getattr(q.question_type, "value", q.question_type) != "mcq":
            continue
        total += 1
        answer = answers.get(str(i))
        if answer in (None, ""):
            continue
        if answer not in (q.options or {}):
            raise ValueError(f"Invalid option for question {i + 1}")
        if answer == q.correct_answer:
            correct += 1
        else:
            wrong += 1
    raw = correct * 4 - wrong if standard == "neet" else correct
    maximum = total * 4 if standard == "neet" else total
    return {"score": raw / maximum * 100 if maximum else 0.0,
            "absolute_score": raw, "correct_count": correct, "wrong_count": wrong,
            "total_mcq": total, "exam_standard": standard}
