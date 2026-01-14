import React from 'react';
import { GraduationCap, Stethoscope, Cpu, BookOpen, School, Building2, Globe, Award } from 'lucide-react';

interface ExamStandard {
    id: string;
    name: string;
    fullName: string;
    description: string;
    icon: React.ReactNode;
    color: string;
    gradient: string;
    region: string;
    subjects: string[];
}

const examStandards: ExamStandard[] = [
    {
        id: 'ncdpi',
        name: 'NCDPI',
        fullName: 'North Carolina End-of-Grade',
        description: 'K-12 standardized assessments for North Carolina students',
        icon: <GraduationCap className="w-12 h-12" />,
        color: 'blue',
        gradient: 'from-blue-500 to-blue-700',
        region: 'United States',
        subjects: ['Math', 'Reading', 'Science']
    },
    {
        id: 'neet',
        name: 'NEET',
        fullName: 'National Eligibility Entrance Test',
        description: 'Medical entrance examination for MBBS/BDS admissions in India',
        icon: <Stethoscope className="w-12 h-12" />,
        color: 'green',
        gradient: 'from-green-500 to-green-700',
        region: 'India',
        subjects: ['Physics', 'Chemistry', 'Biology']
    },
    {
        id: 'jee',
        name: 'JEE',
        fullName: 'Joint Entrance Examination',
        description: 'Engineering entrance exam for IITs, NITs, and other institutions',
        icon: <Cpu className="w-12 h-12" />,
        color: 'orange',
        gradient: 'from-orange-500 to-orange-700',
        region: 'India',
        subjects: ['Physics', 'Chemistry', 'Mathematics']
    },
    {
        id: 'cbse',
        name: 'CBSE',
        fullName: 'Central Board of Secondary Education',
        description: 'National board examinations for classes 10 and 12',
        icon: <BookOpen className="w-12 h-12" />,
        color: 'purple',
        gradient: 'from-purple-500 to-purple-700',
        region: 'India',
        subjects: ['All Subjects']
    },
    {
        id: 'icse',
        name: 'ICSE',
        fullName: 'Indian Certificate of Secondary Education',
        description: 'Private board examinations with comprehensive curriculum',
        icon: <School className="w-12 h-12" />,
        color: 'teal',
        gradient: 'from-teal-500 to-teal-700',
        region: 'India',
        subjects: ['All Subjects']
    },
    {
        id: 'tn_govt',
        name: 'TN Govt',
        fullName: 'Tamil Nadu Government Exams',
        description: 'State board examinations for Tamil Nadu students',
        icon: <Building2 className="w-12 h-12" />,
        color: 'red',
        gradient: 'from-red-500 to-red-700',
        region: 'India (Tamil Nadu)',
        subjects: ['All Subjects', 'Tamil']
    },
    {
        id: 'sat',
        name: 'SAT',
        fullName: 'Scholastic Assessment Test',
        description: 'Standardized test for college admissions in the US',
        icon: <Globe className="w-12 h-12" />,
        color: 'indigo',
        gradient: 'from-indigo-500 to-indigo-700',
        region: 'United States',
        subjects: ['Math', 'Reading', 'Writing']
    },
    {
        id: 'act',
        name: 'ACT',
        fullName: 'American College Testing',
        description: 'Alternative standardized test for US college admissions',
        icon: <Award className="w-12 h-12" />,
        color: 'rose',
        gradient: 'from-rose-500 to-rose-700',
        region: 'United States',
        subjects: ['English', 'Math', 'Reading', 'Science']
    }
];

interface ExamSelectorProps {
    onSelectExam: (examId: string) => void;
}

const ExamSelector: React.FC<ExamSelectorProps> = ({ onSelectExam }) => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-12 px-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-5xl font-black text-slate-900 mb-4">
                        Choose Your Exam
                    </h1>
                    <p className="text-xl text-slate-600 max-w-2xl mx-auto">
                        Select your target examination to access personalized practice tests,
                        adaptive learning, and comprehensive preparation materials
                    </p>
                </div>

                {/* Exam Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {examStandards.map((exam) => (
                        <div
                            key={exam.id}
                            className="group relative bg-white rounded-2xl border-2 border-slate-200 hover:border-slate-300 transition-all duration-300 hover:shadow-2xl hover:scale-105 cursor-pointer overflow-hidden"
                            onClick={() => onSelectExam(exam.id)}
                        >
                            {/* Gradient Background */}
                            <div className={`absolute inset-0 bg-gradient-to-br ${exam.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />

                            {/* Content */}
                            <div className="relative p-6 flex flex-col h-full">
                                {/* Icon */}
                                <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${exam.gradient} flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform duration-300`}>
                                    {exam.icon}
                                </div>

                                {/* Exam Name */}
                                <h3 className="text-2xl font-black text-slate-900 mb-1">
                                    {exam.name}
                                </h3>
                                <p className="text-sm font-bold text-slate-500 mb-3">
                                    {exam.fullName}
                                </p>

                                {/* Description */}
                                <p className="text-sm text-slate-600 mb-4 flex-grow">
                                    {exam.description}
                                </p>

                                {/* Region Badge */}
                                <div className="flex items-center gap-2 mb-3">
                                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">
                                        📍 {exam.region}
                                    </span>
                                </div>

                                {/* Subjects */}
                                <div className="flex flex-wrap gap-1 mb-4">
                                    {exam.subjects.slice(0, 3).map((subject, idx) => (
                                        <span
                                            key={idx}
                                            className="text-xs px-2 py-1 bg-slate-100 text-slate-700 rounded-full font-medium"
                                        >
                                            {subject}
                                        </span>
                                    ))}
                                    {exam.subjects.length > 3 && (
                                        <span className="text-xs px-2 py-1 bg-slate-100 text-slate-700 rounded-full font-medium">
                                            +{exam.subjects.length - 3}
                                        </span>
                                    )}
                                </div>

                                {/* Select Button */}
                                <button className={`w-full py-3 rounded-xl bg-gradient-to-r ${exam.gradient} text-white font-bold hover:shadow-lg transition-all duration-300 group-hover:scale-105`}>
                                    Select {exam.name}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Footer Info */}
                <div className="mt-12 text-center">
                    <p className="text-slate-600">
                        Not sure which exam to choose?
                        <a href="#" className="text-indigo-600 font-bold hover:underline ml-2">
                            View Comparison Guide
                        </a>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ExamSelector;
