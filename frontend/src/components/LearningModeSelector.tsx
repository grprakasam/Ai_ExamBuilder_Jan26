import React from 'react';
import { GraduationCap, Dumbbell, ClipboardCheck } from 'lucide-react';
import { LearningMode } from '../types';

interface LearningModeSelectorProps {
    selectedMode: LearningMode;
    onModeChange: (mode: LearningMode) => void;
}

const LearningModeSelector: React.FC<LearningModeSelectorProps> = ({ selectedMode, onModeChange }) => {
    const modes = [
        {
            id: 'learn' as LearningMode,
            icon: GraduationCap,
            title: 'Learn Mode',
            description: 'Hints available • Unlimited retries • Instant feedback',
            color: 'bg-blue-50 border-blue-200 text-blue-700',
            activeColor: 'bg-blue-600 text-white border-blue-600',
        },
        {
            id: 'practice' as LearningMode,
            icon: Dumbbell,
            title: 'Practice Mode',
            description: 'Instant feedback • Build mastery • Track progress',
            color: 'bg-green-50 border-green-200 text-green-700',
            activeColor: 'bg-green-600 text-white border-green-600',
        },
        {
            id: 'assessment' as LearningMode,
            icon: ClipboardCheck,
            title: 'Assessment Mode',
            description: 'Timed • Formal scoring • Feedback at end',
            color: 'bg-purple-50 border-purple-200 text-purple-700',
            activeColor: 'bg-purple-600 text-white border-purple-600',
        },
    ];

    return (
        <div className="space-y-3">
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wide">Choose Your Learning Mode</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {modes.map((mode) => {
                    const Icon = mode.icon;
                    const isActive = selectedMode === mode.id;

                    return (
                        <button
                            key={mode.id}
                            onClick={() => onModeChange(mode.id)}
                            className={`
                                p-4 rounded-xl border-2 transition-all text-left
                                ${isActive ? mode.activeColor : mode.color}
                                hover:shadow-md active:scale-95
                            `}
                        >
                            <div className="flex items-start gap-3">
                                <Icon className={`w-6 h-6 flex-shrink-0 ${isActive ? 'text-white' : ''}`} />
                                <div className="flex-1 min-w-0">
                                    <h4 className={`font-bold text-base mb-1 ${isActive ? 'text-white' : ''}`}>
                                        {mode.title}
                                    </h4>
                                    <p className={`text-xs ${isActive ? 'text-white/90' : 'opacity-75'}`}>
                                        {mode.description}
                                    </p>
                                </div>
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
};

export default LearningModeSelector;
