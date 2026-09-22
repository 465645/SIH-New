import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, ArrowRight, UserPlus, LogIn } from 'lucide-react';

export default function Login() {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        const endpoint = isLogin ? '/api/login' : '/api/signup';

        try {
            // OAuth2 requires form data for login, but our signup takes JSON
            let bodyData;
            let headers = {};

            if (isLogin) {
                bodyData = new URLSearchParams();
                bodyData.append('username', email);
                bodyData.append('password', password);
                headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
            } else {
                bodyData = JSON.stringify({ email, password });
                headers = { 'Content-Type': 'application/json' };
            }

            const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
                method: 'POST',
                headers: headers,
                body: bodyData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Authentication failed");
            }

            if (isLogin) {
                // Save the VIP pass and go to the dashboard!
                localStorage.setItem('access_token', data.access_token);
                navigate('/'); // Or wherever your InputWizard lives
            } else {
                // Signup successful, switch to login mode
                alert("Account created! Please log in.");
                setIsLogin(true);
            }
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-slate-100">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                        <Lock className="w-8 h-8 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-slate-900">
                        {isLogin ? 'Welcome Back' : 'Create Account'}
                    </h2>
                    <p className="text-slate-500 mt-2">
                        {isLogin ? 'Enter your details to access PackGenius AI.' : 'Sign up to start analyzing packaging.'}
                    </p>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-xl text-sm text-center font-medium">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-bold text-slate-700 mb-2">Email Address</label>
                        <div className="relative">
                            <Mail className="w-5 h-5 text-slate-400 absolute left-4 top-3.5" />
                            <input
                                type="email" required
                                value={email} onChange={(e) => setEmail(e.target.value)}
                                className="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                                placeholder="engineer@company.com"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-bold text-slate-700 mb-2">Password</label>
                        <div className="relative">
                            <Lock className="w-5 h-5 text-slate-400 absolute left-4 top-3.5" />
                            <input
                                type="password" required
                                value={password} onChange={(e) => setPassword(e.target.value)}
                                className="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                                placeholder="••••••••"
                            />
                        </div>
                    </div>

                    <button type="submit" className="w-full py-4 bg-slate-900 text-white rounded-xl font-bold text-lg hover:bg-slate-800 transition-all flex items-center justify-center gap-2 mt-4">
                        {isLogin ? <LogIn className="w-5 h-5" /> : <UserPlus className="w-5 h-5" />}
                        {isLogin ? 'Sign In' : 'Sign Up'}
                    </button>
                </form>

                <div className="mt-8 text-center">
                    <button
                        onClick={() => setIsLogin(!isLogin)}
                        className="text-indigo-600 font-semibold hover:text-indigo-800 transition-colors flex items-center justify-center gap-1 mx-auto"
                    >
                        {isLogin ? "Need an account? Sign up" : "Already have an account? Log in"}
                        <ArrowRight className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}