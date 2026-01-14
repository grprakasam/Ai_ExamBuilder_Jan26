import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, TrendingUp, Award, Clock, Target } from 'lucide-react';

interface ExamDashboardProps {
    examId: string;
    examName: string;
    examColor: string;
}

const examConfigs = {
    ncdpi: {
        fullName: 'North Carolina End-of-Grade',
        subjects: ['Mathematics', 'Reading', 'Science'],
        features: ['Grade-level Practice', 'Standards-aligned', 'Progress Tracking']
    },
    neet: {
        fullName: 'NEET Medical Entrance',
        subjects: ['Physics', 'Chemistry', 'Biology'],
        features: ['Negative Marking (-1)', 'Section-wise Tests', 'Previous Years']
    },
    jee: {
        fullName: 'JEE Engineering Entrance',
        subjects: ['Physics', 'Chemistry', 'Mathematics'],
        features: ['Negative Marking', 'JEE Main & Advanced', 'Topic-wise Practice']
    },
    cbse: {
        fullName: 'CBSE Board Exams',
        subjects: ['All Subjects'],
        features: ['Class 10 & 12', 'Chapter-wise Tests', 'Sample Papers']
    },
    icse: {
        fullName: 'ICSE Board Exams',
        subjects: ['All Subjects'],
        features: ['Comprehensive Curriculum', 'All Subjects', 'Board Pattern']
    },
    tn_govt: {
        fullName: 'Tamil Nadu Government',
        subjects: ['All Subjects', 'Tamil'],
        features: ['State Board Pattern', 'Tamil Medium', 'All Classes']
    },
    sat: {
        fullName: 'SAT College Admission',
        subjects: ['Math', 'Reading', 'Writing'],
        features: ['Full-length Tests', 'Section-wise', 'Score Prediction']
    },
    act: {
        fullName: 'ACT College Admission',
        subjects: ['English', 'Math', 'Reading', 'Science'],
        features: ['Composite Score', 'All Sections', 'Practice Tests']
    }
};

const ExamDashboard: React.FC<ExamDashboardProps> = ({ examId, examName, examColor }) => {
    const navigate = useNavigate();
    const config = examConfigs[examId as keyof typeof examConfigs];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
            {/* Header with Exam Branding */}
            <div className={`bg-gradient-to-r ${examColor} text-white py-8 px-4 shadow-lg`}>
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-4xl font-black mb-2">{examName} Preparation</h1>
                            <p className="text-lg opacity-90">{config.fullName}</p>
                        </div>
                        <button
                            onClick={() => navigate('/')}
                            className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg font-bold transition-colors"
                        >
                            Change Exam
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto py-8 px-4">
                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-white rounded-xl p-6 border-2 border-slate-200 shadow-sm">
                        <div className="flex items-center gap-3 mb-2">
                            <BookOpen className="w-6 h-6 text-blue-600" />
                            <span className="text-sm font-bold text-slate-600 uppercase">Tests Taken</span>
                        </div>
                        <div className="text-3xl font-black text-slate-900">12</div>
                    </div>

                    <div className="bg-white rounded-xl p-6 border-2 border-slate-200 shadow-sm">
                        <div className="flex items-center gap-3 mb-2">
                            <TrendingUp className="w-6 h-6 text-green-600" />
                            <span className="text-sm font-bold text-slate-600 uppercase">Avg Score</span>
                        </div>
                        <div className="text-3xl font-black text-slate-900">78%</div>
                    </div>

                    <div className="bg-white rounded-xl p-6 border-2 border-slate-200 shadow-sm">
                        <div className="flex items-center gap-3 mb-2">
                            <Award className="w-6 h-6 text-yellow-600" />
                            <span className="text-sm font-bold text-slate-600 uppercase">Mastered</span>
                        </div>
                        <div className="text-3xl font-black text-slate-900">8/15</div>
                    </div>

                    <div className="bg-white rounded-xl p-6 border-2 border-slate-200 shadow-sm">
                        <div className="flex items-center gap-3 mb-2">
                            <Clock className="w-6 h-6 text-purple-600" />
                            <span className="text-sm font-bold text-slate-600 uppercase">Study Time</span>
                        </div>
                        <div className="text-3xl font-black text-slate-900">24h</div>
                    </div>
                </div>

                {/* Subjects Grid */}
                <div className="mb-8">
                    <h2 className="text-2xl font-black text-slate-900 mb-4">Subjects</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {config.subjects.map((subject, idx) => (
                            <div
                                key={idx}
                                className="bg-white rounded-xl p-6 border-2 border-slate-200 hover:border-slate-300 hover:shadow-lg transition-all cursor-pointer group"
                            >
                                <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-indigo-600 transition-colors">
                                    {subject}
                                </h3>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-slate-600">Progress: 65%</span>
                                    <button className={`px-4 py-2 rounded-lg bg-gradient-to-r ${examColor} text-white font-bold text-sm hover:shadow-md transition-all`}>
                                        Practice
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Features */}
                <div className="mb-8">
                    <h2 className="text-2xl font-black text-slate-900 mb-4">Features</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {config.features.map((feature, idx) => (
                            <div
                                key={idx}
                                className="bg-white rounded-xl p-4 border-2 border-slate-200 flex items-center gap-3"
                            >
                                <Target className="w-5 h-5 text-indigo-600" />
                                <span className="font-bold text-slate-900">{feature}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className={`bg-gradient-to-br ${examColor} rounded-2xl p-8 text-white`}>
                        <h3 className="text-2xl font-black mb-3">Start New Test</h3>
                        <p className="mb-6 opacity-90">
                            Create a customized practice test based on your learning goals
                        </p>
                        <button
                            onClick={() => navigate('/create')}
                            className="px-6 py-3 bg-white text-slate-900 rounded-xl font-bold hover:shadow-lg transition-all"
                        >
                            Create Test
                        </button>
                    </div>

                    <div className="bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl p-8 text-white">
                        <h3 className="text-2xl font-black mb-3">Continue Learning</h3>
                        <p className="mb-6 opacity-90">
                            Resume your personalized learning path with adaptive difficulty
                        </p>
                        <button
                            onClick={() => navigate('/learning')}
                            className="px-6 py-3 bg-white text-slate-900 rounded-xl font-bold hover:shadow-lg transition-all"
                        >
                            Continue
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ExamDashboard;
