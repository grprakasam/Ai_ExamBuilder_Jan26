export type Subject = 'mathematics' | 'english' | 'science' | 'social_studies';
export type QuestionType = 'mcq' | 'open_ended';
export type Difficulty = 'easy' | 'medium' | 'hard';

export interface Question {
    id: string;
    sequence: number;
    question_text: string;
    question_type: QuestionType;
    options?: Record<string, string>;
    correct_answer: string;
    explanation?: string;
    cognitive_level?: string;
}

export interface Test {
    id: string;
    title: string;
    grade_level: number;
    subject: Subject;
    standard_focus: string;
    question_count: number;
    question_type: QuestionType;
    difficulty: Difficulty;
    created_at: string;
    questions?: Question[];
}

export interface AIFeedback {
    overall_summary: string;
    evaluations: {
        index: number;
        score: number;
        feedback: string;
        suggestion?: string;
    }[];
}

export interface SubmissionResult {
    score: number | null;
    correct_count: number;
    total_mcq: number;
    ai_feedback: AIFeedback;
}
