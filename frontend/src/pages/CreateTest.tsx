import React, { useState, useEffect } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Sparkles, Loader2, FileText, Download, Brain, Zap, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useExamStore } from '../store/examStore';

// NCDPI Standards Data
const standardsData: Record<string, Record<string, string[]>> = {
    mathematics: {
        '3': ['Operations & Algebraic Thinking (OA)', 'Number & Operations in Base Ten (NBT)', 'Number & Operations - Fractions (NF)', 'Measurement & Data (MD)', 'Geometry (G)'],
        '4': ['Operations & Algebraic Thinking (OA)', 'Number & Operations in Base Ten (NBT)', 'Number & Operations - Fractions (NF)', 'Measurement & Data (MD)', 'Geometry (G)'],
        '5': ['Operations & Algebraic Thinking (OA)', 'Number & Operations in Base Ten (NBT)', 'Number & Operations - Fractions (NF)', 'Measurement & Data (MD)', 'Geometry (G)'],
        '6': ['Ratio & Proportional Relationships (RP)', 'The Number System (NS)', 'Expressions & Equations (EE)', 'Geometry (G)', 'Statistics & Probability (SP)'],
        '7': ['Ratio & Proportional Relationships (RP)', 'The Number System (NS)', 'Expressions & Equations (EE)', 'Geometry (G)', 'Statistics & Probability (SP)'],
        '8': ['The Number System (NS)', 'Expressions & Equations (EE)', 'Functions (F)', 'Geometry (G)', 'Statistics & Probability (SP)'],
        'default': ['Number Sense', 'Algebra', 'Geometry', 'Measurement', 'Data Analysis & Probability']
    },
    english: {
        'default': ['Reading: Literature (RL)', 'Reading: Informational Text (RI)', 'Writing (W)', 'Speaking & Listening (SL)', 'Language (L)']
    },
    science: {
        '5': ['Forces & Motion', 'Matter: Properties & Change', 'Energy: Conservation & Transfer', 'Earth Systems & Weather', 'Ecosystems'],
        '8': ['Matter: Properties & Change', 'Energy: Conservation & Transfer', 'Earth Systems, Structures & Processes', 'Ecosystems', 'Evolution & Genetics'],
        'default': ['Forces & Motion', 'Matter & Energy', 'Earth Science', 'Life Science', 'Ecosystems']
    },
    social_studies: {
        'default': ['History', 'Geography & Environmental Literacy', 'Civics & Governance', 'Economics & Financial Literacy', 'Culture']
    }
};

const getStandardsForSelection = (subject: string, gradeLevel: string): string[] => {
    const subjectData = standardsData[subject] || standardsData.mathematics;
    return subjectData[gradeLevel] || subjectData['default'] || [];
};

const testSchema = z.object({
    title: z.string().min(5, 'Title must be at least 5 characters'),
    grade_level: z.string(),
    subject: z.string(),
    standard_focus: z.string().min(1, 'Please select a standard'),
    question_count: z.string(),
    question_type: z.string(),
    difficulty: z.string(),
});

const CreateTest: React.FC = () => {
    const navigate = useNavigate();
    const { selectedExam } = useExamStore();
    const [loading, setLoading] = useState(false);
    const [generatedTest, setGeneratedTest] = useState<any>(null);
    const [availableStandards, setAvailableStandards] = useState<string[]>([]);
    const [step, setStep] = useState(1);

    const { register, handleSubmit, formState: { errors }, control, setValue, watch } = useForm<any>({
        resolver: zodResolver(testSchema),
        defaultValues: {
            title: '',
            question_count: '10',
            grade_level: '5',
            subject: 'mathematics',
            standard_focus: '',
            question_type: 'mcq',
            difficulty: 'medium',
            practice_mode: false,
        }
    });

    const watchSubject = useWatch({ control, name: 'subject' });
    const watchGradeLevel = useWatch({ control, name: 'grade_level' });
    const watchAll = watch();

    useEffect(() => {
        const standards = getStandardsForSelection(watchSubject, watchGradeLevel);
        setAvailableStandards(standards);
        setValue('standard_focus', standards[0] || '');
    }, [watchSubject, watchGradeLevel, setValue]);

    const onSubmit = async (data: any) => {
        setLoading(true);
        try {
            const apiData = {
                ...data,
                grade_level: parseInt(data.grade_level),
                question_count: parseInt(data.question_count),
                exam_standard: selectedExam || 'ncdpi'
            };
            const response = await api.post('/tests/generate', apiData);
            setGeneratedTest(response.data);
            setStep(3);
        } catch (error) {
            console.error('Error generating test:', error);
            alert('Failed to generate test. Please check backend connection and API keys.');
        } finally {
            setLoading(false);
        }
    };

    const subjects = [
        { value: 'mathematics', label: 'Mathematics', icon: '📐', color: 'from-blue-500 to-indigo-600' },
        { value: 'english', label: 'English', icon: '📚', color: 'from-purple-500 to-pink-600' },
        { value: 'science', label: 'Science', icon: '🔬', color: 'from-emerald-500 to-teal-600' },
        { value: 'social_studies', label: 'Social Studies', icon: '🌍', color: 'from-amber-500 to-orange-600' },
    ];

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-2xl sm:text-3xl font-bold">Create Assessment</h1>
                <p className="text-slate-400 text-sm sm:text-base">Design your personalized practice assessment</p>
            </div>


            {/* Progress Steps */}
            <div className="flex items-center justify-center gap-3 sm:gap-6">
                {[1, 2, 3].map((s) => (
                    <div key={s} className="flex items-center gap-3">
                        <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-2xl flex items-center justify-center font-black text-sm transition-all border-2 ${step >= s
                            ? 'bg-indigo-600 border-indigo-600 text-white shadow-xl shadow-indigo-100'
                            : 'bg-white text-slate-400 border-slate-100 shadow-sm'
                            }`}>
                            {s}
                        </div>
                        {s < 3 && <ChevronRight className={`w-5 h-5 ${step > s ? 'text-indigo-600' : 'text-slate-200'}`} />}
                    </div>
                ))}
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
                {/* Step 1: Subject Selection */}
                {step === 1 && (
                    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="text-center space-y-2">
                            <h2 className="text-2xl font-black text-slate-900 tracking-tight">Core Disciplines</h2>
                            <p className="text-slate-500 font-medium">Select a primary subject area for your assessment</p>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {subjects.map((subj) => (
                                <button
                                    key={subj.value}
                                    type="button"
                                    onClick={() => {
                                        setValue('subject', subj.value);
                                        setStep(2);
                                    }}
                                    className={`p-8 rounded-[2rem] border-2 transition-all text-left group hover:scale-[1.02] active:scale-[0.98] flex items-center gap-6 ${watchAll.subject === subj.value
                                        ? 'border-indigo-600 bg-white shadow-2xl shadow-indigo-50'
                                        : 'border-slate-100 bg-white hover:border-slate-200 shadow-sm'
                                        }`}
                                >
                                    <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${subj.color} flex items-center justify-center text-3xl group-hover:scale-110 transition-transform shadow-lg`}>
                                        {subj.icon}
                                    </div>
                                    <div>
                                        <p className="font-black text-slate-900 text-lg">{subj.label}</p>
                                        <p className="text-sm text-slate-400 font-medium">Standard NC Curriculum</p>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Step 2: Configuration */}
                {step === 2 && (
                    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="bg-white p-8 sm:p-12 rounded-[2.5rem] border border-slate-200 shadow-2xl shadow-slate-100/50 space-y-8">
                            <div className="space-y-2">
                                <h3 className="text-xl font-black text-slate-900 tracking-tight flex items-center gap-3">
                                    <Zap className="w-5 h-5 text-indigo-600" />
                                    Configure Assessment
                                </h3>
                                <p className="text-slate-500 font-medium text-sm">Refine the parameters for AI generation</p>
                            </div>

                            <hr className="border-slate-100" />

                            {/* Title */}
                            <div className="space-y-3">
                                <label className="block text-sm font-black text-slate-700 uppercase tracking-widest ml-1">Assessment Identity</label>
                                <input
                                    {...register('title')}
                                    placeholder="e.g., Mathematics Mastery: Algebraic Thinking"
                                    className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 focus:ring-4 focus:ring-indigo-50 focus:border-indigo-600 outline-none transition-all font-medium text-slate-900 placeholder-slate-400"
                                />
                                {errors.title && typeof errors.title.message === 'string' && <p className="text-rose-600 text-xs mt-1 font-bold ml-1">{errors.title.message}</p>}
                            </div>

                            {/* Grade & Standard */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                <div className="space-y-3">
                                    <label className="block text-sm font-black text-slate-700 uppercase tracking-widest ml-1">Grade Level</label>
                                    <select {...register('grade_level')} className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 outline-none font-medium text-slate-900 focus:ring-4 focus:ring-indigo-50 transition-all cursor-pointer appearance-none">
                                        {[3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(g => <option key={g} value={g}>NC Grade {g}</option>)}
                                    </select>
                                </div>
                                <div className="space-y-3">
                                    <label className="block text-sm font-black text-slate-700 uppercase tracking-widest ml-1">Focus Standard</label>
                                    <select {...register('standard_focus')} className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 outline-none font-medium text-slate-900 focus:ring-4 focus:ring-indigo-50 transition-all cursor-pointer appearance-none">
                                        {availableStandards.map((std, idx) => <option key={idx} value={std}>{std}</option>)}
                                    </select>
                                </div>
                            </div>

                            {/* Question Count & Difficulty */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                <div className="space-y-3">
                                    <label className="block text-sm font-black text-slate-700 uppercase tracking-widest ml-1">Total Questions</label>
                                    <input type="number" {...register('question_count')} min="5" max="50" className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 outline-none font-medium text-slate-900 focus:ring-4 focus:ring-indigo-50 transition-all" />
                                </div>
                                <div className="space-y-3">
                                    <label className="block text-sm font-black text-slate-700 uppercase tracking-widest ml-1">Academic Rigor</label>
                                    <select {...register('difficulty')} className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 outline-none font-medium text-slate-900 focus:ring-4 focus:ring-indigo-50 transition-all cursor-pointer appearance-none">
                                        <option value="easy">Foundational (Level 1-2)</option>
                                        <option value="medium">On-grade (Level 3-4)</option>
                                        <option value="hard">Rigorous (Level 5)</option>
                                    </select>
                                </div>
                            </div>

                            {/* Question Type & Study Mode */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4">
                                <div className="space-y-4">
                                    <label className="block text-sm font-black text-slate-700 uppercase tracking-widest ml-1">Response Type</label>
                                    <div className="grid grid-cols-2 gap-3">
                                        {['mcq', 'open_ended'].map((type) => (
                                            <button
                                                key={type}
                                                type="button"
                                                onClick={() => setValue('question_type', type)}
                                                className={`p-5 rounded-2xl border-2 transition-all flex flex-col items-center gap-2 group ${watchAll.question_type === type
                                                    ? 'border-indigo-600 bg-white shadow-lg'
                                                    : 'border-slate-50 bg-slate-50 hover:border-slate-100 text-slate-500'
                                                    }`}
                                            >
                                                <div className={`text-2xl transition-transform group-hover:scale-110 ${watchAll.question_type === type ? '' : 'grayscale opacity-50'}`}>
                                                    {type === 'mcq' ? '🔘' : '✏️'}
                                                </div>
                                                <p className={`font-black text-[10px] uppercase tracking-widest ${watchAll.question_type === type ? 'text-indigo-600' : 'text-slate-400'}`}>
                                                    {type === 'mcq' ? 'Multiple Choice' : 'Open Response'}
                                                </p>
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <label className="block text-sm font-black text-slate-700 uppercase tracking-widest ml-1">Clinical Environment</label>
                                    <div
                                        onClick={() => setValue('practice_mode', !watchAll.practice_mode)}
                                        className={`p-5 rounded-2xl border-2 transition-all cursor-pointer flex items-center justify-between group ${watchAll.practice_mode
                                            ? 'border-emerald-500 bg-white shadow-lg shadow-emerald-50'
                                            : 'border-slate-50 bg-slate-50 hover:border-slate-100'
                                            }`}
                                    >
                                        <div className="flex items-center gap-4 text-left">
                                            <div className={`text-2xl transition-all ${watchAll.practice_mode ? '' : 'grayscale opacity-50'}`}>
                                                {watchAll.practice_mode ? '🧘' : '📝'}
                                            </div>
                                            <div>
                                                <p className="font-black text-slate-900 text-sm tracking-tight">{watchAll.practice_mode ? 'Learning Practice' : 'Standardized Exam'}</p>
                                                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-tighter">
                                                    {watchAll.practice_mode ? 'Real-time Clinical Insights' : 'Formal Performance Metrics'}
                                                </p>
                                            </div>
                                        </div>
                                        <div className={`w-10 h-5 rounded-full relative transition-colors ${watchAll.practice_mode ? 'bg-emerald-500' : 'bg-slate-300'}`}>
                                            <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all shadow-sm ${watchAll.practice_mode ? 'right-1' : 'left-1'}`} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="flex flex-col sm:flex-row gap-4 pt-4">
                            <button
                                type="button"
                                onClick={() => setStep(1)}
                                className="order-2 sm:order-1 flex-1 py-4.5 px-8 rounded-2xl bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 transition-all font-black text-lg py-4 shadow-sm"
                            >
                                Back to Subject
                            </button>
                            <button
                                type="submit"
                                disabled={loading}
                                className="order-1 sm:order-2 flex-[2] bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-black py-4.5 px-10 rounded-2xl flex items-center justify-center gap-3 transition-all hover:scale-[1.02] active:scale-95 shadow-2xl shadow-indigo-100 text-lg py-4"
                            >
                                {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Sparkles className="w-6 h-6" />}
                                {loading ? 'Orchestrating AI Pipeline...' : 'Synthesize Assessment'}
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 3: Success */}
                {step === 3 && generatedTest && (
                    <div className="text-center space-y-6 animate-in fade-in zoom-in duration-500">
                        <div className="w-24 h-24 mx-auto rounded-3xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-2xl shadow-emerald-500/30">
                            <FileText className="w-12 h-12 text-white" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold mb-2">{generatedTest.title}</h2>
                            <p className="text-slate-400">{generatedTest.question_count} questions generated successfully!</p>
                        </div>
                        <div className="flex flex-col sm:flex-row gap-3 justify-center">
                            <button
                                type="button"
                                onClick={() => navigate(`/take/${generatedTest.id}`)}
                                className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/25 hover:scale-105 transition-transform"
                            >
                                <Brain className="w-5 h-5" />
                                Start Assessment
                            </button>
                            <button
                                type="button"
                                className="px-6 py-4 bg-white border border-slate-200 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-slate-50 transition-all shadow-sm"
                            >
                                <Download className="w-5 h-5" />
                                Download PDF
                            </button>
                        </div>
                        <button
                            type="button"
                            onClick={() => { setGeneratedTest(null); setStep(1); }}
                            className="text-slate-400 hover:text-white text-sm transition-colors"
                        >
                            Create Another Assessment
                        </button>
                    </div>
                )}
            </form>
        </div>
    );
};

export default CreateTest;
