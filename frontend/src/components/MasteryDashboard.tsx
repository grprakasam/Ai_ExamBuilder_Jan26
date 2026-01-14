import React from 'react';
import { TrendingUp, Target, Flame, BookOpen, CheckCircle2, AlertCircle } from 'lucide-react';

interface ConceptMastery {
    concept_id: string;
    name: string;
    current_level: number; // 0.0 to 1.0
    questions_attempted: number;
    questions_correct: number;
    streak_current: number;
    is_mastered: boolean;
    needs_review: boolean;
}

interface MasteryDashboardProps {
    concepts: ConceptMastery[];
    overallMastery: number;
    bestStreak: number;
    conceptsDueReview: number;
}

const MasteryDashboard: React.FC<MasteryDashboardProps> = ({
    concepts,
    overallMastery,
    bestStreak,
    conceptsDueReview,
}) => {
    const getMasteryColor = (level: number) => {
        if (level >= 0.8) return 'bg-green-500';
        if (level >= 0.6) return 'bg-blue-500';
        if (level >= 0.4) return 'bg-yellow-500';
        return 'bg-orange-500';
    };

    const getMasteryLabel = (level: number) => {
        if (level >= 0.8) return 'Mastered';
        if (level >= 0.6) return 'Proficient';
        if (level >= 0.4) return 'Developing';
        return 'Learning';
    };

    const mastered = concepts.filter(c => c.current_level >= 0.8).length;
    const proficient = concepts.filter(c => c.current_level >= 0.6 && c.current_level < 0.8).length;
    const developing = concepts.filter(c => c.current_level >= 0.4 && c.current_level < 0.6).length;
    const learning = concepts.filter(c => c.current_level < 0.4).length;

    return (
        <div className="space-y-6">
            {/* Header Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl p-6 text-white">
                    <div className="flex items-center gap-3 mb-2">
                        <Target className="w-6 h-6" />
                        <span className="text-sm font-bold uppercase tracking-wide opacity-90">Overall Mastery</span>
                    </div>
                    <div className="text-4xl font-black">{Math.round(overallMastery * 100)}%</div>
                    <div className="mt-2 text-sm opacity-90">{concepts.length} concepts tracked</div>
                </div>

                <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white">
                    <div className="flex items-center gap-3 mb-2">
                        <CheckCircle2 className="w-6 h-6" />
                        <span className="text-sm font-bold uppercase tracking-wide opacity-90">Mastered</span>
                    </div>
                    <div className="text-4xl font-black">{mastered}</div>
                    <div className="mt-2 text-sm opacity-90">concepts at 80%+</div>
                </div>

                <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-white">
                    <div className="flex items-center gap-3 mb-2">
                        <Flame className="w-6 h-6" />
                        <span className="text-sm font-bold uppercase tracking-wide opacity-90">Best Streak</span>
                    </div>
                    <div className="text-4xl font-black">{bestStreak}</div>
                    <div className="mt-2 text-sm opacity-90">consecutive correct</div>
                </div>

                <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
                    <div className="flex items-center gap-3 mb-2">
                        <BookOpen className="w-6 h-6" />
                        <span className="text-sm font-bold uppercase tracking-wide opacity-90">Due for Review</span>
                    </div>
                    <div className="text-4xl font-black">{conceptsDueReview}</div>
                    <div className="mt-2 text-sm opacity-90">concepts to practice</div>
                </div>
            </div>

            {/* Mastery Distribution */}
            <div className="bg-white rounded-2xl border-2 border-slate-200 p-6">
                <h3 className="text-lg font-bold text-slate-900 mb-4">Mastery Distribution</h3>
                <div className="space-y-3">
                    <div className="flex items-center gap-4">
                        <div className="w-32 text-sm font-bold text-slate-700">Mastered (80%+)</div>
                        <div className="flex-1 bg-slate-100 rounded-full h-8 overflow-hidden">
                            <div
                                className="bg-green-500 h-full flex items-center justify-end px-3 transition-all duration-500"
                                style={{ width: `${(mastered / concepts.length) * 100}%` }}
                            >
                                <span className="text-white text-sm font-bold">{mastered}</span>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="w-32 text-sm font-bold text-slate-700">Proficient (60-79%)</div>
                        <div className="flex-1 bg-slate-100 rounded-full h-8 overflow-hidden">
                            <div
                                className="bg-blue-500 h-full flex items-center justify-end px-3 transition-all duration-500"
                                style={{ width: `${(proficient / concepts.length) * 100}%` }}
                            >
                                <span className="text-white text-sm font-bold">{proficient}</span>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="w-32 text-sm font-bold text-slate-700">Developing (40-59%)</div>
                        <div className="flex-1 bg-slate-100 rounded-full h-8 overflow-hidden">
                            <div
                                className="bg-yellow-500 h-full flex items-center justify-end px-3 transition-all duration-500"
                                style={{ width: `${(developing / concepts.length) * 100}%` }}
                            >
                                <span className="text-white text-sm font-bold">{developing}</span>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="w-32 text-sm font-bold text-slate-700">Learning (0-39%)</div>
                        <div className="flex-1 bg-slate-100 rounded-full h-8 overflow-hidden">
                            <div
                                className="bg-orange-500 h-full flex items-center justify-end px-3 transition-all duration-500"
                                style={{ width: `${(learning / concepts.length) * 100}%` }}
                            >
                                <span className="text-white text-sm font-bold">{learning}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Concept List */}
            <div className="bg-white rounded-2xl border-2 border-slate-200 p-6">
                <h3 className="text-lg font-bold text-slate-900 mb-4">Your Concepts</h3>
                <div className="space-y-3">
                    {concepts.map((concept) => (
                        <div
                            key={concept.concept_id}
                            className="flex items-center gap-4 p-4 rounded-xl border-2 border-slate-100 hover:border-slate-200 transition-colors"
                        >
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                    <h4 className="font-bold text-slate-900">{concept.name}</h4>
                                    {concept.is_mastered && (
                                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                                    )}
                                    {concept.needs_review && (
                                        <AlertCircle className="w-5 h-5 text-orange-600" />
                                    )}
                                </div>
                                <div className="flex items-center gap-4 text-sm text-slate-600">
                                    <span>{concept.questions_correct} / {concept.questions_attempted} correct</span>
                                    {concept.streak_current > 0 && (
                                        <span className="flex items-center gap-1">
                                            <Flame className="w-4 h-4 text-orange-500" />
                                            {concept.streak_current} streak
                                        </span>
                                    )}
                                </div>
                            </div>
                            <div className="text-right">
                                <div className={`text-2xl font-black ${concept.current_level >= 0.8 ? 'text-green-600' :
                                        concept.current_level >= 0.6 ? 'text-blue-600' :
                                            concept.current_level >= 0.4 ? 'text-yellow-600' :
                                                'text-orange-600'
                                    }`}>
                                    {Math.round(concept.current_level * 100)}%
                                </div>
                                <div className="text-xs font-bold text-slate-500 uppercase">
                                    {getMasteryLabel(concept.current_level)}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default MasteryDashboard;
