import React from 'react';

const Footer: React.FC = () => {
    return (
        <footer className="border-t border-slate-100 bg-white py-8 px-4 mt-auto">
            <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-slate-500">
                <p>© 2026 EduApp Platform. Advanced Learning Systems.</p>
                <p className="text-slate-400">Powered by AI • Built for Excellence</p>
            </div>
        </footer>
    );
};

export default Footer;
