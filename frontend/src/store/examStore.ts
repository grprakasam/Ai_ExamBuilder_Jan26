import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ExamState {
    selectedExam: string | null;
    examName: string | null;
    examColor: string | null;
    setExam: (examId: string, examName: string, examColor: string) => void;
    clearExam: () => void;
}

export const useExamStore = create<ExamState>()(
    persist(
        (set) => ({
            selectedExam: null,
            examName: null,
            examColor: null,
            setExam: (examId, examName, examColor) =>
                set({ selectedExam: examId, examName, examColor }),
            clearExam: () =>
                set({ selectedExam: null, examName: null, examColor: null }),
        }),
        {
            name: 'exam-storage',
        }
    )
);
