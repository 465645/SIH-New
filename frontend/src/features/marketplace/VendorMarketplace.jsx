import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    Search, Star, ShieldCheck, MapPin, Truck, Package, Leaf,
    Loader2, Send, IndianRupee, Layers,
} from 'lucide-react';
import Navbar from '../../components/Navbar';
import { api, ApiError } from '../../lib/api';

export default function VendorMarketplace() {
    const navigate = useNavigate();
    const location = useLocation();

    // When the user arrives via "Source This Packaging", these arrive with them.
    const incoming = location.state || {};

    const [materialCode, setMaterialCode] = useState(incoming.materialCode || '');
    const [quantity, setQuantity] = useState(incoming.quantity || 50000);
    const [ecoOnly, setEcoOnly] = useState(false);
    const [query, setQuery] = useState('');

    const [vendors, setVendors] = useState([]);
    const [materials, setMaterials] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [rfqState, setRfqState] = useState(null);

    useEffect(() => {
        api.get('/api/materials', { auth: false })
            .then((d) => setMaterials(d.materials))
            .catch(() => { /* the filter just stays empty */ });
    }, []);

    useEffect(() => {
        setLoading(true); setError('');
        const params = new URLSearchParams({ quantity: String(quantity) });
        if (materialCode) params.set('material_code', materialCode);
        if (ecoOnly) params.set('eco_only', 'true');

        api.get(`/api/marketplace/vendors?${params}`, { auth: false })
            .then((d) => setVendors(d.vendors))
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false));
    }, [materialCode, quantity, ecoOnly]);

    const raiseRFQ = async (vendorRow) => {
        setRfqState({ status: 'sending', vendor: vendorRow?.vendor_name });
        try {
            const result = await api.post('/api/marketplace/rfq', {
                product_name: incoming.productName || 'Packaging enquiry',
                material_code: materialCode || vendorRow?.material_code,
                material_name: incoming.materialName || vendorRow?.title || '',
                required_otr: incoming.requiredOtr ?? null,
                required_wvtr: incoming.requiredWvtr ?? null,
                thickness_um: incoming.thicknessUm ?? null,
                width_mm: incoming.widthMm ?? 150,
                height_mm: incoming.heightMm ?? 250,
                gusset_mm: incoming.gussetMm ?? 60,
                quantity: Number(quantity),
                report_id: incoming.reportId ?? null,
            });
            setRfqState({ status: 'sent', ...result });
        } catch (err) {
            if (err instanceof ApiError && err.status === 401) { navigate('/login'); return; }
            setRfqState({ status: 'error', message: err.message });
        }
    };

    const visible = vendors.filter((v) => {
        if (!query.trim()) return true;
        const hay = `${v.vendor_name} ${v.location} ${v.title || ''} ${
            (v.products || []).map((p) => p.title).join(' ')}`.toLowerCase();
        return hay.includes(query.toLowerCase());
    });

    return (
        <div className="min-h-screen bg-slate-50 font-sans flex flex-col">
            <Navbar />
            <div className="p-6 md:p-10 flex-1">
                <div className="max-w-[1400px] w-full mx-auto space-y-6">

                    <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
                        <div>
                            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                                Packaging Marketplace
                            </h1>
                            <p className="text-slate-500 mt-2 max-w-2xl leading-relaxed">
                                {materialCode
                                    ? 'Showing suppliers who can make the material your analysis recommended.'
                                    : 'Browse verified converters, or run an analysis first to match suppliers to a specification.'}
                            </p>
                        </div>
                        <button
                            onClick={() => navigate('/orders')}
                            className="px-5 py-2.5 bg-white border border-slate-200 rounded-lg text-sm font-bold text-slate-700 hover:bg-slate-50 shadow-sm shrink-0"
                        >
                            My orders &amp; RFQs →
                        </button>
                    </div>

                    {/* Filters */}
                    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div className="md:col-span-2">
                                <label className="block text-xs font-bold text-slate-600 mb-1.5">Search</label>
                                <div className="relative">
                                    <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                                    <input
                                        value={query} onChange={(e) => setQuery(e.target.value)}
                                        placeholder="Vendor, city or product"
                                        className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-slate-600 mb-1.5">Material</label>
                                <select
                                    value={materialCode} onChange={(e) => setMaterialCode(e.target.value)}
                                    className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                                >
                                    <option value="">All materials</option>
                                    {materials.map((m) => (
                                        <option key={m.code} value={m.code}>{m.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-slate-600 mb-1.5">
                                    Order quantity
                                </label>
                                <input
                                    type="number" min="1000" step="1000" value={quantity}
                                    onChange={(e) => setQuantity(Number(e.target.value) || 0)}
                                    className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                                />
                            </div>
                        </div>
                        <label className="flex items-center gap-2.5 mt-4 cursor-pointer w-max">
                            <input
                                type="checkbox" checked={ecoOnly}
                                onChange={(e) => setEcoOnly(e.target.checked)}
                                className="w-5 h-5 text-emerald-600 border-slate-300 rounded focus:ring-emerald-500"
                            />
                            <span className="text-sm font-medium text-slate-700">
                                EPR-registered / eco-friendly suppliers only
                            </span>
                        </label>
                    </div>

                    {rfqState?.status === 'sent' && (
                        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5">
                            <p className="font-bold text-emerald-900">
                                RFQ #{rfqState.rfq_id} sent to {rfqState.matched_count} supplier
                                {rfqState.matched_count === 1 ? '' : 's'}
                            </p>
                            <p className="text-sm text-emerald-800 mt-1">
                                {rfqState.dieline_attached
                                    ? 'Your die-line and technical specification were attached.'
                                    : 'Specification attached.'}{' '}
                                <button onClick={() => navigate('/orders')}
                                    className="font-bold underline">Track it here</button>.
                            </p>
                        </div>
                    )}
                    {rfqState?.status === 'error' && (
                        <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-sm text-red-800">
                            {rfqState.message}
                        </div>
                    )}

                    {loading && (
                        <div className="flex items-center gap-3 text-slate-500 p-10 justify-center">
                            <Loader2 className="w-5 h-5 animate-spin" /> Loading suppliers…
                        </div>
                    )}
                    {error && !loading && (
                        <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-sm text-red-800">
                            {error}
                        </div>
                    )}

                    {!loading && visible.length === 0 && (
                        <div className="bg-white rounded-2xl border border-slate-200 p-10 text-center">
                            <Package className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                            <p className="font-bold text-slate-900">No suppliers match</p>
                            <p className="text-sm text-slate-500 mt-1">
                                Try a different material, a lower quantity, or clear the eco filter.
                            </p>
                        </div>
                    )}

                    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                        {visible.map((v) => (
                            <VendorCard
                                key={`${v.vendor_id}-${v.product_id || 'all'}`}
                                vendor={v} quantity={quantity}
                                canRFQ={Boolean(materialCode)}
                                onRFQ={() => raiseRFQ(v)}
                                sending={rfqState?.status === 'sending'}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

function VendorCard({ vendor: v, quantity, canRFQ, onRFQ, sending }) {
    const matched = v.price_per_unit !== undefined;

    return (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col">
            <div className="flex items-start justify-between gap-3 mb-3">
                <div className="min-w-0">
                    <h3 className="text-lg font-bold text-slate-900 leading-tight">{v.vendor_name}</h3>
                    <p className="text-xs text-slate-500 flex items-center gap-1 mt-1.5">
                        <MapPin className="w-3.5 h-3.5" /> {v.location}
                    </p>
                </div>
                <div className="flex flex-col items-end gap-1.5 shrink-0">
                    <span className="flex items-center gap-1 text-sm font-bold text-slate-900">
                        <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                        {v.rating}
                    </span>
                    <span className="text-[11px] text-slate-400">{v.reviews} reviews</span>
                </div>
            </div>

            <div className="flex flex-wrap gap-1.5 mb-4">
                {v.fssai_verified && (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-1 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-100">
                        <ShieldCheck className="w-3 h-3" /> FSSAI verified
                    </span>
                )}
                {v.eco_friendly && (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-1 rounded-md bg-lime-50 text-lime-700 border border-lime-100">
                        <Leaf className="w-3 h-3" /> EPR registered
                    </span>
                )}
                <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-1 rounded-md bg-slate-50 text-slate-600 border border-slate-200">
                    <Truck className="w-3 h-3" /> {v.lead_time_days} days
                </span>
            </div>

            {matched ? (
                <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 mb-4">
                    <p className="text-sm font-bold text-slate-900">{v.title}</p>
                    <p className="text-xs text-slate-500 mt-0.5 font-mono">{v.structure}</p>
                    <div className="flex items-end justify-between mt-3">
                        <div>
                            <p className="text-[11px] font-bold text-slate-500 uppercase">
                                At {quantity.toLocaleString('en-IN')} units
                            </p>
                            <p className="text-2xl font-black text-slate-900 flex items-center">
                                <IndianRupee className="w-5 h-5" />
                                {v.price_per_unit ?? '—'}
                                <span className="text-xs font-semibold text-slate-400 ml-1">/unit</span>
                            </p>
                        </div>
                        <p className="text-[11px] text-slate-500 text-right">
                            MOQ {v.min_order_qty?.toLocaleString('en-IN')}
                        </p>
                    </div>
                    {!v.meets_moq && (
                        <p className="text-[11px] font-bold text-amber-700 bg-amber-50 rounded-md px-2 py-1.5 mt-3">
                            Below this supplier&apos;s MOQ — raise the quantity to qualify.
                        </p>
                    )}
                    <div className="mt-3 pt-3 border-t border-slate-200">
                        <p className="text-[11px] font-bold text-slate-500 uppercase mb-1.5">Volume breaks</p>
                        <div className="flex gap-3 text-[11px] text-slate-600">
                            {v.tiers?.filter((t) => t.price).map((t) => (
                                <span key={t.qty}>
                                    {(t.qty / 1000)}k: <span className="font-bold">₹{t.price}</span>
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            ) : (
                <div className="mb-4 space-y-2">
                    {(v.products || []).slice(0, 3).map((p) => (
                        <div key={p.id} className="flex items-center justify-between gap-2 text-sm">
                            <span className="text-slate-700 truncate flex items-center gap-1.5">
                                <Layers className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                                {p.title}
                            </span>
                            <span className="font-bold text-slate-900 shrink-0">
                                {p.price_per_unit ? `₹${p.price_per_unit}` : '—'}
                            </span>
                        </div>
                    ))}
                    {v.about && <p className="text-xs text-slate-500 leading-relaxed pt-1">{v.about}</p>}
                </div>
            )}

            <button
                onClick={onRFQ} disabled={!canRFQ || sending}
                title={canRFQ ? '' : 'Select a material to raise an RFQ'}
                className="mt-auto w-full py-3 bg-indigo-600 text-white rounded-lg text-sm font-bold hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 flex items-center justify-center gap-2 transition-colors"
            >
                {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                Request a quote
            </button>
        </div>
    );
}
