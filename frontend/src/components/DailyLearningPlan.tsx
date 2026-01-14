import React from 'react';
import { BookOpen, Clock, TrendingUp } from 'lucide-react';

interface DailyPlanProps {
    conceptsDue: Array<{
        concept_id: string;
        name: string;
        last_practiced: string;
        questions_to_review: number;
    }>;
    newConcept?: {
        concept_id: string;
        name: string;
        description: string;
    };
    goalQuestions: number;
    estimatedMinutes: number;
}

const DailyLearningPlan: React.FC<DailyPlanProps> = ({
    conceptsDue,
    newConcept,
    goalQuestions,
    estimatedMinutes,
}) => {
    const daysSince = (dateStr: string) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        return Math.floor(diff / (1000 * 60 * 60 * 24));
    };

    return (
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border-2 border-indigo-200 p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-black text-slate-900">📅 Today's Learning Plan</h2>
                <div className="flex items-center gap-2 text-slate-600">
                    <Clock className="w-5 h-5" />
                    <span className="font-bold">~{estimatedMinutes} min</span>
                </div>
            </div>

            {/* Due for Review */}
            {conceptsDue.length > 0 && (
                <div className="bg-white rounded-xl p-5 border-2 border-orange-200">
                    <div className="flex items-center gap-2 mb-4">
                        <div className="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center">
                            <TrendingUp className="w-5 h-5 text-orange-600" />
                        </div>
                        <h3 className="font-bold text-slate-900">🔄 Due for Review (keep your knowledge fresh!)</h3>
                    </div>
                    <div className="space-y-2">
                        {conceptsDue.map((concept) => (
                            <div
                                key={concept.concept_id}
                                className="flex items-center justify-between p-3 rounded-lg bg-orange-50 border border-orange-100"
                            >
                                <div>
                                    <div className="font-bold text-slate-900">{concept.name}</div>
                                    <div className="text-sm text-slate-600">
                                        {concept.questions_to_review} questions • Last seen: {daysSince(concept.last_practiced)} days ago
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Continue Learning */}
            {newConcept && (
                <div className="bg-white rounded-xl p-5 border-2 border-blue-200">
                    <div className="flex items-center gap-2 mb-4">
                        <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                            <BookOpen className="w-5 h-5 text-blue-600" />
                        </div>
                        <h3 className="font-bold text-slate-900">📚 Continue Learning</h3>
                    </div>
                    <div className="p-4 rounded-lg bg-blue-50 border border-blue-100">
                        <div className="font-bold text-slate-900 mb-1">{newConcept.name}</div>
                        <div className="text-sm text-slate-600 mb-3">{newConcept.description}</div>
                        <div className="text-xs text-blue-700 font-bold uppercase">Next lesson</div>
                    </div>
                </div>
            )}

            {/* Goal */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-5 text-white">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="text-sm font-bold uppercase tracking-wide opacity-90 mb-1">Your Goal Today</div>
                        <div className="text-3xl font-black">{goalQuestions} questions</div>
                    </div>
                    <button className="px-6 py-3 bg-white text-indigo-600 rounded-xl font-bold hover:bg-indigo-50 transition-colors">
                        Start Today's Session
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DailyLearningPlan;
