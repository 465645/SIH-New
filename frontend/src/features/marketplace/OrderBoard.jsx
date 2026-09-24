import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Loader2, FileText, IndianRupee, ArrowRight, CheckCircle2, Clock,
} from 'lucide-react';
import Navbar from '../../components/Navbar';
import { api, API_BASE, ApiError } from '../../lib/api';

const STAGE_TONE = {
    placed: 'border-slate-300 bg-slate-50',
    artwork_approval: 'border-indigo-300 bg-indigo-50',
    in_production: 'border-amber-300 bg-amber-50',
    quality_check: 'border-purple-300 bg-purple-50',
    dispatched: 'border-sky-300 bg-sky-50',
    delivered: 'border-emerald-300 bg-emerald-50',
};

export default function OrderBoard() {
    const navigate = useNavigate();
    const [tab, setTab] = useState('rfqs');
    const [role, setRole] = useState('buyer');
    const [rfqs, setRfqs] = useState([]);
    const [board, setBoard] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const guard = useCallback((err) => {
        if (err instanceof ApiError && err.status === 401) { navigate('/login'); return true; }
        setError(err.message);
        return false;
    }, [navigate]);

    const load = useCallback(async () => {
        setLoading(true); setError('');
        try {
            const [me, r, b] = await Promise.all([
                api.get('/api/account/me'),
                api.get('/api/marketplace/rfqs'),
                api.get('/api/marketplace/board'),
            ]);
            setRole(me.role);
            setRfqs(r.rfqs);
            setBoard(b);
        } catch (err) {
            guard(err);
        }
        setLoading(false);
    }, [guard]);

    useEffect(() => { load(); }, [load]);

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-50 flex flex-col">
                <Navbar />
                <div className="flex-1 flex items-center justify-center gap-3 text-slate-500">
                    <Loader2 className="w-5 h-5 animate-spin" /> Loading…
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 font-sans flex flex-col">
            <Navbar />
            <div className="p-6 md:p-10 flex-1">
                <div className="max-w-[1500px] w-full mx-auto space-y-6">
                    <div>
                        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                            {role === 'supplier' ? 'Incoming Business' : 'My Sourcing'}
                        </h1>
                        <p className="text-slate-500 mt-2">
                            {role === 'supplier'
                                ? 'Open RFQs you can supply, and the orders you are fulfilling.'
                                : 'Your quote requests and the orders you have placed.'}
                        </p>
                    </div>

                    <div className="flex gap-2 border-b border-slate-200">
                        {[['rfqs', role === 'supplier' ? 'Open RFQs' : 'My RFQs'],
                          ['board', 'Order tracking']].map(([id, label]) => (
                            <button
                                key={id} onClick={() => setTab(id)}
                                className={`px-5 py-3 text-sm font-bold border-b-2 transition-colors ${tab === id
                                    ? 'border-indigo-600 text-indigo-700'
                                    : 'border-transparent text-slate-500 hover:text-slate-800'}`}
                            >
                                {label}
                            </button>
                        ))}
                    </div>

                    {error && (
                        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-800">
                            {error}
                        </div>
                    )}

                    {tab === 'rfqs' && (
                        <RFQList rfqs={rfqs} role={role} onChange={load} guard={guard} />
                    )}
                    {tab === 'board' && (
                        <Kanban board={board} onChange={load} guard={guard} />
                    )}
                </div>
            </div>
        </div>
    );
}

function RFQList({ rfqs, role, onChange, guard }) {
    const [openId, setOpenId] = useState(null);

    if (rfqs.length === 0) {
        return (
            <div className="bg-white rounded-2xl border border-slate-200 p-10 text-center">
                <FileText className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                <p className="font-bold text-slate-900">No RFQs yet</p>
                <p className="text-sm text-slate-500 mt-1">
                    {role === 'supplier'
                        ? 'Add materials to your inventory to start receiving matching RFQs.'
                        : 'Run an analysis, then use "Source This Packaging" to raise one.'}
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {rfqs.map((r) => (
                <div key={r.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                                <h3 className="font-bold text-slate-900">{r.product_name}</h3>
                                <span className={`text-[11px] font-black px-2 py-0.5 rounded uppercase ${
                                    r.status === 'awarded' ? 'bg-emerald-100 text-emerald-700'
                                        : r.status === 'quoted' ? 'bg-indigo-100 text-indigo-700'
                                            : 'bg-slate-100 text-slate-600'}`}>
                                    {r.status}
                                </span>
                            </div>
                            <p className="text-sm text-slate-500 mt-1">
                                {r.material_name || r.material_code} &middot; {r.dimensions} &middot;{' '}
                                {r.quantity?.toLocaleString('en-IN')} units
                            </p>
                            {(r.required_otr != null || r.required_wvtr != null) && (
                                <p className="text-xs text-slate-500 mt-1 font-mono">
                                    OTR ≤ {r.required_otr ?? '—'} · WVTR ≤ {r.required_wvtr ?? '—'}
                                </p>
                            )}
                        </div>
                        <div className="flex items-center gap-3 shrink-0">
                            <a
                                href={`${API_BASE}/api/marketplace/rfq/${r.id}/dieline.svg`}
                                target="_blank" rel="noreferrer"
                                className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-xs font-bold text-slate-700 hover:bg-slate-50"
                            >
                                Die-line
                            </a>
                            <button
                                onClick={() => setOpenId(openId === r.id ? null : r.id)}
                                className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold hover:bg-slate-800"
                            >
                                {role === 'supplier' ? 'Submit quote' : `Quotes (${r.quote_count})`}
                            </button>
                        </div>
                    </div>

                    {openId === r.id && (
                        role === 'supplier'
                            ? <QuoteForm rfqId={r.id} onDone={onChange} guard={guard} />
                            : <QuoteComparison rfqId={r.id} onDone={onChange} guard={guard} />
                    )}
                </div>
            ))}
        </div>
    );
}

function QuoteForm({ rfqId, onDone, guard }) {
    const [form, setForm] = useState({
        price_per_unit: 2.5, moq: 25000, lead_time_days: 14, tooling_cost: 0, notes: '',
    });
    const [busy, setBusy] = useState(false);
    const [done, setDone] = useState(false);

    const submit = async () => {
        setBusy(true);
        try {
            await api.post('/api/marketplace/quote', { rfq_id: rfqId, ...form });
            setDone(true);
            onDone();
        } catch (err) { guard(err); }
        setBusy(false);
    };

    if (done) {
        return (
            <p className="mt-5 pt-5 border-t border-slate-100 text-sm font-bold text-emerald-700 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" /> Quote submitted.
            </p>
        );
    }

    return (
        <div className="mt-5 pt-5 border-t border-slate-100">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[['price_per_unit', 'Price / unit (₹)', '0.01'],
                  ['moq', 'Your MOQ', '1000'],
                  ['lead_time_days', 'Lead time (days)', '1'],
                  ['tooling_cost', 'Tooling cost (₹)', '100']].map(([k, label, step]) => (
                    <div key={k}>
                        <label className="block text-xs font-bold text-slate-600 mb-1.5">{label}</label>
                        <input
                            type="number" step={step} value={form[k]}
                            onChange={(e) => setForm((p) => ({ ...p, [k]: Number(e.target.value) }))}
                            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                    </div>
                ))}
            </div>
            <button
                onClick={submit} disabled={busy}
                className="mt-4 px-6 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-bold hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2"
            >
                {busy && <Loader2 className="w-4 h-4 animate-spin" />} Send quote
            </button>
        </div>
    );
}

function QuoteComparison({ rfqId, onDone, guard }) {
    const [data, setData] = useState(null);
    const [busy, setBusy] = useState(false);

    useEffect(() => {
        api.get(`/api/marketplace/rfq/${rfqId}/quotes`).then(setData).catch(guard);
    }, [rfqId, guard]);

    const placeOrder = async (quoteId) => {
        setBusy(true);
        try {
            await api.post('/api/marketplace/purchase-order', { quote_id: quoteId });
            onDone();
        } catch (err) { guard(err); }
        setBusy(false);
    };

    if (!data) return <p className="mt-5 text-sm text-slate-500">Loading quotes…</p>;
    if (data.quotes.length === 0) {
        return <p className="mt-5 pt-5 border-t border-slate-100 text-sm text-slate-500">
            No quotes received yet.
        </p>;
    }

    return (
        <div className="mt-5 pt-5 border-t border-slate-100 overflow-x-auto">
            <table className="w-full text-sm min-w-[720px]">
                <thead>
                    <tr className="text-left text-xs font-bold text-slate-500 uppercase border-b border-slate-200">
                        <th className="pb-2 pr-4">Supplier</th>
                        <th className="pb-2 pr-4">Unit</th>
                        <th className="pb-2 pr-4">Tooling</th>
                        <th className="pb-2 pr-4">Landed</th>
                        <th className="pb-2 pr-4">Order value</th>
                        <th className="pb-2 pr-4">Lead</th>
                        <th className="pb-2"></th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                    {data.quotes.map((q) => (
                        <tr key={q.quote_id} className={q.best_price ? 'bg-emerald-50/50' : ''}>
                            <td className="py-3 pr-4">
                                <span className="font-semibold text-slate-900">{q.vendor_name}</span>
                                {q.best_price && (
                                    <span className="ml-2 text-[10px] font-black text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded">
                                        BEST
                                    </span>
                                )}
                            </td>
                            <td className="py-3 pr-4 text-slate-600">₹{q.price_per_unit}</td>
                            <td className="py-3 pr-4 text-slate-600">₹{q.tooling_cost}</td>
                            <td className="py-3 pr-4 font-bold text-slate-900">₹{q.landed_cost_per_unit}</td>
                            <td className="py-3 pr-4 text-slate-600">₹{q.order_value?.toLocaleString('en-IN')}</td>
                            <td className="py-3 pr-4 text-slate-600">{q.lead_time_days}d</td>
                            <td className="py-3">
                                <button
                                    onClick={() => placeOrder(q.quote_id)} disabled={busy}
                                    className="px-4 py-1.5 bg-slate-900 text-white rounded-lg text-xs font-bold hover:bg-slate-800 disabled:opacity-50"
                                >
                                    Place PO
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <p className="text-xs text-slate-500 mt-3">
                Landed cost amortises the one-off tooling charge across the order quantity,
                which is what actually decides the cheapest supplier at this volume.
            </p>
        </div>
    );
}

function Kanban({ board, onChange, guard }) {
    const [busy, setBusy] = useState(null);

    if (!board || board.total === 0) {
        return (
            <div className="bg-white rounded-2xl border border-slate-200 p-10 text-center">
                <Clock className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                <p className="font-bold text-slate-900">No orders in flight</p>
                <p className="text-sm text-slate-500 mt-1">
                    Accept a quote to raise a purchase order and it will appear here.
                </p>
            </div>
        );
    }

    const move = async (poId, status) => {
        setBusy(poId);
        try {
            await api.patch(`/api/marketplace/purchase-order/${poId}`, { status });
            onChange();
        } catch (err) { guard(err); }
        setBusy(null);
    };

    const stageKeys = board.stages.map((s) => s.key);

    return (
        <div className="overflow-x-auto pb-4">
            <div className="flex gap-4 min-w-max">
                {board.stages.map((stage, idx) => (
                    <div key={stage.key} className="w-72 shrink-0">
                        <div className={`rounded-t-xl border-t-4 px-4 py-3 ${STAGE_TONE[stage.key]}`}>
                            <p className="text-sm font-bold text-slate-900">{stage.label}</p>
                            <p className="text-xs text-slate-500">{stage.orders.length} order
                                {stage.orders.length === 1 ? '' : 's'}</p>
                        </div>
                        <div className="bg-slate-100/70 rounded-b-xl p-3 space-y-3 min-h-[140px]">
                            {stage.orders.map((po) => (
                                <div key={po.id} className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
                                    <p className="font-mono text-xs font-bold text-slate-900">{po.po_number}</p>
                                    <p className="text-xs text-slate-500 mt-1">{po.vendor_name}</p>
                                    <p className="text-sm font-bold text-slate-900 mt-2 flex items-center">
                                        <IndianRupee className="w-3.5 h-3.5" />
                                        {po.total_value?.toLocaleString('en-IN')}
                                    </p>
                                    <p className="text-[11px] text-slate-500">
                                        {po.quantity?.toLocaleString('en-IN')} units
                                    </p>
                                    {idx < stageKeys.length - 1 && (
                                        <button
                                            onClick={() => move(po.id, stageKeys[idx + 1])}
                                            disabled={busy === po.id}
                                            className="mt-3 w-full py-1.5 bg-slate-100 text-slate-700 rounded-md text-[11px] font-bold hover:bg-slate-200 flex items-center justify-center gap-1 disabled:opacity-50"
                                        >
                                            {busy === po.id
                                                ? <Loader2 className="w-3 h-3 animate-spin" />
                                                : <>Advance <ArrowRight className="w-3 h-3" /></>}
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
