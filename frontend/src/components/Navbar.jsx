import React from 'react';
import { Package, Bell, LogOut, LayoutDashboard, FileText, ShoppingBag } from 'lucide-react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

export default function Navbar() {
    const navigate = useNavigate();
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    return (
        <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
            {/* Maximum breadth container with larger edge padding */}
            <div className="w-full px-6 lg:px-16 mx-auto">
                <div className="flex justify-between items-center h-20">

                    {/* Far Left: Logo & Brand */}
                    <div className="flex items-center gap-3 cursor-pointer shrink-0" onClick={() => navigate('/wizard')}>
                        <div className="p-2 bg-indigo-600 rounded-lg shadow-sm">
                            <Package className="w-7 h-7 text-white" />
                        </div>
                        <span className="text-2xl font-bold text-slate-900 tracking-tight">PackGenius</span>
                    </div>

                    {/* Middle: Main Navigation Links - Increased Font Size */}
                    <div className="hidden md:flex items-center space-x-4">
                        <Link
                            to="/wizard"
                            className={`flex items-center px-5 py-2.5 rounded-lg text-base font-semibold transition-all duration-200 ${isActive('/wizard') ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`}
                        >
                            <LayoutDashboard className="w-5 h-5 mr-2" />
                            New Analysis
                        </Link>
                        <Link
                            to="/results"
                            className={`flex items-center px-5 py-2.5 rounded-lg text-base font-semibold transition-all duration-200 ${isActive('/results') ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`}
                        >
                            <FileText className="w-5 h-5 mr-2" />
                            My Reports
                        </Link>
                        <Link
                            to="/marketplace"
                            className={`flex items-center px-5 py-2.5 rounded-lg text-base font-semibold transition-all duration-200 ${isActive('/marketplace') ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`}
                        >
                            <ShoppingBag className="w-5 h-5 mr-2" />
                            Vendor Marketplace
                        </Link>
                    </div>

                    {/* Far Right: Profile & Actions */}
                    <div className="flex items-center space-x-6 shrink-0">
                        <button className="text-slate-500 hover:text-indigo-600 transition-colors relative">
                            <Bell className="w-6 h-6" />
                            <span className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-red-500 rounded-full border-2 border-white shadow-sm"></span>
                        </button>

                        <div className="h-8 w-px bg-slate-200"></div>

                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-base shadow-sm ring-2 ring-indigo-50">
                                AD
                            </div>
                            <button
                                onClick={() => navigate('/login')}
                                className="text-slate-500 hover:text-red-600 transition-colors p-1"
                                title="Log out"
                            >
                                <LogOut className="w-6 h-6" />
                            </button>
                        </div>
                    </div>

                </div>
            </div>
        </nav>
    );
}