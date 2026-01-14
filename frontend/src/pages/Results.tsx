import React, { useEffect, useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle2, XCircle, ChevronLeft, Download, Award, Target, Brain, Sparkles, MessageSquare, Lightbulb, RefreshCw, Search } from 'lucide-react';
import api from '../services/api';
import { useProgressStore } from '../store/progressStore';

const Results: React.FC = () => {
    const { testId } = useParams<{ testId: string }>();
    const location = useLocation();
    const navigate = useNavigate();
    const userAnswers = location.state?.answers || {};
    const aiFeedback = location.state?.ai_feedback || null;
    const practiceMode = location.state?.practiceMode || false;
    const updateProgress = useProgressStore(state => state.updateProgress);

    const [test, setTest] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [downloading, setDownloading] = useState(false);

    useEffect(() => {
        const fetchTest = async () => {
            try {
                const response = await api.get(`/tests/${testId}`);
                setTest(response.data);
            } catch (error) {
                console.error("Failed to fetch test", error);
            } finally {
                setLoading(false);
            }
        };
        fetchTest();
    }, [testId]);

    // Calculate Score
    const getScore = () => {
        if (!test) return 0;
        const questions = test.questions || [];
        if (aiFeedback?.evaluations) {
            const sum = aiFeedback.evaluations.reduce((acc: number, curr: any) => acc + (curr.score || 0), 0);
            return Math.round((sum / questions.length) * 100);
        } else {
            let correct = 0;
            questions.forEach((q: any, index: number) => {
                if (userAnswers[index] === q.correct_answer) correct++;
            });
            return Math.round((correct / questions.length) * 100);
        }
    };

    const totalScore = getScore();

    useEffect(() => {
        if (test && !loading) {
            updateProgress(test.subject, totalScore, test.questions?.length || 0);
        }
    }, [test, loading]);

    const handleDownload = async () => {
        setDownloading(true);
        try {
            const response = await api.get(`/reports/${testId}/results/download`, {
                params: {
                    score: totalScore,
                    feedback: aiFeedback?.overall_summary || "Good effort!"
                },
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Report_${test.title}.pdf`);
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            console.error("Download failed", error);
        } finally {
            setDownloading(false);
        }
    };

    if (loading) return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
            <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-slate-400">Loading your performance report...</p>
        </div>
    );

    if (!test) return <div>Test not found</div>;

    const questions = test.questions || [];

    return (
        <div className="max-w-5xl mx-auto space-y-12 py-4 animate-in fade-in duration-700">
            {/* Summary Header - Professional Report Style */}
            <div className="bg-white rounded-[2.5rem] border border-slate-200 p-10 sm:p-14 text-center space-y-10 relative overflow-hidden shadow-xl shadow-slate-100/50">
                <div className="absolute top-0 left-0 w-full h-2 bg-indigo-600" />

                <div className="flex flex-col items-center gap-4">
                    <div className="inline-flex items-center justify-center p-6 bg-indigo-50 rounded-full border border-indigo-100 mb-2">
                        <Award className="w-16 h-16 text-indigo-600" />
                    </div>
                    {practiceMode && (
                        <div className="px-4 py-1 bg-emerald-50 text-emerald-600 border border-emerald-100 rounded-full text-xs font-black uppercase tracking-widest">
                            Practice Session Verified
                        </div>
                    )}
                </div>

                <div className="space-y-3">
                    <h1 className="text-4xl sm:text-5xl font-black text-slate-900 tracking-tight">Performance Report</h1>
                    <p className="text-slate-500 font-bold text-lg">{test.title}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl mx-auto">
                    <div className="p-8 bg-slate-50 rounded-3xl border border-slate-100 flex flex-col items-center justify-center space-y-3 transition-transform hover:scale-[1.02]">
                        <div className="p-3 bg-white rounded-2xl border border-slate-100 shadow-sm">
                            <Target className="w-8 h-8 text-indigo-600" />
                        </div>
                        <p className="text-5xl font-black text-slate-900 tracking-tighter">{totalScore}%</p>
                        <p className="text-xs text-slate-400 uppercase tracking-widest font-black">Overall Mastery</p>
                    </div>
                    <div className="p-8 bg-slate-50 rounded-3xl border border-slate-100 flex flex-col items-center justify-center space-y-3 transition-transform hover:scale-[1.02]">
                        <div className="p-3 bg-white rounded-2xl border border-slate-100 shadow-sm">
                            <Brain className="w-8 h-8 text-indigo-600" />
                        </div>
                        <p className="text-3xl font-black text-slate-900">{totalScore >= 80 ? 'Distinguished' : totalScore >= 60 ? 'Proficient' : 'Developing'}</p>
                        <p className="text-xs text-slate-400 uppercase tracking-widest font-black">NCDPI Performance Level</p>
                    </div>
                </div>

                {aiFeedback?.overall_summary && (
                    <div className="bg-indigo-50/50 border border-indigo-100 p-8 rounded-3xl text-left space-y-4">
                        <div className="flex items-center gap-3 text-indigo-600 font-black uppercase tracking-widest text-xs">
                            <Sparkles className="w-5 h-5" />
                            Clinical Learning Insight
                        </div>
                        <p className="text-slate-700 leading-relaxed italic text-lg font-medium">"{aiFeedback.overall_summary}"</p>
                    </div>
                )}

                <div className="flex flex-wrap justify-center gap-4 pt-6">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="flex items-center gap-3 px-8 py-4 bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 rounded-2xl font-black transition-all shadow-sm"
                    >
                        <ChevronLeft className="w-5 h-5" />
                        Back to Dashboard
                    </button>
                    <button
                        onClick={handleDownload}
                        disabled={downloading}
                        className="flex items-center gap-3 px-8 py-4 bg-indigo-600 text-white hover:bg-indigo-700 rounded-2xl font-black transition-all shadow-xl shadow-indigo-100 disabled:opacity-50"
                    >
                        <Download className="w-5 h-5" />
                        {downloading ? "Generating PDF..." : "Export Report"}
                    </button>
                    <button
                        onClick={() => navigate('/create')}
                        className="flex items-center gap-3 px-8 py-4 bg-emerald-600 text-white hover:bg-emerald-700 rounded-2xl font-black transition-all shadow-xl shadow-emerald-100"
                    >
                        <RefreshCw className="w-5 h-5" />
                        New Practice
                    </button>
                </div>
            </div>

            {/* In-Depth Question Review */}
            <div className="space-y-8 px-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-3">
                        <Search className="w-6 h-6 text-slate-400" />
                        Detailed Analysis
                    </h2>
                </div>

                <div className="space-y-8">
                    {questions.map((q: any, index: number) => {
                        const feedback = aiFeedback?.evaluations?.find((e: any) => e.index === index + 1);
                        const isCorrect = feedback ? feedback.score >= 0.8 : userAnswers[index] === q.correct_answer;
                        const isMCQ = q.question_type === 'mcq' || !!q.options;

                        return (
                            <div key={index} className={`p-8 sm:p-10 bg-white rounded-[2rem] border-2 ${isCorrect ? 'border-emerald-100 shadow-emerald-50/50' : 'border-rose-100 shadow-rose-50/50'} space-y-8 shadow-xl transition-all hover:scale-[1.01]`}>
                                <div className="flex items-start justify-between gap-6">
                                    <div className="space-y-3">
                                        <div className="flex items-center gap-3">
                                            <span className={`px-2.5 py-1 rounded-lg font-black text-xs ${isCorrect ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                                                Q{index + 1}
                                            </span>
                                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                                {isMCQ ? 'Conceptual Selection' : 'Written Performance'}
                                            </span>
                                        </div>
                                        <h3 className="text-xl sm:text-2xl font-bold text-slate-900 leading-tight tracking-tight">
                                            {q.question_text}
                                        </h3>
                                    </div>
                                    <div className={`p-3 rounded-2xl ${isCorrect ? 'bg-emerald-50' : 'bg-rose-50'}`}>
                                        {isCorrect ? (
                                            <CheckCircle2 className="w-8 h-8 text-emerald-600 flex-shrink-0" />
                                        ) : (
                                            <XCircle className="w-8 h-8 text-rose-600 flex-shrink-0" />
                                        )}
                                    </div>
                                </div>

                                {isMCQ ? (
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        {Object.entries(q.options || {}).map(([key, value]) => {
                                            const isSelected = userAnswers[index] === key;
                                            const isRight = q.correct_answer === key;
                                            return (
                                                <div
                                                    key={key}
                                                    className={`p-5 rounded-2xl text-sm border-2 flex items-center gap-4 transition-all ${isRight ? 'bg-emerald-50 border-emerald-200 text-slate-900 font-bold' :
                                                        isSelected ? 'bg-rose-50 border-rose-200 text-slate-900 font-bold' :
                                                            'bg-slate-50 border-slate-50 text-slate-500'
                                                        }`}
                                                >
                                                    <span className={`w-8 h-8 rounded-xl flex items-center justify-center font-black text-xs ${isRight ? 'bg-emerald-600 text-white' : isSelected ? 'bg-rose-600 text-white' : 'bg-white border border-slate-200 text-slate-400'}`}>
                                                        {key}
                                                    </span>
                                                    <span className="flex-1">{value as string}</span>
                                                </div>
                                            );
                                        })}
                                    </div>
                                ) : (
                                    <div className="space-y-4 bg-slate-50 p-8 rounded-3xl border border-slate-100">
                                        <div className="flex items-center gap-2 text-slate-400 text-[10px] font-black uppercase tracking-widest">
                                            <MessageSquare className="w-3 h-3" />
                                            Authentication of Response
                                        </div>
                                        <p className="text-slate-700 leading-relaxed font-medium italic text-lg">
                                            {userAnswers[index] || "No response provided for this assessment."}
                                        </p>
                                    </div>
                                )}

                                {(feedback?.feedback || q.explanation) && (
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        <div className="bg-white p-6 rounded-2xl border border-indigo-100 flex gap-5 shadow-sm">
                                            <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center flex-shrink-0">
                                                <MessageSquare className="w-5 h-5 text-indigo-600" />
                                            </div>
                                            <div className="space-y-2">
                                                <p className="text-[10px] font-black text-indigo-600 uppercase tracking-widest">Educator Feedback</p>
                                                <p className="text-sm text-slate-600 leading-relaxed font-bold">
                                                    {feedback?.feedback || q.explanation}
                                                </p>
                                            </div>
                                        </div>
                                        {feedback?.suggestion && (
                                            <div className="bg-white p-6 rounded-2xl border border-amber-100 flex gap-5 shadow-sm">
                                                <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center flex-shrink-0">
                                                    <Lightbulb className="w-5 h-5 text-amber-600" />
                                                </div>
                                                <div className="space-y-2">
                                                    <p className="text-[10px] font-black text-amber-600 uppercase tracking-widest">Next-Level Strategy</p>
                                                    <p className="text-sm text-slate-600 leading-relaxed font-bold">
                                                        {feedback.suggestion}
                                                    </p>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default Results;
