import React, { useState, useEffect } from 'react';
import {
    Leaf, PackageSearch, Activity, IndianRupee, ShieldCheck,
    Settings2, Download, ShoppingCart, ArrowLeft, Lock, RefreshCw
} from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../../components/Navbar';
import { api, ApiError, fetchBlobUrl } from '../../lib/api';

export default function ResultsDashboard() {
    const navigate = useNavigate();
    const location = useLocation();

    // 1. Change apiData to a state variable so it can update dynamically
    const [apiData, setApiData] = useState(location.state?.apiData || {
        optimal_material: "Standard Multi-layer Pouch",
        estimated_cost_per_unit: 1.50,
        epr_green_score: 50,
        barrier_requirement: "Medium",
        map_gas: "None"
    });

    // The engineering detail that sits alongside the headline recommendation
    const [why, setWhy] = useState(location.state?.why || []);
    const [mapDesign, setMapDesign] = useState(location.state?.mapDesign || null);
    const [alternatives, setAlternatives] = useState(location.state?.alternatives || []);

    const spec = apiData.specification;

    // The parameters the user actually entered in the wizard. Falls back to a
    // generic profile only when the page is opened directly without wizard state.
    const baseRequest = location.state?.request || {
        product_name: "Simulated Product",
        fssai_category: "Beverages",
        is_liquid: true,
        moisture_content: 10.0,
        lipid_content: "Low",
        ph_level: 7.0,
        filling_process: "None"
    };

    const [shelfLife, setShelfLife] = useState(location.state?.request?.shelf_life_days || 90);
    const [weight, setWeight] = useState(250);
    const [hasZipLock, setHasZipLock] = useState(false);
    const [isSimulating, setIsSimulating] = useState(false);

    // Pack dimensions drive film area, which drives cost - Module 4/5
    const [widthMm, setWidthMm] = useState(150);
    const [heightMm, setHeightMm] = useState(250);
    const [gussetMm, setGussetMm] = useState(60);
    const [geometry, setGeometry] = useState(null);
    const [priceCurve, setPriceCurve] = useState(null);
    const [busyAction, setBusyAction] = useState('');

    // 2. Add this effect to recalculate ML predictions when shelf life changes
    useEffect(() => {
        const fetchSimulation = async () => {
            const token = localStorage.getItem("access_token");
            if (!token) {
                navigate('/login');
                return;
            }

            setIsSimulating(true);
            try {
                const response = await fetch('http://127.0.0.1:8000/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    // Re-run the user's own product against the new target shelf life
                    body: JSON.stringify({ ...baseRequest, shelf_life_days: shelfLife })
                });

                if (response.status === 401) {
                    localStorage.removeItem("access_token");
                    navigate('/login');
                    return;
                }

                const result = await response.json();
                if (result.status === "success") {
                    setApiData(result.data);
                    setWhy(result.why || []);
                    setMapDesign(result.map_design || null);
                    setAlternatives(result.alternatives || []);
                }
            } catch (error) {
                console.error("Simulation failed:", error);
            }
            setIsSimulating(false);
        };

        // Debounce: Wait 500ms after the user stops sliding before making the API call
        const timer = setTimeout(() => {
            fetchSimulation();
        }, 500);

        return () => clearTimeout(timer);
    }, [shelfLife]);

    // Recompute film area and unit cost whenever a dimension slider moves.
    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        const timer = setTimeout(() => {
            api.post('/api/dieline/geometry', {
                width_mm: widthMm, height_mm: heightMm, gusset_mm: gussetMm,
                product_name: apiData.optimal_material || 'Pack',
                material_code: apiData.material_code || null,
            })
                .then(setGeometry)
                .catch((err) => {
                    if (err instanceof ApiError && err.status === 401) navigate('/login');
                });
        }, 300);
        return () => clearTimeout(timer);
    }, [widthMm, heightMm, gussetMm, apiData.material_code, apiData.optimal_material, navigate]);

    // Live market pricing for the recommended material, for the histogram
    useEffect(() => {
        if (!apiData.material_code) return;
        api.get(`/api/marketplace/price-curve?material_code=${apiData.material_code}`,
            { auth: false })
            .then(setPriceCurve)
            .catch(() => setPriceCurve(null));
    }, [apiData.material_code]);

    const openDieline = async (format) => {
        setBusyAction(format);
        try {
            const url = await fetchBlobUrl(`/api/dieline/${format}`, {
                body: {
                    width_mm: widthMm, height_mm: heightMm, gusset_mm: gussetMm,
                    product_name: location.state?.request?.product_name || 'Product',
                    net_quantity: `${weight} g`,
                    material_code: apiData.material_code || null,
                    material_name: apiData.optimal_material || '',
                    ingredients: '',
                },
            });
            window.open(url, '_blank', 'noopener');
        } catch (err) {
            if (err instanceof ApiError && err.status === 401) navigate('/login');
            else alert(err.message);
        }
        setBusyAction('');
    };

    const sourceThis = () => {
        navigate('/marketplace', {
            state: {
                materialCode: apiData.material_code,
                materialName: apiData.optimal_material,
                productName: location.state?.request?.product_name || 'Packaging enquiry',
                requiredOtr: spec?.otr_max_cc_m2_day ?? null,
                requiredWvtr: spec?.wvtr_max_g_m2_day ?? null,
                thicknessUm: spec?.film_thickness_um ?? null,
                widthMm, heightMm, gussetMm,
                quantity: 50000,
            },
        });
    };

    // Estimate Standard Dimensions based on weight
    const getStandardDimensions = (w) => {
        if (w <= 100) return "100mm × 150mm";
        if (w <= 500) return "150mm × 250mm";
        return "200mm × 350mm";
    };

    // When the backend has priced the pack from its actual film area, scale that
    // figure by weight rather than re-deriving it from a magic 250g baseline.
    const baseWeight = apiData.cost?.fill_weight_g || 250;
    const weightMultiplier = weight / baseWeight;
    const zipLockCost = hasZipLock ? 1.50 : 0;

    // Once the die-line has priced the actual film area, that figure is more
    // accurate than scaling the backend's standard-pack estimate by weight.
    const filmCost = geometry?.cost?.cost_per_unit;
    const finalCost = filmCost != null
        ? filmCost + zipLockCost
        : (apiData.estimated_cost_per_unit * weightMultiplier) + zipLockCost;

    // ... (Keep the rest of your return statement exactly the same, but you can add this loading indicator near the Material Header)

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
                            <button
                                onClick={() => openDieline('svg')}
                                disabled={busyAction !== ''}
                                className="px-5 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 flex items-center shadow-sm transition-all disabled:opacity-50"
                            >
                                <Download className="w-4 h-4 mr-2" />
                                {busyAction === 'svg' ? 'Generating…' : 'Die-line SVG'}
                            </button>
                            <button
                                onClick={() => openDieline('pdf')}
                                disabled={busyAction !== ''}
                                className="px-5 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 flex items-center shadow-sm transition-all disabled:opacity-50"
                            >
                                <Download className="w-4 h-4 mr-2" />
                                {busyAction === 'pdf' ? 'Generating…' : 'PDF'}
                            </button>
                            <button
                                onClick={sourceThis}
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

                        {/* RIGHT SIDE: Technical Specification */}
                        <div className="lg:col-span-5 flex flex-col gap-4">
                            <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
                                <div className="flex items-center gap-2 mb-5">
                                    <Activity className="w-5 h-5 text-indigo-600" />
                                    <p className="text-sm font-bold text-slate-500 uppercase tracking-wide">
                                        Barrier Specification
                                    </p>
                                </div>

                                {spec ? (
                                    <div className="space-y-4">
                                        <SpecRow
                                            label="Oxygen Transmission (OTR)"
                                            required={spec.breathable ? "Breathable" : `≤ ${spec.otr_max_cc_m2_day}`}
                                            achieved={spec.breathable ? "—" : spec.achieved_otr}
                                            unit="cc/m²/day"
                                        />
                                        <SpecRow
                                            label="Water Vapour Transmission (WVTR)"
                                            required={spec.wvtr_max_g_m2_day === null ? "Breathable" : `≤ ${spec.wvtr_max_g_m2_day}`}
                                            achieved={spec.wvtr_max_g_m2_day === null ? "—" : spec.achieved_wvtr}
                                            unit="g/m²/day"
                                        />
                                        <SpecRow
                                            label="Film Thickness"
                                            required={`${spec.film_thickness_um}`}
                                            achieved={null}
                                            unit="micron"
                                        />
                                        <SpecRow
                                            label="Mechanical Strength"
                                            required={`${spec.mechanical_strength_mpa}`}
                                            achieved={null}
                                            unit="MPa tensile"
                                        />
                                        <SpecRow
                                            label="Sealability"
                                            required={spec.sealability}
                                            achieved={null}
                                            unit=""
                                        />
                                        <SpecRow
                                            label="MAP Suitable"
                                            required={spec.map_suitable ? "Yes" : "No"}
                                            achieved={null}
                                            unit=""
                                        />
                                    </div>
                                ) : (
                                    <p className="text-sm text-slate-500">
                                        Run an analysis from the wizard to generate a full specification.
                                    </p>
                                )}
                            </div>

                            <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
                                <p className="text-sm font-bold text-slate-500 uppercase tracking-wide">Recyclability</p>
                                <p className="text-lg font-bold text-slate-900">
                                    {apiData.sustainability
                                        ? (apiData.sustainability.compostable ? 'Compostable'
                                            : apiData.sustainability.recyclable ? 'Recyclable'
                                                : 'Complex multi-layer')
                                        : (apiData.epr_green_score > 50 ? 'Highly Recyclable' : 'Complex Multi-layer')}
                                </p>
                            </div>
                        </div>

                    </div>

                    {/* Pack dimensions, film consumption and live market pricing */}
                    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 md:p-10">
                        <div className="flex items-center gap-3 mb-8">
                            <div className="p-2.5 bg-indigo-50 rounded-xl border border-indigo-100">
                                <Settings2 className="w-6 h-6 text-indigo-600" />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-slate-900">Pack Engineering &amp; Economics</h3>
                                <p className="text-sm text-slate-500 mt-0.5">
                                    Dimensions set the film area, which sets the cost per pouch.
                                </p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                            <div className="space-y-7">
                                <DimSlider label="Width" value={widthMm} onChange={setWidthMm}
                                    min={60} max={400} unit="mm" />
                                <DimSlider label="Height" value={heightMm} onChange={setHeightMm}
                                    min={80} max={500} unit="mm" />
                                <DimSlider label="Bottom gusset" value={gussetMm} onChange={setGussetMm}
                                    min={0} max={160} unit="mm" />

                                {geometry && (
                                    <div className="grid grid-cols-2 gap-3 pt-2">
                                        <MiniStat label="Flat web"
                                            value={`${geometry.geometry.web_width_mm} × ${geometry.geometry.web_height_mm}`}
                                            unit="mm" />
                                        <MiniStat label="Film per pouch"
                                            value={geometry.geometry.film_area_m2} unit="m²" />
                                        <MiniStat label="Panel area"
                                            value={geometry.geometry.panel_area_cm2} unit="cm²" />
                                        <MiniStat label="Min type height"
                                            value={geometry.geometry.min_type_height_mm} unit="mm"
                                            hint="Legal Metrology Rule 9" />
                                    </div>
                                )}
                            </div>

                            <div>
                                <p className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-4">
                                    Market price by order volume
                                </p>
                                {priceCurve ? (
                                    <PriceHistogram curve={priceCurve} />
                                ) : (
                                    <p className="text-sm text-slate-500">
                                        No marketplace pricing for this material yet.
                                    </p>
                                )}
                                {geometry?.cost && (
                                    <div className="mt-6 bg-slate-50 border border-slate-200 rounded-xl p-5">
                                        <p className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">
                                            Film cost at these dimensions
                                        </p>
                                        <p className="text-3xl font-black text-slate-900">
                                            ₹{geometry.cost.cost_per_unit}
                                            <span className="text-sm font-semibold text-slate-400"> / pouch</span>
                                        </p>
                                        <p className="text-xs text-slate-500 mt-2">
                                            {geometry.cost.film_area_m2} m² × ₹{geometry.cost.cost_per_m2}/m²,
                                            plus a {Math.round((geometry.cost.waste_factor - 1) * 100)}% trim
                                            and start-up waste allowance.
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Modified Atmosphere design - only for respiring produce */}
                    {mapDesign && (
                        <div className="bg-white rounded-2xl border border-emerald-200 shadow-sm p-8 md:p-10">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2.5 bg-emerald-50 rounded-xl border border-emerald-100">
                                    <Leaf className="w-6 h-6 text-emerald-600" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-slate-900">Modified Atmosphere Design</h3>
                                    <p className="text-sm text-slate-500 mt-0.5">
                                        Respiration rate {mapDesign.respiration_rate_at_storage} mg CO&#8322;/kg/h
                                        at storage temperature &mdash; {mapDesign.respiration_band} band
                                    </p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                                <GasTile label="Oxygen" value={mapDesign.o2_percent} tone="indigo" />
                                <GasTile label="Carbon Dioxide" value={mapDesign.co2_percent} tone="amber" />
                                <GasTile label="Nitrogen" value={mapDesign.n2_percent} tone="slate" />
                            </div>

                            <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 mb-4">
                                <p className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">
                                    Perforation Guidance
                                </p>
                                <p className="text-sm text-slate-700 leading-relaxed">{mapDesign.perforation_guidance}</p>
                                <p className="text-sm text-slate-600 mt-3">
                                    Film must admit at least{' '}
                                    <span className="font-bold text-slate-900">
                                        {mapDesign.required_o2_transmission} cc O&#8322;/kg/day
                                    </span>{' '}
                                    to match what the produce consumes.
                                </p>
                            </div>

                            {mapDesign.warnings?.map((w, i) => (
                                <div key={i} className="flex gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl mb-3">
                                    <span className="text-amber-600 font-bold shrink-0">!</span>
                                    <p className="text-sm text-amber-900 leading-relaxed">{w}</p>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Why this recommendation */}
                    {why.length > 0 && (
                        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 md:p-10">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2.5 bg-indigo-50 rounded-xl border border-indigo-100">
                                    <ShieldCheck className="w-6 h-6 text-indigo-600" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-slate-900">Why this specification</h3>
                                    <p className="text-sm text-slate-500 mt-0.5">
                                        Each rule that fired, and the input that triggered it.
                                    </p>
                                </div>
                            </div>
                            <ul className="space-y-3">
                                {why.map((r, i) => (
                                    <li key={i} className="flex gap-4 p-4 bg-slate-50 rounded-xl border border-slate-100">
                                        <code className="text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-md h-fit shrink-0 whitespace-nowrap">
                                            {r.rule}
                                        </code>
                                        <p className="text-sm text-slate-700 leading-relaxed">{r.detail}</p>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Alternatives */}
                    {alternatives.length > 0 && (
                        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 md:p-10">
                            <h3 className="text-xl font-bold text-slate-900 mb-1">Qualified alternatives</h3>
                            <p className="text-sm text-slate-500 mb-6">
                                Other materials that also meet every requirement, ranked below the primary pick.
                            </p>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm min-w-[620px]">
                                    <thead>
                                        <tr className="text-left text-xs font-bold text-slate-500 uppercase tracking-wide border-b border-slate-200">
                                            <th className="pb-3 pr-4">Material</th>
                                            <th className="pb-3 pr-4">Gauge</th>
                                            <th className="pb-3 pr-4">OTR</th>
                                            <th className="pb-3 pr-4">WVTR</th>
                                            <th className="pb-3 pr-4">Cost/m&#178;</th>
                                            <th className="pb-3">EPR</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {alternatives.map((a) => (
                                            <tr key={a.code}>
                                                <td className="py-3 pr-4 font-semibold text-slate-900">{a.name}</td>
                                                <td className="py-3 pr-4 text-slate-600">{a.specified_thickness_um} &micro;m</td>
                                                <td className="py-3 pr-4 text-slate-600">{a.effective_otr}</td>
                                                <td className="py-3 pr-4 text-slate-600">{a.effective_wvtr}</td>
                                                <td className="py-3 pr-4 text-slate-600">&#8377;{a.cost_per_m2}</td>
                                                <td className="py-3 text-slate-600">{a.epr_score}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function SpecRow({ label, required, achieved, unit }) {
    return (
        <div className="flex items-start justify-between gap-4 pb-3 border-b border-slate-100 last:border-0 last:pb-0">
            <p className="text-sm font-medium text-slate-600 leading-snug">{label}</p>
            <div className="text-right shrink-0">
                <p className="text-base font-bold text-slate-900">
                    {required} {unit && <span className="text-xs font-semibold text-slate-400">{unit}</span>}
                </p>
                {achieved !== null && achieved !== undefined && (
                    <p className="text-xs text-emerald-600 font-semibold mt-0.5">
                        achieves {achieved}
                    </p>
                )}
            </div>
        </div>
    );
}

function GasTile({ label, value, tone }) {
    const tones = {
        indigo: "bg-indigo-50 border-indigo-100 text-indigo-700",
        amber: "bg-amber-50 border-amber-100 text-amber-700",
        slate: "bg-slate-50 border-slate-200 text-slate-700",
    };
    return (
        <div className={`rounded-xl border p-5 ${tones[tone]}`}>
            <p className="text-xs font-bold uppercase tracking-wide opacity-70">{label}</p>
            <p className="text-3xl font-black mt-1">{value}<span className="text-lg">%</span></p>
        </div>
    );
}

function DimSlider({ label, value, onChange, min, max, unit }) {
    return (
        <div>
            <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-bold text-slate-700">{label}</label>
                <div className="flex items-center gap-2">
                    <input
                        type="number" min={min} max={max} value={value}
                        onChange={(e) => onChange(Number(e.target.value) || min)}
                        className="w-20 px-2.5 py-1.5 text-right bg-white border border-slate-300 rounded-md text-sm font-bold outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="text-sm font-semibold text-slate-500 w-7">{unit}</span>
                </div>
            </div>
            <input
                type="range" min={min} max={max} step="5" value={value}
                onChange={(e) => onChange(Number(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
        </div>
    );
}

function MiniStat({ label, value, unit, hint }) {
    return (
        <div className="bg-slate-50 border border-slate-100 rounded-lg p-3">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">{label}</p>
            <p className="text-base font-bold text-slate-900 mt-0.5">
                {value} <span className="text-xs font-semibold text-slate-400">{unit}</span>
            </p>
            {hint && <p className="text-[10px] text-slate-400 mt-0.5">{hint}</p>}
        </div>
    );
}

function PriceHistogram({ curve }) {
    const points = curve.points.filter((p) => p.best_price != null);
    if (points.length === 0) {
        return <p className="text-sm text-slate-500">No supplier meets these volumes yet.</p>;
    }
    const max = Math.max(...points.map((p) => p.best_price));

    return (
        <div>
            <div className="flex items-end gap-2 h-44">
                {points.map((p) => (
                    <div key={p.quantity} className="flex-1 flex flex-col items-center justify-end h-full">
                        <span className="text-[11px] font-bold text-slate-900 mb-1">₹{p.best_price}</span>
                        <div
                            className="w-full bg-indigo-500 rounded-t-md transition-all duration-500 hover:bg-indigo-600"
                            style={{ height: `${(p.best_price / max) * 100}%` }}
                            title={`${p.offer_count} offer(s), avg ₹${p.average_price}`}
                        />
                    </div>
                ))}
            </div>
            <div className="flex gap-2 mt-2">
                {points.map((p) => (
                    <span key={p.quantity} className="flex-1 text-center text-[10px] font-semibold text-slate-500">
                        {p.quantity >= 1000 ? `${p.quantity / 1000}k` : p.quantity}
                    </span>
                ))}
            </div>
            <p className="text-xs text-slate-500 mt-3">
                Best live quote across {curve.vendor_count} supplier
                {curve.vendor_count === 1 ? '' : 's'} at each MOQ break.
            </p>
        </div>
    );
}
