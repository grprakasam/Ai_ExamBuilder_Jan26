import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SubjectProgress {
    subject: string;
    mastery: number; // 0-100
    testsCompleted: number;
}

interface ProgressState {
    streak: number;
    lastPracticeDate: string | null;
    totalQuestionsSolved: number;
    subjectMastery: SubjectProgress[];

    updateProgress: (subject: string, score: number, questionsCount: number) => void;
    incrementStreak: () => void;
}

export const useProgressStore = create<ProgressState>()(
    persist(
        (set, get) => ({
            streak: 0,
            lastPracticeDate: null,
            totalQuestionsSolved: 0,
            subjectMastery: [
                { subject: 'mathematics', mastery: 0, testsCompleted: 0 },
                { subject: 'english', mastery: 0, testsCompleted: 0 },
                { subject: 'science', mastery: 0, testsCompleted: 0 },
                { subject: 'social_studies', mastery: 0, testsCompleted: 0 },
            ],

            updateProgress: (subject, score, questionsCount) => {
                const now = new Date().toISOString().split('T')[0];
                const { lastPracticeDate, streak, subjectMastery, totalQuestionsSolved } = get();

                // Update Streak
                let newStreak = streak;
                if (!lastPracticeDate) {
                    newStreak = 1;
                } else {
                    const last = new Date(lastPracticeDate);
                    const today = new Date(now);
                    const diff = (today.getTime() - last.getTime()) / (1000 * 3600 * 24);

                    if (diff === 1) {
                        newStreak += 1;
                    } else if (diff > 1) {
                        newStreak = 1;
                    }
                }

                // Update Subject Mastery (rolling average)
                const newSubjectMastery = subjectMastery.map(sm => {
                    if (sm.subject === subject) {
                        const totalTests = sm.testsCompleted + 1;
                        const newMastery = Math.round((sm.mastery * sm.testsCompleted + score) / totalTests);
                        return { ...sm, mastery: newMastery, testsCompleted: totalTests };
                    }
                    return sm;
                });

                set({
                    streak: newStreak,
                    lastPracticeDate: now,
                    totalQuestionsSolved: totalQuestionsSolved + questionsCount,
                    subjectMastery: newSubjectMastery,
                });
            },

            incrementStreak: () => set((state) => ({ streak: state.streak + 1 })),
        }),
        {
            name: 'student-progress-storage',
        }
    )
);
