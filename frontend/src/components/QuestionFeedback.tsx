import React from 'react';
import { CheckCircle2, XCircle, Lightbulb, BookOpen, AlertCircle } from 'lucide-react';
import { Question } from '../types';

interface QuestionFeedbackProps {
    question: Question;
    userAnswer: string;
    isCorrect: boolean;
    showHint?: boolean;
    onTryAgain?: () => void;
    onShowHint?: () => void;
}

const QuestionFeedback: React.FC<QuestionFeedbackProps> = ({
    question,
    userAnswer,
    isCorrect,
    showHint = false,
    onTryAgain,
    onShowHint,
}) => {
    return (
        <div className="space-y-4 mt-6">
            {/* Feedback Header */}
            <div className={`
                p-4 rounded-xl border-2 flex items-start gap-3
                ${isCorrect
                    ? 'bg-green-50 border-green-200'
                    : 'bg-orange-50 border-orange-200'
                }
            `}>
                {isCorrect ? (
                    <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
                ) : (
                    <XCircle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-0.5" />
                )}
                <div className="flex-1">
                    <h4 className={`font-bold text-base mb-1 ${isCorrect ? 'text-green-900' : 'text-orange-900'}`}>
                        {isCorrect ? "Excellent! You've got this concept." : "Not quite - let's understand why."}
                    </h4>
                    <p className={`text-sm ${isCorrect ? 'text-green-700' : 'text-orange-700'}`}>
                        {isCorrect
                            ? "Your practice is paying off! Keep building mastery."
                            : "This is a common challenge. Here's the key insight..."
                        }
                    </p>
                </div>
            </div>

            {/* Correct Answer Explanation */}
            {question.explanation_correct && (
                <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
                    <div className="flex items-start gap-3">
                        <BookOpen className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                        <div>
                            <h5 className="font-bold text-blue-900 mb-2">Why {question.correct_answer} is correct:</h5>
                            <p className="text-sm text-blue-800">{question.explanation_correct}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Wrong Answer Explanation */}
            {!isCorrect && question.explanation_wrong && question.explanation_wrong[userAnswer] && (
                <div className="bg-orange-50 border-2 border-orange-200 rounded-xl p-4">
                    <div className="flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                        <div>
                            <h5 className="font-bold text-orange-900 mb-2">Why {userAnswer} is not correct:</h5>
                            <p className="text-sm text-orange-800">{question.explanation_wrong[userAnswer]}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Common Misconceptions */}
            {!isCorrect && question.common_misconceptions && question.common_misconceptions.length > 0 && (
                <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-4">
                    <h5 className="font-bold text-yellow-900 mb-2 flex items-center gap-2">
                        <AlertCircle className="w-5 h-5" />
                        Common Mistakes to Avoid:
                    </h5>
                    <ul className="space-y-1 text-sm text-yellow-800">
                        {question.common_misconceptions.map((misconception, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                                <span className="text-yellow-600 mt-0.5">•</span>
                                <span>{misconception}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Worked Example */}
            {question.worked_example && (
                <div className="bg-slate-50 border-2 border-slate-200 rounded-xl p-4">
                    <h5 className="font-bold text-slate-900 mb-2">Step-by-Step Solution:</h5>
                    <pre className="text-sm text-slate-800 whitespace-pre-wrap font-mono bg-white p-3 rounded border border-slate-200">
                        {question.worked_example}
                    </pre>
                </div>
            )}

            {/* Hint (if requested) */}
            {showHint && question.hint && (
                <div className="bg-indigo-50 border-2 border-indigo-200 rounded-xl p-4">
                    <div className="flex items-start gap-3">
                        <Lightbulb className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                        <div>
                            <h5 className="font-bold text-indigo-900 mb-2">Hint:</h5>
                            <p className="text-sm text-indigo-800">{question.hint}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3 pt-2">
                {!isCorrect && onTryAgain && (
                    <button
                        onClick={onTryAgain}
                        className="px-4 py-2 bg-orange-600 text-white rounded-lg font-semibold hover:bg-orange-700 transition-colors"
                    >
                        Try Again
                    </button>
                )}
                {!showHint && question.hint && onShowHint && (
                    <button
                        onClick={onShowHint}
                        className="px-4 py-2 bg-indigo-100 text-indigo-700 rounded-lg font-semibold hover:bg-indigo-200 transition-colors flex items-center gap-2"
                    >
                        <Lightbulb className="w-4 h-4" />
                        Show Hint
                    </button>
                )}
            </div>
        </div>
    );
};

export default QuestionFeedback;
