import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { GraduationCap, Lock, Mail, User, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import api from '../services/api';

const Signup: React.FC = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    const { register, handleSubmit, formState: { errors } } = useForm();

    const onSubmit = async (data: any) => {
        setLoading(true);
        setError(null);
        try {
            await api.post('/auth/signup', {
                email: data.email,
                password: data.password,
                full_name: data.full_name,
            });
            setSuccess(true);
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Account creation failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="min-h-[85vh] flex items-center justify-center p-6 animate-in fade-in zoom-in duration-500">
                <div className="max-w-md w-full space-y-8 bg-white p-12 rounded-[2.5rem] border border-emerald-100 shadow-2xl shadow-emerald-50 text-center">
                    <div className="w-24 h-24 bg-emerald-50 rounded-full flex items-center justify-center border border-emerald-100 mx-auto mb-2">
                        <CheckCircle2 className="w-14 h-14 text-emerald-600" />
                    </div>
                    <div className="space-y-2">
                        <h2 className="text-3xl font-black text-slate-900 tracking-tight">Account Verified</h2>
                        <p className="text-slate-500 font-medium">Your secure student profile is active. Preparing your personalized learning dashboard...</p>
                    </div>
                    <div className="h-1.5 w-full bg-slate-50 rounded-full overflow-hidden mt-6">
                        <div className="h-full bg-emerald-600 animate-progress origin-left"></div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-[85vh] flex items-center justify-center p-6 animate-in fade-in slide-in-from-bottom duration-500">
            <div className="max-w-md w-full space-y-10 bg-white p-10 sm:p-12 rounded-[2.5rem] border border-slate-200 shadow-2xl shadow-slate-200/50">
                <div className="text-center space-y-3">
                    <div className="inline-flex items-center justify-center p-4 bg-indigo-50 rounded-2xl border border-indigo-100 mb-2">
                        <GraduationCap className="w-12 h-12 text-indigo-600" />
                    </div>
                    <h1 className="text-3xl font-black text-slate-900 tracking-tight">Join the Academy</h1>
                    <p className="text-slate-500 font-medium">Start your personalized EOG practice journey.</p>
                </div>

                {error && (
                    <div className="bg-rose-50 border border-rose-100 text-rose-600 p-4 rounded-2xl flex items-center gap-3 text-sm font-bold animate-in shake duration-300">
                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    <div className="space-y-5">
                        <div className="space-y-2">
                            <label className="block text-sm font-bold text-slate-700 uppercase tracking-wider ml-1">Full Name</label>
                            <div className="relative">
                                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    {...register('full_name', { required: 'Full name is required' })}
                                    placeholder="Alex Johnson"
                                    className="w-full bg-slate-50 border border-slate-100 rounded-2xl pl-12 pr-5 py-4 focus:ring-4 focus:ring-indigo-50 focus:border-indigo-600 outline-none transition-all font-medium text-slate-900 placeholder-slate-400"
                                />
                            </div>
                            {errors.full_name?.message && typeof errors.full_name.message === 'string' && (
                                <p className="text-rose-600 text-xs mt-1 font-bold ml-1">{errors.full_name.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <label className="block text-sm font-bold text-slate-700 uppercase tracking-wider ml-1">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    {...register('email', { required: 'Email is required' })}
                                    type="email"
                                    placeholder="student@example.com"
                                    className="w-full bg-slate-50 border border-slate-100 rounded-2xl pl-12 pr-5 py-4 focus:ring-4 focus:ring-indigo-50 focus:border-indigo-600 outline-none transition-all font-medium text-slate-900 placeholder-slate-400"
                                />
                            </div>
                            {errors.email?.message && typeof errors.email.message === 'string' && (
                                <p className="text-rose-600 text-xs mt-1 font-bold ml-1">{errors.email.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <label className="block text-sm font-bold text-slate-700 uppercase tracking-wider ml-1">Secure Passphrase</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    {...register('password', {
                                        required: 'Passphrase is required',
                                        minLength: { value: 8, message: 'Must be at least 8 characters' }
                                    })}
                                    type="password"
                                    placeholder="••••••••"
                                    className="w-full bg-slate-50 border border-slate-100 rounded-2xl pl-12 pr-5 py-4 focus:ring-4 focus:ring-indigo-50 focus:border-indigo-600 outline-none transition-all font-medium text-slate-900 placeholder-slate-400"
                                />
                            </div>
                            {errors.password?.message && typeof errors.password.message === 'string' && (
                                <p className="text-rose-600 text-xs mt-1 font-bold ml-1">{errors.password.message}</p>
                            )}
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-black py-4.5 rounded-2xl flex items-center justify-center gap-3 transition-all hover:scale-[1.02] active:scale-95 shadow-xl shadow-indigo-100 text-lg py-4"
                    >
                        {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : 'Create Account Now'}
                    </button>
                </form>

                <div className="text-center pt-2">
                    <p className="text-slate-500 font-medium">
                        Already have a passphrase? {' '}
                        <Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-black transition-colors underline underline-offset-4">
                            Sign In
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Signup;
