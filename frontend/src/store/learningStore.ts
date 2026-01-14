import { create } from 'zustand';
import { LearningMode, LearningSessionState } from '../types';

interface LearningStore extends LearningSessionState {
    // Actions
    setMode: (mode: LearningMode) => void;
    setCurrentQuestion: (index: number) => void;
    setAnswer: (questionIndex: number, answer: string) => void;
    toggleMarkForReview: (questionIndex: number) => void;
    recordQuestionTime: (questionIndex: number, seconds: number) => void;
    resetSession: () => void;

    // Feedback state
    showFeedback: boolean;
    showHint: boolean;
    setShowFeedback: (show: boolean) => void;
    setShowHint: (show: boolean) => void;
}

const initialState: LearningSessionState = {
    mode: 'learn',
    current_question_index: 0,
    answers: {},
    marked_for_review: new Set(),
    time_started: new Date(),
    time_per_question: {},
};

export const useLearningStore = create<LearningStore>((set) => ({
    ...initialState,
    showFeedback: false,
    showHint: false,

    setMode: (mode) => set({ mode }),

    setCurrentQuestion: (index) => set({
        current_question_index: index,
        showFeedback: false,
        showHint: false,
    }),

    setAnswer: (questionIndex, answer) => set((state) => ({
        answers: { ...state.answers, [questionIndex]: answer },
    })),

    toggleMarkForReview: (questionIndex) => set((state) => {
        const newMarked = new Set(state.marked_for_review);
        if (newMarked.has(questionIndex)) {
            newMarked.delete(questionIndex);
        } else {
            newMarked.add(questionIndex);
        }
        return { marked_for_review: newMarked };
    }),

    recordQuestionTime: (questionIndex, seconds) => set((state) => ({
        time_per_question: { ...state.time_per_question, [questionIndex]: seconds },
    })),

    setShowFeedback: (show) => set({ showFeedback: show }),
    setShowHint: (show) => set({ showHint: show }),

    resetSession: () => set({
        ...initialState,
        time_started: new Date(),
        showFeedback: false,
        showHint: false,
    }),
}));
