import React, { useState } from 'react';
import {
    Leaf, PackageSearch, Activity, IndianRupee, ShieldCheck,
    Settings2, Download, ShoppingCart, ArrowLeft, Lock
} from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../../components/Navbar';

export default function ResultsDashboard() {
    const navigate = useNavigate();
    const location = useLocation();

    // Extract the live data from our Python FastAPI backend (with a fallback just in case)
    const apiData = location.state?.apiData || {
        optimal_material: "Standard Multi-layer Pouch",
        estimated_cost_per_unit: 1.50,
        epr_green_score: 50,
        barrier_requirement: "Medium",
        map_gas: "None"
    };

    const [shelfLife, setShelfLife] = useState(90);
    const [weight, setWeight] = useState(250);
    const [hasZipLock, setHasZipLock] = useState(false);

    // Estimate Standard Dimensions based on weight
    const getStandardDimensions = (w) => {
        if (w <= 100) return "100mm × 150mm";
        if (w <= 500) return "150mm × 250mm";
        return "200mm × 350mm";
    };

    // Calculate final dynamic cost using the base cost from the Python backend
    const weightMultiplier = weight / 250;
    const zipLockCost = hasZipLock ? 1.50 : 0;
    const finalCost = (apiData.estimated_cost_per_unit * weightMultiplier) + zipLockCost;

    return (
        <div className="min-h-screen bg-slate-50 font-sans flex flex-col">
            <Navbar />

            <div className="p-6 md:p-10 flex-1">
                <div className="max-w-[1500px] w-full mx-auto space-y-8">

                    {/* Header */}
                    <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                        <div className="flex flex-col items-start">
                            <button
                                onClick={() => navigate('/wizard')}
                                className="flex items-center text-sm font-medium text-slate-500 hover:text-indigo-600 mb-3 transition-colors"
                            >
                                <ArrowLeft className="w-4 h-4 mr-1" /> Back to Parameters
                            </button>
                            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">AI Packaging Specification</h1>
                        </div>

                        <div className="flex gap-3">
                            <button className="px-5 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 flex items-center shadow-sm transition-all">
                                <Download className="w-4 h-4 mr-2" /> Die-line PDF
                            </button>
                            <button
                                onClick={() => navigate('/marketplace')}
                                className="px-5 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 flex items-center shadow-sm transition-all focus:ring-4 focus:ring-indigo-100"
                            >
                                <ShoppingCart className="w-4 h-4 mr-2" /> Source Material
                            </button>
                        </div>
                    </div>

                    {/* Top Cards Row */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                        {/* Material Recommended */}
                        <div className="bg-white p-6 md:p-8 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                            <div className="flex items-center justify-between mb-4">
                                <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">Optimal Material</span>
                                <PackageSearch className="text-indigo-500 w-6 h-6" />
                            </div>
                            <h2 className="text-2xl font-bold text-slate-900">{apiData.optimal_material}</h2>
                            <div className="mt-6 inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-100 w-max">
                                <ShieldCheck className="w-4 h-4 mr-1.5" /> FSSAI Compliant
                            </div>
                        </div>

                        {/* Unit Economics & Weight/Dimensions */}
                        <div className="bg-white p-6 md:p-8 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">Estimated Cost</span>
                                <IndianRupee className="text-emerald-500 w-6 h-6" />
                            </div>
                            <div className="flex items-baseline gap-2 mb-6">
                                <h2 className="text-5xl font-black text-slate-900">₹{finalCost.toFixed(2)}</h2>
                                <span className="text-sm text-slate-500 font-medium">/ unit</span>
                            </div>

                            {/* Dynamic Weight & Dimension Input */}
                            <div className="flex flex-col gap-3 bg-slate-50 p-4 rounded-xl border border-slate-100">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium text-slate-600">Fill Weight:</span>
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="number"
                                            value={weight}
                                            onChange={(e) => setWeight(Number(e.target.value) || 0)}
                                            className="w-24 px-3 py-1.5 text-right border border-slate-300 rounded-md text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:outline-none bg-white"
                                        />
                                        <span className="text-sm font-bold text-slate-500">grams</span>
                                    </div>
                                </div>
                                <div className="flex items-center justify-between pt-3 border-t border-slate-200">
                                    <span className="text-sm font-medium text-slate-600">Std. Dimensions:</span>
                                    <div className="text-right">
                                        <span className="text-sm font-bold text-slate-800">{getStandardDimensions(weight)}</span>
                                        <p className="text-[10px] font-semibold text-slate-400 mt-0.5 uppercase tracking-wide">Size can be customized later</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* EPR Green Score */}
                        <div className="bg-white p-6 md:p-8 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                            <div className="flex items-center justify-between mb-4">
                                <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">EPR Green Score</span>
                                <Leaf className={apiData.epr_green_score > 50 ? "text-emerald-500 w-6 h-6" : "text-amber-500 w-6 h-6"} />
                            </div>
                            <div className="flex items-end gap-3">
                                <h2 className={`text-5xl font-black ${apiData.epr_green_score > 50 ? 'text-emerald-600' : 'text-amber-600'}`}>
                                    {apiData.epr_green_score}
                                </h2>
                                <span className="text-base text-slate-500 font-medium mb-1">/ 100</span>
                            </div>
                            <div className="w-full bg-slate-100 h-2.5 mt-6 rounded-full overflow-hidden">
                                <div
                                    className={`h-full transition-all duration-700 ease-out ${apiData.epr_green_score > 50 ? 'bg-emerald-500' : 'bg-amber-500'}`}
                                    style={{ width: `${apiData.epr_green_score}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>

                    {/* Bottom Split Layout: Simulator (Left) and Tech Specs (Right) */}
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

                        {/* LEFT SIDE: Interactive Simulator */}
                        <div className="lg:col-span-7 bg-white p-8 md:p-10 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-center">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 mb-12">
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-indigo-50 rounded-xl border border-indigo-100">
                                        <Settings2 className="w-6 h-6 text-indigo-600" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-slate-900">Specification Simulator</h3>
                                        <p className="text-sm text-slate-500 mt-1">Adjust target shelf life and structure extras.</p>
                                    </div>
                                </div>

                                {/* Zip Lock Toggle */}
                                <label className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all shrink-0 ${hasZipLock ? 'border-indigo-600 bg-indigo-50/50' : 'border-slate-200 bg-white hover:border-slate-300'}`}>
                                    <input
                                        type="checkbox"
                                        checked={hasZipLock}
                                        onChange={(e) => setHasZipLock(e.target.checked)}
                                        className="w-5 h-5 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500 cursor-pointer"
                                    />
                                    <div>
                                        <div className="flex items-center gap-1.5">
                                            <Lock className={`w-4 h-4 ${hasZipLock ? 'text-indigo-600' : 'text-slate-400'}`} />
                                            <span className="text-sm font-bold text-slate-900">Zip-Lock</span>
                                        </div>
                                        <span className="text-xs font-medium text-slate-500 block mt-0.5">+₹1.50 / unit</span>
                                    </div>
                                </label>
                            </div>

                            {/* Slider */}
                            <div className="w-full mb-8 relative">
                                <div className="flex justify-between text-xs font-bold text-slate-400 mb-6 px-1">
                                    <span>30 Days (Fast)</span>
                                    <span>180 Days (Long Term)</span>
                                </div>
                                <input
                                    type="range"
                                    min="30" max="180" step="15"
                                    value={shelfLife}
                                    onChange={(e) => setShelfLife(Number(e.target.value))}
                                    className="w-full h-2.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                                />
                                <div className="flex justify-center mt-8">
                                    <span className="inline-block px-6 py-2.5 bg-indigo-600 text-white rounded-full text-sm font-bold shadow-lg shadow-indigo-600/30">
                                        Target: {shelfLife} Days
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* RIGHT SIDE: Stacked Technical Specs */}
                        <div className="lg:col-span-5 flex flex-col gap-4">
                            <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
                                <p className="text-sm font-bold text-slate-500 uppercase tracking-wide">O2 / Moisture Barrier</p>
                                <p className="text-xl font-bold text-slate-900">{apiData.barrier_requirement}</p>
                            </div>
                            <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
                                <p className="text-sm font-bold text-slate-500 uppercase tracking-wide">MAP Gas Req.</p>
                                <p className="text-xl font-bold text-slate-900">{apiData.map_gas}</p>
                            </div>
                            <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
                                <p className="text-sm font-bold text-slate-500 uppercase tracking-wide">Recyclability</p>
                                <p className="text-xl font-bold text-slate-900">{apiData.epr_green_score > 50 ? 'Highly Recyclable' : 'Complex Multi-layer'}</p>
                            </div>
                            <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
                                <p className="text-sm font-bold text-slate-500 uppercase tracking-wide">FSSAI Status</p>
                                <div className="flex items-center text-xl text-emerald-600 font-bold">
                                    <Activity className="w-5 h-5 mr-2" /> Approved
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}