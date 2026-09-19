import React, { useState } from 'react';
import { Package, Leaf, Factory, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
    const [role, setRole] = useState('producer');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    // New state for toggling password visibility
    const [showPassword, setShowPassword] = useState(false);

    const navigate = useNavigate();

    // Function to show password for 3 seconds
    const handleShowPassword = () => {
        setShowPassword(true);
        setTimeout(() => {
            setShowPassword(false);
        }, 3000);
    };

    const handleLogin = (e) => {
        e.preventDefault();
        setError('');

        if (!email.trim() || !password.trim()) {
            setError('Please enter both email and password.');
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setError('Please enter a valid email address (e.g., name@company.com).');
            return;
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters long.');
            return;
        }

        if (email === 'admin@packgenius.com' && password === 'password123') {
            navigate('/wizard');
        } else {
            setError('Invalid credentials. (Hint: use admin@packgenius.com / password123)');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8">

                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-12 h-12 bg-indigo-100 rounded-full mb-4">
                        <Package className="text-indigo-600 w-6 h-6" />
                    </div>
                    <h2 className="text-2xl font-bold text-slate-900">Welcome Back</h2>
                    <p className="text-slate-500 mt-2">Sign in to your packaging dashboard</p>
                </div>

                {/* Role Selection */}
                <div className="flex gap-4 mb-8">
                    <button
                        type="button"
                        onClick={() => setRole('producer')}
                        className={`flex-1 flex flex-col items-center p-4 border rounded-lg transition-colors ${role === 'producer' ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-slate-200 text-slate-500 hover:border-indigo-200'}`}
                    >
                        <Leaf className="mb-2 w-6 h-6" />
                        <span className="text-sm font-medium">Food Producer</span>
                    </button>
                    <button
                        type="button"
                        onClick={() => setRole('vendor')}
                        className={`flex-1 flex flex-col items-center p-4 border rounded-lg transition-colors ${role === 'vendor' ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-slate-200 text-slate-500 hover:border-emerald-200'}`}
                    >
                        <Factory className="mb-2 w-6 h-6" />
                        <span className="text-sm font-medium">Packaging Vendor</span>
                    </button>
                </div>

                {/* Form */}
                <form className="space-y-4" onSubmit={handleLogin}>

                    {/* Error Message Display */}
                    {error && (
                        <div className="flex items-center gap-2 p-3 bg-red-50 text-red-700 border border-red-200 rounded-lg text-sm">
                            <AlertCircle className="w-4 h-4 shrink-0" />
                            <p>{error}</p>
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                        <input
                            type="text"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                            placeholder="admin@packgenius.com"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
                        <div className="relative">
                            <input
                                type={showPassword ? "text" : "password"}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none pr-10"
                                placeholder="••••••••"
                            />
                            <button
                                type="button"
                                onClick={handleShowPassword}
                                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-indigo-600 focus:outline-none transition-colors"
                                title="Show password for 3 seconds"
                            >
                                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center justify-between">
                        <label className="flex items-center">
                            <input type="checkbox" className="w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500" />
                            <span className="ml-2 text-sm text-slate-600">Remember me</span>
                        </label>
                        <a href="#" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">Forgot password?</a>
                    </div>

                    <button type="submit" className="w-full bg-slate-900 text-white font-medium py-2.5 rounded-lg hover:bg-slate-800 transition-colors">
                        Sign In
                    </button>
                </form>

                {/* SSO */}
                <div className="mt-8">
                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-slate-200"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-2 bg-white text-slate-500">Or continue with</span>
                        </div>
                    </div>
                    <div className="mt-6 flex gap-4">
                        <button type="button" className="flex-1 flex justify-center py-2.5 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors font-medium text-slate-700">
                            Google
                        </button>
                        <button type="button" className="flex-1 flex justify-center py-2.5 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors font-medium text-slate-700">
                            LinkedIn
                        </button>
                    </div>
                </div>

            </div>
        </div>
    );
}