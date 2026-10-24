import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Send, Timer, CheckCircle2, Lightbulb, MessageSquare, XCircle } from 'lucide-react';
import api from '../services/api';

const TakeTest: React.FC = () => {
    const { testId } = useParams<{ testId: string }>();
    const navigate = useNavigate();
    const location = useLocation();
    const practiceMode = location.state?.practiceMode || false;

    const [accessCode, setAccessCode] = useState(sessionStorage.getItem('exam-access:' + testId) || '');
    const [enteredCode, setEnteredCode] = useState('');
    const [attemptId, setAttemptId] = useState('');
    const [nextAdaptiveIndex, setNextAdaptiveIndex] = useState<number | null>(null);
    const [answerError, setAnswerError] = useState('');
    const [started] = useState(Date.now());
    const [test, setTest] = useState<any>(null);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [timeLeft, setTimeLeft] = useState(15 * 60);
    const [showHint, setShowHint] = useState(false);
    const [isAnswered, setIsAnswered] = useState(false);

    useEffect(() => {
        const fetchTest = async () => {
            if (!accessCode) { setLoading(false); return; }
            setLoading(true);
            try {
                sessionStorage.setItem('exam-access:' + testId, accessCode);
                const response = await api.get(`/tests/${testId}`);
                const attempt = await api.post('/access/start-attempt', { test_id: testId, access_code: accessCode });
                setAttemptId(attempt.data.attempt_id);
                setAnswers(attempt.data.answers || {});
                const remaining = response.data.questions.findIndex((_: unknown, i: number) => !(String(i) in (attempt.data.answers || {})));
                setCurrentQuestionIndex(remaining >= 0 ? remaining : response.data.questions.length - 1);
                setIsAnswered(remaining < 0 && practiceMode);
                sessionStorage.setItem('exam-attempt:' + testId, attempt.data.attempt_id);
                setTest(response.data);
            } catch (error) {
                setAnswerError("Check your access code and remaining attempts.");
            } finally {
                setLoading(false);
            }
        };
        fetchTest();
    }, [testId, accessCode]);

    useEffect(() => {
        if (timeLeft <= 0 || practiceMode) return;
        const timer = setInterval(() => {
            setTimeLeft(prev => prev - 1);
        }, 1000);
        return () => clearInterval(timer);
    }, [timeLeft, practiceMode]);

    const handleAnswerChange = async (value: string) => {
        if (isAnswered && practiceMode) return;

        setAnswers({
            ...answers,
            [currentQuestionIndex]: value
        });

        if (practiceMode) {
            try {
                setSubmitting(true);
                const { data } = await api.post('/tests/' + testId + '/practice-answer', {
                    attempt_id: attemptId, question_index: currentQuestionIndex, answer: value,
                    time_taken_seconds: (Date.now() - started) / 1000, had_hint: showHint
                });
                setNextAdaptiveIndex(data.next_question_index);
                setIsAnswered(true); setAnswerError('');
            } catch { setAnswerError('Could not record this answer. Please retry.'); }
            finally { setSubmitting(false); }
        }
    };

    const nextQuestion = () => {
        setCurrentQuestionIndex(prev => practiceMode ? (nextAdaptiveIndex ?? prev) : prev + 1);
        setIsAnswered(false);
        setShowHint(false);
    };

    const handleSubmit = async () => {
        setSubmitting(true);
        try {
            const response = await api.post(`/tests/${testId}/submit`, { attempt_id: attemptId, answers, time_taken_seconds: Math.round((Date.now() - started) / 1000) });
            navigate(`/results/${testId}`, {
                state: {
                    answers,
                    score: response.data.score,
                    attemptId,
                    ai_feedback: response.data.ai_feedback,
                    practiceMode
                }
            });
        } catch (error) {
            setAnswerError("Submission failed. Your answers remain here; please retry.");
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
            <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
    );

    if (!test) return <section className="max-w-md mx-auto space-y-4">
        <h1 className="text-xl font-bold">Enter test access code</h1>
        <p>{answerError || 'Use the access code shared with this test.'}</p>
        <input aria-label="Access code" className="border p-3" value={enteredCode} onChange={e => setEnteredCode(e.target.value)} />
        <button className="bg-indigo-600 text-white p-3" onClick={() => setAccessCode(enteredCode)}>Open test</button>
    </section>;

    const questions = test.questions || [];
    const currentQuestion = questions[currentQuestionIndex];
    const isLastQuestion = practiceMode ? Object.keys(answers).length >= questions.length && isAnswered : currentQuestionIndex === questions.length - 1;
    const isMCQ = currentQuestion.question_type === 'mcq' || !!currentQuestion.options;
    const userAnswer = answers[currentQuestionIndex];
    const isCorrect = userAnswer === currentQuestion.correct_answer;

    return (
        <div className="max-w-4xl mx-auto space-y-8 py-4 animate-in slide-in-from-bottom duration-400">
            {/* Header with Focus */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="space-y-1">
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl font-black text-slate-900 tracking-tight">{test.title}</h1>
                        {practiceMode && (
                            <span className="px-2 py-0.5 bg-emerald-50 text-emerald-600 border border-emerald-100 rounded text-[10px] font-black uppercase tracking-widest">
                                Practice Mode
                            </span>
                        )}
                    </div>
                    <p className="text-slate-500 font-medium">Question {currentQuestionIndex + 1} of {questions.length}</p>
                </div>
                {!practiceMode && (
                    <div className="flex items-center gap-3 bg-white px-4 py-2 rounded-2xl border border-slate-200 shadow-sm">
                        <Timer className="w-5 h-5 text-indigo-600" />
                        <span className="text-lg font-black font-mono text-slate-900 tracking-tighter">
                            {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
                        </span>
                    </div>
                )}
            </div>

            {/* Progress Bar */}
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden shadow-inner">
                <div className="h-full bg-indigo-600 transition-all duration-700 ease-out shadow-sm" style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }} />
            </div>

            {/* Assessment Area */}
            <div className="bg-white p-8 sm:p-12 rounded-[2rem] border border-slate-200 shadow-xl shadow-slate-100/50 space-y-10 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1.5 bg-indigo-600/10" />

                <button
                    onClick={() => setShowHint(!showHint)}
                    className="absolute top-8 right-8 p-3 rounded-2xl bg-amber-50 text-amber-600 hover:bg-amber-100 transition-all border border-amber-100 shadow-sm"
                    title="Get a hint"
                >
                    <Lightbulb className="w-6 h-6" />
                </button>

                <div className="space-y-6">
                    <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 leading-[1.3] tracking-tight">
                        {currentQuestion.question_text}
                    </h2>
                </div>

                {showHint && (
                    <div className="bg-amber-50 border-l-4 border-amber-400 p-5 rounded-2xl animate-in fade-in zoom-in duration-300">
                        <div className="flex items-center gap-2 mb-1">
                            <Lightbulb className="w-4 h-4 text-amber-600" />
                            <span className="text-xs font-black text-amber-700 uppercase">Hint</span>
                        </div>
                        <p className="text-sm text-slate-700 font-medium italic leading-relaxed">{currentQuestion.hint || 'Consider the relevant concepts and show each step.'}</p>
                    </div>
                )}

                {isMCQ ? (
                    <div className="grid grid-cols-1 gap-4">
                        {Object.entries(currentQuestion.options || {}).map(([key, value]) => (
                            <button
                                key={key}
                                onClick={() => handleAnswerChange(key)}
                                disabled={submitting || (isAnswered && practiceMode)}
                                className={`flex items-start gap-5 p-6 rounded-2xl border-2 transition-all text-left group ${userAnswer === key
                                    ? (practiceMode ? (isCorrect ? 'border-emerald-500 bg-emerald-50' : 'border-rose-500 bg-rose-50') : 'border-indigo-600 bg-indigo-50 shadow-md')
                                    : 'border-slate-50 bg-slate-50 hover:border-slate-200 hover:bg-white'
                                    }`}
                            >
                                <div className={`w-9 h-9 rounded-xl flex items-center justify-center font-black flex-shrink-0 transition-transform group-hover:scale-105 ${userAnswer === key ? 'bg-indigo-600 text-white' : 'bg-white text-slate-400 border border-slate-200 shadow-sm'}`}>
                                    {key}
                                </div>
                                <span className={`flex-1 font-bold text-lg leading-snug pt-1 ${userAnswer === key ? 'text-slate-900' : 'text-slate-600'}`}>
                                    {value as string}
                                </span>
                                {practiceMode && isAnswered && key === currentQuestion.correct_answer && (
                                    <div className="bg-emerald-100 border border-emerald-200 p-1.5 rounded-lg ml-2">
                                        <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                                    </div>
                                )}
                                {practiceMode && isAnswered && userAnswer === key && !isCorrect && (
                                    <div className="bg-rose-100 border border-rose-200 p-1.5 rounded-lg ml-2">
                                        <XCircle className="w-5 h-5 text-rose-600" />
                                    </div>
                                )}
                            </button>
                        ))}
                    </div>
                ) : (
                    <textarea
                        value={userAnswer || ''}
                        onChange={(e) => setAnswers({ ...answers, [currentQuestionIndex]: e.target.value })}
                        placeholder="Type your detailed response here..."
                        className="w-full bg-slate-50 border-2 border-slate-100 rounded-3xl p-8 h-48 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-600 transition-all font-medium text-lg text-slate-900 placeholder-slate-400"
                    />
                )}

                {practiceMode && !isMCQ && !isAnswered && <button disabled={submitting || !userAnswer}
                    onClick={() => handleAnswerChange(userAnswer)}>Record written answer for review</button>}
                {practiceMode && !isMCQ && isAnswered && <p>Written answer recorded. Educator review is required.</p>}
                {practiceMode && isMCQ && isAnswered && (
                    <div className={`p-8 rounded-3xl border-2 animate-in slide-in-from-top duration-500 ${isCorrect ? 'bg-emerald-50 border-emerald-100' : 'bg-rose-50 border-rose-100'}`}>
                        <div className="flex items-center gap-3 mb-3">
                            <MessageSquare className={`w-5 h-5 ${isCorrect ? 'text-emerald-600' : 'text-rose-600'}`} />
                            <span className={`text-sm font-black uppercase tracking-widest ${isCorrect ? 'text-emerald-700' : 'text-rose-700'}`}>
                                {isCorrect ? 'Excellent Job!' : 'Learning Opportunity'}
                            </span>
                        </div>
                        <p className="text-lg text-slate-700 leading-relaxed font-medium">
                            {isCorrect ? 'Your answer is exactly correct.' : `The optimal choice was ${currentQuestion.correct_answer}. `}
                            <span className="block mt-2 font-normal text-slate-600 italic">
                                {currentQuestion.explanation}
                            </span>
                        </p>
                    </div>
                )}
            </div>

            {answerError && <p role="alert">{answerError}</p>}
            {/* Navigation Controls */}
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4 py-4">
                <button
                    onClick={() => setCurrentQuestionIndex(p => p - 1)}
                    disabled={practiceMode || currentQuestionIndex === 0}
                    className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-30 font-bold flex items-center justify-center gap-2 transition-all"
                >
                    <ChevronLeft className="w-5 h-5" /> Previous
                </button>

                {isLastQuestion ? (
                    <button
                        onClick={handleSubmit}
                        disabled={!userAnswer || submitting}
                        className="w-full sm:w-auto px-10 py-4 rounded-2xl bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 font-black shadow-xl shadow-indigo-100 flex items-center justify-center gap-3 transition-all hover:scale-[1.02] active:scale-95 text-lg"
                    >
                        {submitting ? 'Submitting Responses...' : 'Finish Assessment'}
                        <Send className="w-5 h-5" />
                    </button>
                ) : (
                    <button
                        onClick={nextQuestion}
                        disabled={!userAnswer || submitting || (practiceMode && !isAnswered)}
                        className="w-full sm:w-auto px-12 py-4 rounded-2xl bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 font-black shadow-xl shadow-indigo-100 flex items-center justify-center gap-3 transition-all hover:scale-[1.02] active:scale-95 text-lg"
                    >
                        Next Question <ChevronRight className="w-5 h-5" />
                    </button>
                )}
            </div>
        </div>
    );
};

export default TakeTest;
