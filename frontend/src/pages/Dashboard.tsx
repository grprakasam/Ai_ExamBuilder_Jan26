import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Calendar, ChevronRight, Search, Plus } from 'lucide-react';
import api from '../services/api';
import { useProgressStore } from '../store/progressStore';
import { useExamStore } from '../store/examStore';
import ExamDashboard from '../components/ExamDashboard';

const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const { subjectMastery, totalQuestionsSolved } = useProgressStore();
    const { selectedExam, examName, examColor } = useExamStore();
    const [tests, setTests] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    if (selectedExam && examName && examColor) {
        return <ExamDashboard examId={selectedExam} examName={examName} examColor={examColor} />;
    }


    useEffect(() => {
        const fetchRecentTests = async () => {
            try {
                const response = await api.get('/tests/list/recent');
                setTests(response.data);
            } catch (error) {
                console.error("Failed to fetch recent tests", error);
                setTests([]);
            } finally {
                setLoading(false);
            }
        };
        fetchRecentTests();
    }, []);

    return (
        <div className="max-w-5xl mx-auto space-y-12 py-4">
            {/* Minimal Welcome Header */}
            <header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="space-y-1">
                    <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Dashboard</h1>
                    <p className="text-slate-500 font-medium">
                        Welcome back. You've completed <span className="text-indigo-600 font-bold">{totalQuestionsSolved}</span> practice questions.
                    </p>
                </div>
                <button
                    onClick={() => navigate('/create')}
                    className="flex items-center justify-center gap-2 px-6 py-2.5 bg-indigo-600 text-white rounded-xl font-bold shadow-sm hover:bg-indigo-700 transition-all active:scale-95"
                >
                    <Plus className="w-5 h-5" />
                    New Test
                </button>
            </header>

            {/* Clean Tests List */}
            <section className="space-y-6">
                <div className="flex items-center justify-between px-2">
                    <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-slate-400" />
                        Recent Activities
                    </h2>
                </div>

                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm divide-y divide-slate-100 overflow-hidden">
                    {tests.length > 0 ? tests.map((test) => (
                        <div
                            key={test.id}
                            onClick={() => navigate(`/take/${test.id}`)}
                            className="p-5 hover:bg-slate-50 transition-colors cursor-pointer group flex items-center justify-between gap-4"
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center text-slate-400 group-hover:text-indigo-600 group-hover:bg-indigo-50 transition-all">
                                    <BookOpen className="w-6 h-6" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">{test.title}</h3>
                                    <p className="text-xs text-slate-500 font-medium uppercase tracking-tighter">
                                        {test.subject} • Grade {test.grade_level} • {test.questions?.length || 0} Questions
                                    </p>
                                </div>
                            </div>
                            <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-indigo-600 transition-all transform group-hover:translate-x-1" />
                        </div>
                    )) : (
                        <div className="py-20 text-center space-y-4">
                            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto text-slate-300">
                                <Search className="w-8 h-8" />
                            </div>
                            <div className="space-y-1">
                                <p className="text-slate-900 font-bold">{loading ? "Fetching your data..." : "No assessments found"}</p>
                                <p className="text-sm text-slate-500">Start by creating your first personalized practice test.</p>
                            </div>
                            {!loading && (
                                <button
                                    onClick={() => navigate('/create')}
                                    className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-bold text-sm hover:bg-indigo-700 transition-all"
                                >
                                    Create Assessment
                                </button>
                            )}
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
};

export default Dashboard;
