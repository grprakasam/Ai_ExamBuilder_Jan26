import React from 'react';
import { Target, TrendingUp, AlertTriangle, CheckCircle2, BookOpen, ArrowRight } from 'lucide-react';

interface LearningProfileProps {
    overallMastery: number;
    conceptsAssessed: number;
    mastered: string[];
    proficient: string[];
    needsWork: string[];
    recommendedStart: string | null;
    onStartLearning: () => void;
}

const LearningProfile: React.FC<LearningProfileProps> = ({
    overallMastery,
    conceptsAssessed,
    mastered,
    proficient,
    needsWork,
    recommendedStart,
    onStartLearning,
}) => {
    const getConceptName = (conceptId: string) => {
        // Convert concept_id to readable name
        const parts = conceptId.split('.');
        return parts[parts.length - 1]
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6 py-8">
            {/* Header */}
            <div className="text-center space-y-3">
                <h1 className="text-3xl font-black text-slate-900">📊 Your Learning Profile</h1>
                <p className="text-slate-600 text-lg">
                    We've analyzed your current knowledge to create a personalized learning path
                </p>
            </div>

            {/* Overall Score */}
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-8 text-white text-center">
                <div className="flex items-center justify-center gap-3 mb-3">
                    <Target className="w-8 h-8" />
                    <span className="text-lg font-bold uppercase tracking-wide">Overall Mastery</span>
                </div>
                <div className="text-6xl font-black mb-2">{Math.round(overallMastery * 100)}%</div>
                <div className="text-lg opacity-90">Based on {conceptsAssessed} concepts assessed</div>
            </div>

            {/* Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Mastered */}
                <div className="bg-green-50 border-2 border-green-200 rounded-2xl p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <CheckCircle2 className="w-6 h-6 text-green-600" />
                        <h3 className="font-bold text-green-900">Mastered (80%+)</h3>
                    </div>
                    <div className="text-4xl font-black text-green-600 mb-3">{mastered.length}</div>
                    {mastered.length > 0 && (
                        <div className="space-y-1">
                            {mastered.slice(0, 3).map((conceptId) => (
                                <div key={conceptId} className="text-sm text-green-700 font-medium">
                                    ✓ {getConceptName(conceptId)}
                                </div>
                            ))}
                            {mastered.length > 3 && (
                                <div className="text-xs text-green-600 italic">
                                    +{mastered.length - 3} more
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Proficient */}
                <div className="bg-blue-50 border-2 border-blue-200 rounded-2xl p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <TrendingUp className="w-6 h-6 text-blue-600" />
                        <h3 className="font-bold text-blue-900">Proficient (60-79%)</h3>
                    </div>
                    <div className="text-4xl font-black text-blue-600 mb-3">{proficient.length}</div>
                    {proficient.length > 0 && (
                        <div className="space-y-1">
                            {proficient.slice(0, 3).map((conceptId) => (
                                <div key={conceptId} className="text-sm text-blue-700 font-medium">
                                    • {getConceptName(conceptId)}
                                </div>
                            ))}
                            {proficient.length > 3 && (
                                <div className="text-xs text-blue-600 italic">
                                    +{proficient.length - 3} more
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Needs Work */}
                <div className="bg-orange-50 border-2 border-orange-200 rounded-2xl p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <AlertTriangle className="w-6 h-6 text-orange-600" />
                        <h3 className="font-bold text-orange-900">Needs Work (&lt;60%)</h3>
                    </div>
                    <div className="text-4xl font-black text-orange-600 mb-3">{needsWork.length}</div>
                    {needsWork.length > 0 && (
                        <div className="space-y-1">
                            {needsWork.slice(0, 3).map((conceptId) => (
                                <div key={conceptId} className="text-sm text-orange-700 font-medium">
                                    ⚠ {getConceptName(conceptId)}
                                </div>
                            ))}
                            {needsWork.length > 3 && (
                                <div className="text-xs text-orange-600 italic">
                                    +{needsWork.length - 3} more
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Recommended Starting Point */}
            {recommendedStart && (
                <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-2xl p-8">
                    <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-xl bg-indigo-600 flex items-center justify-center flex-shrink-0">
                            <BookOpen className="w-6 h-6 text-white" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-xl font-bold text-slate-900 mb-2">
                                🎯 Recommended Starting Point
                            </h3>
                            <p className="text-slate-600 mb-4">
                                Based on your diagnostic results, we recommend starting with:
                            </p>
                            <div className="bg-white rounded-xl p-4 border-2 border-indigo-200 mb-4">
                                <div className="text-2xl font-black text-indigo-600 mb-1">
                                    {getConceptName(recommendedStart)}
                                </div>
                                <div className="text-sm text-slate-600">
                                    This foundational concept will help you build mastery in related topics
                                </div>
                            </div>
                            <button
                                onClick={onStartLearning}
                                className="w-full px-6 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-bold text-lg hover:from-indigo-700 hover:to-purple-700 transition-all flex items-center justify-center gap-3 shadow-lg hover:shadow-xl"
                            >
                                Start Learning Path
                                <ArrowRight className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* What's Next */}
            <div className="bg-white border-2 border-slate-200 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-slate-900 mb-4">What Happens Next?</h3>
                <div className="space-y-3">
                    <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0 font-bold text-indigo-600">
                            1
                        </div>
                        <div>
                            <div className="font-bold text-slate-900">Personalized Practice</div>
                            <div className="text-sm text-slate-600">
                                You'll practice concepts in the optimal order, starting with foundations
                            </div>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0 font-bold text-indigo-600">
                            2
                        </div>
                        <div>
                            <div className="font-bold text-slate-900">Adaptive Difficulty</div>
                            <div className="text-sm text-slate-600">
                                Questions adjust to your level - not too easy, not too hard
                            </div>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0 font-bold text-indigo-600">
                            3
                        </div>
                        <div>
                            <div className="font-bold text-slate-900">Spaced Repetition</div>
                            <div className="text-sm text-slate-600">
                                We'll remind you to review concepts at the perfect time for retention
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LearningProfile;
