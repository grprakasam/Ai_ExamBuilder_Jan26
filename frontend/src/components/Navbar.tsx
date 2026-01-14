import React, { useState } from 'react';
import { useNavigate, NavLink } from 'react-router-dom';
import { LayoutDashboard, FilePlus, GraduationCap, Menu, X } from 'lucide-react';

const Navbar: React.FC = () => {
    const navigate = useNavigate();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const navItems = [
        { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/create', icon: FilePlus, label: 'Create' },
    ];

    return (
        <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50 safe-area-inset">
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
                <div className="h-16 flex items-center justify-between gap-4">
                    {/* Logo */}
                    <div
                        className="flex items-center gap-2.5 cursor-pointer group"
                        onClick={() => navigate('/dashboard')}
                    >
                        <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow-md shadow-indigo-200 group-hover:scale-105 transition-transform">
                            <GraduationCap className="w-5 h-5 text-white" />
                        </div>
                        <div className="hidden sm:block">
                            <span className="text-lg font-bold text-slate-900">
                                EOG Prep
                            </span>
                        </div>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-1">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                className={({ isActive }) => `
                                    flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
                                    ${isActive
                                        ? 'bg-slate-100 text-indigo-600'
                                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                                    }
                                `}
                            >
                                <item.icon className="w-4.5 h-4.5" />
                                {item.label}
                            </NavLink>
                        ))}
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className="md:hidden p-2 rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors"
                    >
                        {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden border-t border-slate-200 bg-white animate-in slide-in-from-top duration-200">
                    <div className="p-4 space-y-1">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                onClick={() => setMobileMenuOpen(false)}
                                className={({ isActive }) => `
                                    flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all
                                    ${isActive
                                        ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-100'
                                        : 'text-slate-600 hover:bg-slate-50'
                                    }
                                `}
                            >
                                <item.icon className="w-5 h-5" />
                                {item.label}
                            </NavLink>
                        ))}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
