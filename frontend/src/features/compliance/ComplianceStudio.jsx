import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ShieldAlert, ShieldCheck, AlertTriangle, HelpCircle, Beaker,
    ClipboardList, QrCode, Loader2, Star, Info,
} from 'lucide-react';
import Navbar from '../../components/Navbar';
import { api, API_BASE, ApiError } from '../../lib/api';

const TABS = [
    { id: 'additives', label: 'Preservative Check', icon: Beaker },
    { id: 'nutrition', label: 'Nutrition & FoP', icon: ClipboardList },
    { id: 'label', label: 'Label & QR', icon: QrCode },
];

const FSSAI_CATEGORIES = [
    'Dairy products and analogues', 'Fats and oils, and fat emulsions',
    'Fruits, vegetables, nuts and seeds', 'Confectionery',
    'Cereals and cereal products', 'Bakery products',
    'Beverages, excluding dairy products', 'Ready-to-eat savouries',
    'Prepared foods', 'Salts, spices, soups, sauces and salads',
];

export default function ComplianceStudio() {
    const [tab, setTab] = useState('additives');
    const navigate = useNavigate();

    const handleError = (err, setError) => {
        if (err instanceof ApiError && err.status === 401) {
            navigate('/login');
            return;
        }
        setError(err.message || 'Something went wrong.');
    };

    return (
        <div className="min-h-screen bg-slate-50 font-sans flex flex-col">
            <Navbar />
            <div className="p-6 md:p-10 flex-1">
                <div className="max-w-[1200px] w-full mx-auto space-y-8">
                    <div>
                        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                            Formulation &amp; Compliance
                        </h1>
                        <p className="text-slate-500 mt-2 max-w-3xl leading-relaxed">
                            Screen your recipe against FSSAI additive limits, generate the
                            front-of-pack label, and mint the consumer QR code before you
                            commit artwork to print.
                        </p>
                    </div>

                    <div className="flex gap-2 border-b border-slate-200 overflow-x-auto">
                        {TABS.map(({ id, label, icon: Icon }) => (
                            <button
                                key={id}
                                onClick={() => setTab(id)}
                                className={`flex items-center gap-2 px-5 py-3 text-sm font-bold whitespace-nowrap border-b-2 transition-colors ${tab === id
                                    ? 'border-indigo-600 text-indigo-700'
                                    : 'border-transparent text-slate-500 hover:text-slate-800'}`}
                            >
                                <Icon className="w-4 h-4" /> {label}
                            </button>
                        ))}
                    </div>

                    {tab === 'additives' && <AdditivePanel onError={handleError} />}
                    {tab === 'nutrition' && <NutritionPanel onError={handleError} />}
                    {tab === 'label' && <LabelPanel onError={handleError} />}
                </div>
            </div>
        </div>
    );
}

/* ------------------------------------------------------------------ */
/* Preservative validator                                              */
/* ------------------------------------------------------------------ */

const VERDICT_STYLE = {
    banned: { cls: 'bg-red-50 border-red-200 text-red-800', Icon: ShieldAlert, label: 'BANNED' },
    over_limit: { cls: 'bg-red-50 border-red-200 text-red-800', Icon: AlertTriangle, label: 'OVER LIMIT' },
    unknown: { cls: 'bg-amber-50 border-amber-200 text-amber-900', Icon: HelpCircle, label: 'UNKNOWN' },
    ok: { cls: 'bg-emerald-50 border-emerald-200 text-emerald-800', Icon: ShieldCheck, label: 'OK' },
};

function AdditivePanel({ onError }) {
    const [text, setText] = useState(
        'Potassium sorbate (INS 202) - 800 ppm\nSodium benzoate - 250 ppm\nAscorbic acid'
    );
    const [category, setCategory] = useState('Bakery products');
    const [isInfant, setIsInfant] = useState(false);
    const [result, setResult] = useState(null);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState('');

    const run = async () => {
        setBusy(true); setError(''); setResult(null);
        try {
            const data = await api.post('/api/compliance/preservatives', {
                raw_text: text, fssai_category: category, is_infant_food: isInfant,
            });
            setResult(data);
        } catch (err) {
            onError(err, setError);
        }
        setBusy(false);
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
                <h2 className="text-lg font-bold text-slate-900 mb-1">Additives &amp; preservatives</h2>
                <p className="text-sm text-slate-500 mb-6">
                    One per line. Levels are optional &mdash; include them as
                    <span className="font-semibold"> 800 ppm</span> to check against the ceiling.
                </p>

                <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    rows={8}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none resize-y"
                />

                <label className="block text-sm font-bold text-slate-700 mt-5 mb-2">FSSAI Category</label>
                <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                >
                    {FSSAI_CATEGORIES.map((c) => <option key={c}>{c}</option>)}
                </select>

                <label className="flex items-center gap-3 mt-5 cursor-pointer">
                    <input
                        type="checkbox" checked={isInfant}
                        onChange={(e) => setIsInfant(e.target.checked)}
                        className="w-5 h-5 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500"
                    />
                    <span className="text-sm font-medium text-slate-700">
                        Food for infants / young children (stricter prohibitions apply)
                    </span>
                </label>

                <button
                    onClick={run} disabled={busy}
                    className="mt-6 w-full py-3.5 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                    {busy && <Loader2 className="w-4 h-4 animate-spin" />}
                    {busy ? 'Checking…' : 'Check compliance'}
                </button>
                {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
            </div>

            <div className="space-y-4">
                {!result && (
                    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-sm text-slate-500">
                        Results appear here.
                    </div>
                )}

                {result && (
                    <>
                        <div className={`rounded-2xl border p-6 ${result.overall === 'pass'
                            ? 'bg-emerald-50 border-emerald-200'
                            : result.overall === 'review'
                                ? 'bg-amber-50 border-amber-200'
                                : 'bg-red-50 border-red-200'}`}>
                            <p className="text-xs font-bold uppercase tracking-wide opacity-70">Overall</p>
                            <p className="text-2xl font-black mt-1">
                                {result.overall === 'pass' ? 'Compliant'
                                    : result.overall === 'review' ? 'Needs review' : 'Not compliant'}
                            </p>
                            <p className="text-sm mt-2 opacity-80">
                                {result.counts.banned} banned &middot; {result.counts.over_limit} over limit
                                &middot; {result.counts.unknown} unknown &middot; {result.counts.ok} ok
                            </p>
                        </div>

                        {result.results.map((r, i) => {
                            const style = VERDICT_STYLE[r.verdict] || VERDICT_STYLE.unknown;
                            const Icon = style.Icon;
                            return (
                                <div key={i} className={`rounded-xl border p-5 ${style.cls}`}>
                                    <div className="flex items-start gap-3">
                                        <Icon className="w-5 h-5 shrink-0 mt-0.5" />
                                        <div className="min-w-0">
                                            <div className="flex flex-wrap items-center gap-2">
                                                <span className="font-bold">{r.input}</span>
                                                {r.ins && (
                                                    <code className="text-xs bg-white/70 px-2 py-0.5 rounded font-bold">
                                                        INS {r.ins}
                                                    </code>
                                                )}
                                                <span className="text-[10px] font-black tracking-wider opacity-70">
                                                    {style.label}
                                                </span>
                                            </div>
                                            <p className="text-sm mt-1.5 leading-relaxed">{r.message}</p>
                                            {r.legal_basis && (
                                                <p className="text-xs mt-2 opacity-70 italic">{r.legal_basis}</p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}

                        {result.interactions.map((it, i) => (
                            <div key={i} className="rounded-xl border border-indigo-200 bg-indigo-50 p-5">
                                <div className="flex items-start gap-3">
                                    <Info className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                                    <div>
                                        <p className="font-bold text-indigo-900 text-sm">
                                            Interaction: {it.additives.join(' + ')}
                                        </p>
                                        <p className="text-sm text-indigo-800 mt-1 leading-relaxed">{it.message}</p>
                                    </div>
                                </div>
                            </div>
                        ))}

                        <p className="text-xs text-slate-500 leading-relaxed px-1">{result.disclaimer}</p>
                    </>
                )}
            </div>
        </div>
    );
}

/* ------------------------------------------------------------------ */
/* Nutrition / front-of-pack                                           */
/* ------------------------------------------------------------------ */

const MACROS = [
    ['energy_kcal', 'Energy (kcal)'], ['protein', 'Protein (g)'],
    ['carbohydrate', 'Carbohydrate (g)'], ['total_sugar', 'Total sugars (g)'],
    ['fat', 'Total fat (g)'], ['saturated_fat', 'Saturated fat (g)'],
    ['trans_fat', 'Trans fat (g)'], ['fibre', 'Dietary fibre (g)'],
    ['sodium_mg', 'Sodium (mg)'], ['fvnl_percent', 'Fruit/veg/nut/legume (%)'],
];

const BAND_CLASSES = {
    green: 'bg-emerald-500 text-white',
    amber: 'bg-amber-400 text-amber-950',
    red: 'bg-red-500 text-white',
    grey: 'bg-slate-300 text-slate-700',
};

function NutritionPanel({ onError }) {
    const [values, setValues] = useState({
        energy_kcal: 535, protein: 6.5, carbohydrate: 53, total_sugar: 3.2,
        fat: 32, saturated_fat: 14, trans_fat: 0.2, fibre: 3.1,
        sodium_mg: 820, fvnl_percent: 0,
    });
    const [isLiquid, setIsLiquid] = useState(false);
    const [panelText, setPanelText] = useState('');
    const [result, setResult] = useState(null);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState('');
    const [parseNote, setParseNote] = useState('');

    const set = (k, v) => setValues((p) => ({ ...p, [k]: v === '' ? '' : Number(v) }));

    const importText = async () => {
        setError(''); setParseNote('');
        try {
            const parsed = await api.post('/api/compliance/parse-text', { text: panelText });
            setValues((p) => ({ ...p, ...parsed.values }));
            setParseNote(
                `Read ${Object.keys(parsed.values).length} values.` +
                (parsed.warnings?.length ? ` ${parsed.warnings[0]}` : '')
            );
        } catch (err) {
            onError(err, setError);
        }
    };

    const run = async () => {
        setBusy(true); setError(''); setResult(null);
        try {
            const clean = Object.fromEntries(
                Object.entries(values).filter(([, v]) => v !== '' && v !== null)
            );
            setResult(await api.post('/api/compliance/nutrition', { ...clean, is_liquid: isLiquid }));
        } catch (err) {
            onError(err, setError);
        }
        setBusy(false);
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
                    <h2 className="text-lg font-bold text-slate-900 mb-1">Paste a nutrition panel</h2>
                    <p className="text-sm text-slate-500 mb-4">
                        Type or paste the panel text and it will fill the fields below.
                    </p>
                    <textarea
                        value={panelText} onChange={(e) => setPanelText(e.target.value)}
                        rows={5} placeholder={'Nutrition Information per 100 g\nEnergy 535 kcal\nProtein 6.5 g…'}
                        className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white resize-y"
                    />
                    <button
                        onClick={importText} disabled={!panelText.trim()}
                        className="mt-3 px-5 py-2.5 bg-slate-100 text-slate-800 rounded-lg text-sm font-bold hover:bg-slate-200 disabled:opacity-40"
                    >
                        Read panel
                    </button>
                    {parseNote && <p className="text-xs text-emerald-700 mt-2 font-medium">{parseNote}</p>}
                </div>

                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
                    <h2 className="text-lg font-bold text-slate-900 mb-5">
                        Values per {isLiquid ? '100 ml' : '100 g'}
                    </h2>
                    <div className="grid grid-cols-2 gap-4">
                        {MACROS.map(([key, label]) => (
                            <div key={key}>
                                <label className="block text-xs font-bold text-slate-600 mb-1.5">{label}</label>
                                <input
                                    type="number" step="0.1" value={values[key] ?? ''}
                                    onChange={(e) => set(key, e.target.value)}
                                    className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                                />
                            </div>
                        ))}
                    </div>
                    <label className="flex items-center gap-3 mt-5 cursor-pointer">
                        <input
                            type="checkbox" checked={isLiquid}
                            onChange={(e) => setIsLiquid(e.target.checked)}
                            className="w-5 h-5 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500"
                        />
                        <span className="text-sm font-medium text-slate-700">
                            Beverage (tighter thresholds apply per 100 ml)
                        </span>
                    </label>
                    <button
                        onClick={run} disabled={busy}
                        className="mt-6 w-full py-3.5 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        {busy && <Loader2 className="w-4 h-4 animate-spin" />}
                        {busy ? 'Calculating…' : 'Generate front-of-pack label'}
                    </button>
                    {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
                </div>
            </div>

            <div className="space-y-6">
                {!result && (
                    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-sm text-slate-500">
                        The traffic-light label and star rating appear here.
                    </div>
                )}

                {result && (
                    <>
                        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
                            <p className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-4">
                                Traffic lights &mdash; {result.traffic_lights.basis}
                            </p>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                                {Object.entries(result.traffic_lights.nutrients).map(([name, n]) => (
                                    <div key={name} className={`rounded-xl p-4 text-center ${BAND_CLASSES[n.colour]}`}>
                                        <p className="text-[10px] font-black uppercase tracking-wider opacity-90">
                                            {name}
                                        </p>
                                        <p className="text-2xl font-black mt-1">
                                            {n.value ?? '—'}<span className="text-xs">{n.value != null && 'g'}</span>
                                        </p>
                                        <p className="text-[11px] font-bold mt-0.5">{n.band}</p>
                                    </div>
                                ))}
                            </div>
                            <p className="text-sm text-slate-600 mt-4">{result.traffic_lights.summary}</p>
                        </div>

                        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
                            <p className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-4">
                                Indian Nutrition Rating
                            </p>
                            <div className="flex items-center gap-4">
                                <StarRow stars={result.inr.stars} />
                                <div>
                                    <p className="text-3xl font-black text-slate-900">{result.inr.stars}</p>
                                    <p className="text-xs text-slate-500 font-semibold">out of 5</p>
                                </div>
                            </div>
                            <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
                                <div className="bg-red-50 rounded-lg p-3">
                                    <p className="text-xs font-bold text-red-700">Negative points</p>
                                    <p className="text-xl font-black text-red-900">{result.inr.negative_points}</p>
                                </div>
                                <div className="bg-emerald-50 rounded-lg p-3">
                                    <p className="text-xs font-bold text-emerald-700">Positive points</p>
                                    <p className="text-xl font-black text-emerald-900">{result.inr.positive_points}</p>
                                </div>
                            </div>
                            {result.inr.improvement_drivers.length > 0 && (
                                <div className="mt-5">
                                    <p className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">
                                        How to improve the rating
                                    </p>
                                    <ul className="space-y-2">
                                        {result.inr.improvement_drivers.map((d, i) => (
                                            <li key={i} className="text-sm text-slate-700 leading-relaxed flex gap-2">
                                                <span className="text-indigo-500 font-bold">→</span>{d}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                            <p className="text-xs text-slate-400 mt-5 leading-relaxed">{result.inr.disclaimer}</p>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

function StarRow({ stars }) {
    return (
        <div className="flex gap-0.5">
            {[1, 2, 3, 4, 5].map((i) => {
                const fill = stars - i + 1;
                return (
                    <Star
                        key={i}
                        className={`w-7 h-7 ${fill >= 1 ? 'text-amber-400 fill-amber-400'
                            : fill >= 0.5 ? 'text-amber-400 fill-amber-200'
                                : 'text-slate-300'}`}
                    />
                );
            })}
        </div>
    );
}

/* ------------------------------------------------------------------ */
/* Label + QR                                                          */
/* ------------------------------------------------------------------ */

function LabelPanel({ onError }) {
    const [form, setForm] = useState({
        product_name: 'Masala Bhujia', brand: 'Your Brand',
        fssai_category: 'Ready-to-eat savouries', fssai_licence: '10012345678901',
        net_quantity: '200 g', manufacturer: 'Your Foods Pvt Ltd',
        ingredients: 'Besan, edible oil, spices, salt, potassium sorbate 800 ppm',
        is_veg: true, packaging_material: '', recyclable: false,
    });
    const [nutrition, setNutrition] = useState({
        energy_kcal: 535, protein: 6.5, total_sugar: 3.2, fat: 32,
        saturated_fat: 14, fibre: 3.1, sodium_mg: 820,
    });
    const [result, setResult] = useState(null);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState('');

    const set = (k, v) => setForm((p) => ({ ...p, [k]: v }));

    const create = async () => {
        setBusy(true); setError(''); setResult(null);
        try {
            setResult(await api.post('/api/compliance/label', { ...form, nutrition }));
        } catch (err) {
            onError(err, setError);
        }
        setBusy(false);
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 space-y-4">
                <h2 className="text-lg font-bold text-slate-900">Label details</h2>
                {[
                    ['product_name', 'Product name'], ['brand', 'Brand'],
                    ['fssai_licence', 'FSSAI licence number'], ['net_quantity', 'Net quantity'],
                    ['manufacturer', 'Manufactured / packed by'],
                ].map(([key, label]) => (
                    <div key={key}>
                        <label className="block text-xs font-bold text-slate-600 mb-1.5">{label}</label>
                        <input
                            value={form[key]} onChange={(e) => set(key, e.target.value)}
                            className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                        />
                    </div>
                ))}
                <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1.5">Ingredients</label>
                    <textarea
                        rows={3} value={form.ingredients}
                        onChange={(e) => set('ingredients', e.target.value)}
                        className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white resize-y"
                    />
                </div>
                <div className="flex flex-wrap gap-5 pt-1">
                    <label className="flex items-center gap-2.5 cursor-pointer">
                        <input
                            type="checkbox" checked={form.is_veg}
                            onChange={(e) => set('is_veg', e.target.checked)}
                            className="w-5 h-5 text-emerald-600 border-slate-300 rounded focus:ring-emerald-500"
                        />
                        <span className="text-sm font-medium text-slate-700">Vegetarian</span>
                    </label>
                    <label className="flex items-center gap-2.5 cursor-pointer">
                        <input
                            type="checkbox" checked={form.recyclable}
                            onChange={(e) => set('recyclable', e.target.checked)}
                            className="w-5 h-5 text-emerald-600 border-slate-300 rounded focus:ring-emerald-500"
                        />
                        <span className="text-sm font-medium text-slate-700">Recyclable pack</span>
                    </label>
                </div>

                <button
                    onClick={create} disabled={busy}
                    className="w-full py-3.5 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
                >
                    {busy && <Loader2 className="w-4 h-4 animate-spin" />}
                    {busy ? 'Creating…' : 'Create label & QR code'}
                </button>
                {error && <p className="text-sm text-red-600">{error}</p>}
            </div>

            <div className="space-y-6">
                {!result && (
                    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-sm text-slate-500">
                        The QR code and its public page appear here once the label is created.
                    </div>
                )}
                {result && (
                    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
                        <p className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-4">
                            Consumer traceability QR
                        </p>
                        <div className="flex flex-col sm:flex-row gap-6 items-start">
                            <img
                                src={`${API_BASE}/api/public/trace/${result.trace_code}/qr.png`}
                                alt="Traceability QR code"
                                className="w-44 h-44 border border-slate-200 rounded-xl"
                            />
                            <div className="min-w-0">
                                <p className="text-sm text-slate-600 leading-relaxed">
                                    Place this on the back panel. Scanning it opens a plain-language
                                    health summary and disposal instructions.
                                </p>
                                <p className="text-xs font-mono bg-slate-100 px-3 py-2 rounded-lg mt-3 break-all">
                                    {result.trace_code}
                                </p>
                                <a
                                    href={`${API_BASE}/api/public/trace/${result.trace_code}`}
                                    target="_blank" rel="noreferrer"
                                    className="inline-block mt-3 text-sm font-bold text-indigo-600 hover:text-indigo-800"
                                >
                                    Open the public page →
                                </a>
                            </div>
                        </div>

                        <div className="mt-6 pt-6 border-t border-slate-100 flex items-center gap-4">
                            <StarRow stars={result.inr.stars} />
                            <div>
                                <p className="text-sm font-bold text-slate-900">
                                    INR {result.inr.stars} / 5
                                </p>
                                <p className={`text-xs font-bold ${result.compliance.overall === 'pass'
                                    ? 'text-emerald-600' : 'text-red-600'}`}>
                                    Additive screening: {result.compliance.overall}
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
