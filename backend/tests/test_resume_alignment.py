import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["OPENAI_API_KEY"] = "test-placeholder"
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.session import get_db
from app.models.base_class import Base
from app.models.test import Test as Exam, Question, SubjectEnum, QuestionTypeEnum, DifficultyEnum, ExamStandardEnum
from app.models.concept import MasteryRecord
from app.services.scoring import score_questions
from app.schemas.generated import GeneratedQuestions
from app.services.question_generator import QuestionGenerator
from app.services.feedback_engine import FeedbackEngine

@pytest.fixture
def client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread":False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    def db():
        with Session() as session: yield session
    app.dependency_overrides[get_db] = db
    with TestClient(app) as c: yield c, Session
    app.dependency_overrides.clear()
    engine.dispose()

def seed(Session, standard="neet"):
    with Session() as db:
        test = Exam(title="Practice", grade_level=5, subject=SubjectEnum.MATH, standard_focus="Fractions",
                    question_count=2, question_type=QuestionTypeEnum.MCQ, difficulty=DifficultyEnum.MEDIUM,
                    exam_standard=ExamStandardEnum(standard), access_code="ABCD1234", max_attempts=3)
        db.add(test); db.flush()
        for i in range(2):
            db.add(Question(test_id=test.id, sequence=i+1, question_text="Example", question_type=QuestionTypeEnum.MCQ,
                            options={"A":"1","B":"2","C":"3","D":"4"}, correct_answer="A", concept_ids=["fractions"],
                            difficulty_score=0.3+i*0.4))
        from app.models.concept import Concept
        db.add(Concept(concept_id="fractions", name="Fractions"))
        db.commit()
        return str(test.id)

def start(c, tid):
    r = c.post("/api/v1/access/start-attempt", json={"test_id":tid,"access_code":"ABCD1234"})
    assert r.status_code == 200, r.text
    return r.json()["attempt_id"]

def test_startup_and_access(client):
    c, Session = client; tid=seed(Session)
    assert c.get("/health").status_code == 200
    assert c.get(f"/api/v1/tests/{tid}").status_code == 403
    assert c.get(f"/api/v1/tests/{tid}", headers={"X-Access-Code":"ABCD-1234"}).status_code == 200
    assert "access_code" not in c.get("/api/v1/tests/recent").json()[0]
    assert c.get("/api/v1/access/admin/pending-requests").status_code == 401
    first = start(c,tid)
    assert start(c,tid) == first
    from app.models.exam_attempt import ExamAttempt
    for _ in range(3):
        aid = start(c,tid)
        with Session() as db:
            db.query(ExamAttempt).filter(ExamAttempt.id == uuid.UUID(aid)).update({"is_completed":True})
            db.commit()
    assert c.post("/api/v1/access/start-attempt",json={"test_id":tid,"access_code":"ABCD1234"}).status_code == 403
    assert c.get(f"/api/v1/tests/{tid}",headers={"X-Access-Code":"ABCD1234"}).status_code == 200

def test_score_survives_feedback_outage_and_replay_rejected(client,monkeypatch):
    c, Session = client; tid=seed(Session); aid=start(c,tid)
    async def fail(*args,**kwargs): raise RuntimeError("provider unavailable")
    monkeypatch.setattr(FeedbackEngine,"evaluate_responses",fail)
    body={"attempt_id":aid,"answers":{"0":"A","1":"B"}}
    r=c.post(f"/api/v1/tests/{tid}/submit",json=body,headers={"X-Access-Code":"ABCD1234"})
    assert r.status_code==200,r.text
    assert r.json()["score"]==37.5 and r.json()["absolute_score"]==3
    assert r.json()["ai_feedback"] is None
    assert c.post(f"/api/v1/tests/{tid}/submit",json=body,headers={"X-Access-Code":"ABCD1234"}).status_code==409
    saved=c.get(f"/api/v1/tests/{tid}/results/{aid}",headers={"X-Access-Code":"ABCD1234"})
    assert saved.json()["score"]==37.5
    with Session() as db:
        records=db.query(MasteryRecord).all()
        assert len(records)==1 and records[0].questions_attempted==2
        assert records[0].next_review_due is not None

def test_practice_updates_mastery_once_and_returns_next(client):
    c, Session=client; tid=seed(Session); aid=start(c,tid)
    body={"attempt_id":aid,"question_index":0,"answer":"A","time_taken_seconds":10}
    r=c.post(f"/api/v1/tests/{tid}/practice-answer",json=body,headers={"X-Access-Code":"ABCD1234"})
    assert r.status_code==200,r.text
    assert r.json()["next_question_index"]==1
    assert c.post(f"/api/v1/tests/{tid}/practice-answer",json=body,headers={"X-Access-Code":"ABCD1234"}).status_code==409
    assert c.get(f"/api/v1/learning/mastery/summary/{tid}",headers={"X-Access-Code":"ABCD1234"}).json()["total_concepts"]==1
    other=c.get(f"/api/v1/learning/mastery/summary/{tid}",headers={"X-Access-Code":"ABCD1234","user-agent":"another-browser"})
    assert other.json()["total_concepts"]==0

def test_generated_metadata_and_exam_context(client,monkeypatch):
    c,Session=client; seen={}
    async def fake(self,**kwargs):
        seen.update(kwargs)
        return [{"sequence":1,"question_text":"Question","question_type":"mcq","correct_answer":"A",
                 "options":{"A":"1","B":"2","C":"3","D":"4"},"concept_ids":["algebra"],"difficulty_score":0.4,"hint":"Hint"}]
    monkeypatch.setattr(QuestionGenerator,"generate_questions",fake)
    body={"title":"JEE practice","grade_level":12,"subject":"mathematics","standard_focus":"Algebra",
          "question_count":1,"question_type":"mcq","difficulty":"medium","exam_standard":"jee"}
    r=c.post("/api/v1/tests/generate",json=body)
    assert r.status_code==200,r.text
    assert seen["exam_standard"]=="jee" and r.json()["access_code"]
    assert r.json()["questions"][0]["concept_ids"]==["algebra"]
    assert r.json()["questions"][0]["hint"]=="Hint"

def test_bad_model_output_rejected_before_saving(client,monkeypatch):
    c,Session=client
    async def fake(*args,**kwargs): return [{"sequence":1,"question_text":"Q","question_type":"mcq","correct_answer":"Z","options":{"A":"1"}}]
    monkeypatch.setattr(QuestionGenerator,"generate_questions",fake)
    r=c.post("/api/v1/tests/generate",json={"title":"Bad output","grade_level":5,"subject":"mathematics",
        "standard_focus":"Fractions","question_count":1,"question_type":"mcq","difficulty":"medium"})
    assert r.status_code==502
    with Session() as db: assert db.query(Exam).count()==0

def test_examination_prompt_context():
    generator=QuestionGenerator()
    assert "JEE engineering" in generator._build_prompt(12,"mathematics","Algebra",1,"mcq","medium","jee")
    assert "NEET medical" in generator._build_prompt(12,"science","Biology",1,"mcq","medium","neet")

def test_result_pdf_uses_saved_score_and_access_checks(client,monkeypatch):
    from pathlib import Path
    from app.services.pdf_service import PDFService
    c, Session=client; tid=seed(Session); aid=start(c,tid)
    response=c.post(f"/api/v1/tests/{tid}/submit",headers={"X-Access-Code":"ABCD1234"},
                    json={"attempt_id":aid,"answers":{"0":"A","1":"B"},"include_feedback":False})
    assert response.status_code==200
    captured={}
    def fake_pdf(self, info, questions, output, **kwargs):
        captured.update(info)
        Path(output).write_bytes(b"%PDF-1.4 test")
    monkeypatch.setattr(PDFService,"generate_test_pdf",fake_pdf)
    path=f"/api/v1/reports/{tid}/results/download?attempt_id={aid}&score=100&feedback=fake"
    assert c.get(path).status_code==403
    assert c.get(path,headers={"X-Access-Code":"ABCD1234"}).status_code==200
    assert captured["score"]==37.5 and captured["feedback"]!="fake"
    assert c.get(path,headers={"X-Access-Code":"ABCD1234","user-agent":"other"}).status_code==403

def test_written_practice_waits_for_human_review(client):
    from app.models.test import QuestionTypeEnum
    c, Session=client; tid=seed(Session); aid=start(c,tid)
    with Session() as db:
        question=db.query(Question).filter(Question.test_id==uuid.UUID(tid), Question.sequence==1).one()
        question.question_type=QuestionTypeEnum.OPEN_ENDED
        db.commit()
    r=c.post(f"/api/v1/tests/{tid}/practice-answer",headers={"X-Access-Code":"ABCD1234"},
             json={"attempt_id":aid,"question_index":0,"answer":"A written explanation"})
    assert r.status_code==200, r.text
    assert r.json()["is_correct"] is None
    with Session() as db: assert db.query(MasteryRecord).count()==0
