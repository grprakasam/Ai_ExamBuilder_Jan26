export type Subject = 'mathematics' | 'english' | 'science' | 'social_studies';
export type QuestionType = 'mcq' | 'open_ended' | 'mixed';
export type Difficulty = 'easy' | 'medium' | 'hard';

// Learning Modes
export type LearningMode = 'learn' | 'practice' | 'assessment';

// Bloom's Taxonomy Levels
export type BloomLevel = 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create';

export interface Question {
    id: string;
    sequence: number;
    question_text: string;
    question_type: QuestionType;
    options?: Record<string, string>;
    correct_answer: string;

    // Legacy fields (backward compatibility)
    explanation?: string;
    cognitive_level?: string;

    // Learning-Centered Fields
    concept_ids?: string[];
    prerequisite_concepts?: string[];
    learning_objective?: string;
    bloom_level?: BloomLevel;
    difficulty_score?: number; // 0.0-1.0

    // Rich Feedback
    explanation_correct?: string;
    explanation_wrong?: Record<string, string>; // {"A": "why wrong", "B": "why wrong"}
    common_misconceptions?: string[];
    worked_example?: string;
    hint?: string;

    // Analytics (read-only)
    times_attempted?: number;
    times_correct?: number;
    avg_time_seconds?: number;
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

// Learning Session State
export interface LearningSessionState {
    mode: LearningMode;
    current_question_index: number;
    answers: Record<number, string>; // question index -> answer
    marked_for_review: Set<number>;
    time_started: Date;
    time_per_question: Record<number, number>; // seconds spent
}
