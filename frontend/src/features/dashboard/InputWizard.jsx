import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar';
import React, { useState } from 'react';
import {
    Box, TestTubes, ThermometerSnowflake,
    ArrowRight, Bot, CheckCircle2, Factory,
    Search, ChevronDown
} from 'lucide-react';

export default function InputWizard() {
    const [activeSection, setActiveSection] = useState(1);
    const navigate = useNavigate();

    // --- HOISTED STATE (Shared across steps) ---
    const [productCategory, setProductCategory] = useState("");
    const [isAiEnabled, setIsAiEnabled] = useState(true);
    const [storageTemp, setStorageTemp] = useState("Ambient");

    // Logic to determine if the selected category is typically a liquid
    const isLiquid = productCategory.toLowerCase().includes("beverage") ||
        productCategory.toLowerCase().includes("dairy") ||
        productCategory.toLowerCase().includes("oil");

    // NEW: Technical Spec States
    const [moisture, setMoisture] = useState(10.0);
    const [lipid, setLipid] = useState("Low (<5%)");
    const [ph, setPh] = useState(7.0);
    const [fillingProcess, setFillingProcess] = useState("Standard Ambient Fill");

    // NEW: Auto-fill technical specs when AI is enabled and category changes
    React.useEffect(() => {
        if (!isAiEnabled) return;

        const cat = productCategory.toLowerCase();

        if (cat.includes("dairy") || cat.includes("milk") || cat.includes("ice")) {
            setMoisture(85.0); setLipid("Medium (5-20%)"); setPh(6.7); setFillingProcess("Aseptic / Cold Fill");
        } else if (cat.includes("beverage") || cat.includes("juice")) {
            setMoisture(90.0); setLipid("Low (<5%)"); setPh(3.5); setFillingProcess("Hot Fill (Up to 85°C)");
        } else if (cat.includes("nut") || cat.includes("seed") || cat.includes("fats")) {
            setMoisture(2.0); setLipid("High (>20%) - Requires O2 Barrier"); setPh(7.0); setFillingProcess("N/A - Solid product");
        } else if (cat.includes("fruit") || cat.includes("vegetable") || cat.includes("potato")) {
            setMoisture(75.0); setLipid("Low (<5%)"); setPh(5.5); setFillingProcess("N/A - Solid product");
        } else if (cat.includes("bakery") || cat.includes("cereal") || cat.includes("savoury")) {
            setMoisture(5.0); setLipid("Medium (5-20%)"); setPh(6.0); setFillingProcess("N/A - Solid product");
        } else {
            // Default reset
            setMoisture(10.0); setLipid("Low (<5%)"); setPh(7.0); setFillingProcess("Standard Ambient Fill");
        }
    }, [productCategory, isAiEnabled]);

    const handleRunAnalysis = async () => {
        // 1. Check for token before allowing the request
        const token = localStorage.getItem("access_token");
        if (!token) {
            alert("Security Lock: Please log in to run AI analysis.");
            navigate('/login'); // Sends them to the login page
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // 2. Send the VIP pass!
                },
                body: JSON.stringify({
                    product_name: "User Product",
                    fssai_category: productCategory || "Unknown",
                    shelf_life_days: 90,
                    is_liquid: isLiquid,
                    moisture_content: Number(moisture),
                    lipid_content: lipid.split(" ")[0],
                    ph_level: isLiquid ? Number(ph) : null,
                    filling_process: isLiquid ? fillingProcess : "None"
                })
            });

            if (response.status === 401) {
                alert("Session expired. Please log in again.");
                localStorage.removeItem("access_token");
                navigate('/login');
                return;
            }

            const result = await response.json();

            if (result.status === "success") {
                navigate('/results', { state: { apiData: result.data } });
            }
        } catch (error) {
            console.error("Failed to connect to AI Engine:", error);
            alert("Ensure your FastAPI server is running on port 8000!");
        }
    };

    const result = await response.json();

    // Navigate to the results page and pass the API data along
    if (result.status === "success") {
        navigate('/results', { state: { apiData: result.data } });
    }
} catch (error) {
    console.error("Failed to connect to AI Engine:", error);
    alert("Ensure your FastAPI server is running on port 8000!");
}
    };

return (
    <div className="flex flex-col min-h-screen bg-slate-50 font-sans">
        <Navbar />

        {/* Main Content Split Area */}
        <div className="flex flex-1 h-[calc(100vh-80px)] overflow-hidden">

            {/* LEFT SIDEBAR - Increased Width and Full Height */}
            <div className="hidden lg:flex flex-col w-96 bg-slate-900 text-white p-10 shadow-2xl z-10 overflow-y-auto">
                <div className="flex items-center gap-4 mb-16">
                    <div className="p-2.5 bg-indigo-500 rounded-xl shadow-lg">
                        <Factory className="w-7 h-7 text-white" />
                    </div>
                    <h1 className="text-2xl font-extrabold tracking-tight">PackGenius AI</h1>
                </div>

                <div className="space-y-10 flex-1 relative">
                    <StepIndicator
                        num={1} title="Product Profile" desc="Basic food characteristics"
                        active={activeSection === 1} icon={<Box size={20} />}
                    />
                    <StepIndicator
                        num={2} title="Technical Specs" desc="Moisture, pH & chemistry"
                        active={activeSection === 2} icon={<TestTubes size={20} />}
                    />
                    <StepIndicator
                        num={3} title="Supply Chain" desc="Storage & transit environment"
                        active={activeSection === 3} icon={<ThermometerSnowflake size={20} />}
                    />
                </div>

                <div className="mt-auto pt-8 border-t border-slate-700/50">
                    <div className="flex items-center gap-3 text-slate-400 text-sm">
                        <Bot size={18} className="text-indigo-400" />
                        <span>AI Engine Status: <span className="text-emerald-400 font-medium">Ready</span></span>
                    </div>
                </div>
            </div>

            {/* RIGHT CONTENT - Continuous Scroll Form */}
            <div className="flex-1 flex flex-col h-full overflow-y-auto scroll-smooth pb-24">
                <div className="max-w-4xl w-full mx-auto p-8 md:p-12 lg:p-16">

                    <div className="mb-10">
                        <h2 className="text-3xl font-extrabold text-slate-900">
                            Configure Packaging Parameters
                        </h2>
                        <p className="text-base text-slate-500 mt-2">Provide the details below to generate your FSSAI-compliant material specs.</p>
                    </div>

                    {/* Form Containers - Stacked Vertically */}
                    <div className="space-y-8">

                        {/* Section 1: Product Profile */}
                        <div
                            onClick={() => setActiveSection(1)}
                            onFocus={() => setActiveSection(1)}
                            className={`transition-all duration-300 bg-white rounded-2xl p-10 border-2 ${activeSection === 1 ? 'border-indigo-600 shadow-xl ring-4 ring-indigo-50' : 'border-slate-200 shadow-sm opacity-60 hover:opacity-100 cursor-pointer'}`}
                        >
                            <div className="mb-8 border-b border-slate-100 pb-4">
                                <h3 className="text-xl font-bold text-slate-900">1. Define Product Profile</h3>
                            </div>
                            <StepOne productCategory={productCategory} setProductCategory={setProductCategory} />
                        </div>

                        {/* Section 2: Technical Specs */}
                        <div
                            onClick={() => setActiveSection(2)}
                            onFocus={() => setActiveSection(2)}
                            className={`transition-all duration-300 bg-white rounded-2xl p-10 border-2 ${activeSection === 2 ? 'border-indigo-600 shadow-xl ring-4 ring-indigo-50' : 'border-slate-200 shadow-sm opacity-60 hover:opacity-100 cursor-pointer'}`}
                        >
                            <div className="mb-8 border-b border-slate-100 pb-4">
                                <h3 className="text-xl font-bold text-slate-900">2. Technical Parameters</h3>
                            </div>
                            <StepTwo
                                isAiEnabled={isAiEnabled} setIsAiEnabled={setIsAiEnabled} isLiquid={isLiquid}
                                moisture={moisture} setMoisture={setMoisture}
                                lipid={lipid} setLipid={setLipid}
                                ph={ph} setPh={setPh}
                                fillingProcess={fillingProcess} setFillingProcess={setFillingProcess}
                            />                        </div>

                        {/* Section 3: Supply Chain */}
                        <div
                            onClick={() => setActiveSection(3)}
                            onFocus={() => setActiveSection(3)}
                            className={`transition-all duration-300 bg-white rounded-2xl p-10 border-2 ${activeSection === 3 ? 'border-indigo-600 shadow-xl ring-4 ring-indigo-50' : 'border-slate-200 shadow-sm opacity-60 hover:opacity-100 cursor-pointer'}`}
                        >
                            <div className="mb-8 border-b border-slate-100 pb-4">
                                <h3 className="text-xl font-bold text-slate-900">3. Supply Chain Environment</h3>
                            </div>
                            <StepThree storageTemp={storageTemp} setStorageTemp={setStorageTemp} />
                        </div>

                    </div>

                    {/* Navigation Footer */}
                    <div className="mt-12 flex justify-end">
                        <button
                            onClick={handleRunAnalysis}
                            className="flex items-center px-8 py-4 bg-slate-900 text-white rounded-xl font-bold text-lg hover:bg-slate-800 transition-all shadow-xl shadow-slate-900/20 focus:ring-4 focus:ring-slate-200"
                        >
                            Run AI Analysis
                            <ArrowRight className="w-5 h-5 ml-3 text-emerald-400" />
                        </button>
                    </div>

                </div>
            </div>

        </div>
    </div>
);
}

// --- Professional Sub-Components ---

function StepIndicator({ num, title, desc, active, icon }) {
    return (
        <div className={`flex gap-5 transition-opacity duration-300 ${active ? 'opacity-100' : 'opacity-40'}`}>
            <div className="relative flex flex-col items-center">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-300 z-10 
          ${active ? 'bg-indigo-600 border-indigo-500 text-white shadow-[0_0_20px_rgba(79,70,229,0.4)] scale-110' : 'bg-slate-800 border-slate-600 text-slate-400'}`}>
                    {icon}
                </div>
            </div>
            <div className="pt-1">
                <h3 className={`text-base font-bold ${active ? 'text-white' : 'text-slate-300'}`}>{title}</h3>
                <p className="text-sm text-slate-400 mt-1">{desc}</p>
            </div>
        </div>
    );
}
function StepOne({ productCategory, setProductCategory }) {
    const [searchQuery, setSearchQuery] = useState(productCategory || "");
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);

    // Pointing to image files in your public/icons folder
    const fssaiCategories = [
        { id: "01", name: "Dairy products and analogues", image: "/public/icon/Dairy_products_and_analogues.png" },
        { id: "02", name: "Fats and oils, and fat emulsions", image: "/public/icon/Fats_and_oils_and_fat_emulsions.png" },
        { id: "03", name: "Edible ices, sherbet and sorbet", image: "/public/icon/Edible_ices_sherbet_and_sorbet.png" },
        { id: "04", name: "Fruits, vegetables, nuts and seeds", image: "/public/icon/Fruits_vegetables_nuts_and_seeds.png" },
        { id: "05", name: "Confectionery", image: "/public/icon/Confectionery.png" },
        { id: "06", name: "Cereals and cereal products", image: "/public/icon/Cereals_and_cereal_products.png" },
        { id: "07", name: "Bakery products", image: "/public/icon/Bakery_products.png" },
        { id: "08", name: "Sweeteners, including honey", image: "/public/icon/Sweeteners_including_honey.png" },
        { id: "09", name: "Salts, spices, soups, sauces and salads", image: "/public/icon/Salts_spices_soups_sauces_and_salads.png" },
        { id: "10", name: "Foodstuffs for nutritional uses", image: "/public/icon/Foodstuffs_for_nutritional_uses.png" },
        { id: "11", name: "Beverages, excluding dairy products", image: "/public/icon/Beverages_excluding_dairy_products.png" },
        { id: "12", name: "Ready-to-eat savouries", image: "/public/icon/Ready-to-eat_savouries.png" },
        { id: "13", name: "Prepared foods", image: "/public/icon/Prepared_foods.png" },
        { id: "99", name: "Substances added to food", image: "/public/icon/Substances_added_to_food.png" }
    ];

    // Filter categories based on user input
    const filteredCategories = fssaiCategories.filter(cat =>
        cat.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <label className="block text-sm font-bold text-slate-700 mb-2">Product Name</label>
                    <input type="text" placeholder="e.g., Premium Cold-Pressed Apple Juice"
                        className="w-full px-5 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-base focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none transition-all placeholder:text-slate-400" />
                </div>

                {/* Searchable Custom Dropdown */}
                <div className="relative">
                    <label className="block text-sm font-bold text-slate-700 mb-2">FSSAI Category</label>
                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <Search className="h-5 w-5 text-slate-400" />
                        </div>
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => {
                                setSearchQuery(e.target.value);
                                setProductCategory(e.target.value); // Sync to parent
                                setIsDropdownOpen(true);
                            }}
                            onFocus={() => setIsDropdownOpen(true)}
                            onBlur={() => setTimeout(() => setIsDropdownOpen(false), 200)}
                            placeholder="Search matrix (e.g., Dairy)..."
                            className="w-full pl-11 pr-10 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-base focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none transition-all text-slate-700 placeholder:text-slate-400"
                        />
                        <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
                            <ChevronDown className="h-5 w-5 text-slate-400" />
                        </div>
                    </div>

                    {/* Dropdown Menu */}
                    {isDropdownOpen && (
                        <div className="absolute z-50 w-full mt-2 bg-white border border-slate-200 rounded-xl shadow-xl max-h-60 overflow-y-auto">
                            {filteredCategories.length > 0 ? (
                                filteredCategories.map((category) => (
                                    <div
                                        key={category.id}
                                        // Changed onClick to onMouseDown right here!
                                        onMouseDown={(e) => {
                                            e.preventDefault(); // Prevents input from losing focus immediately
                                            setSearchQuery(category.name);
                                            setProductCategory(category.name);
                                            setIsDropdownOpen(false);
                                        }}
                                        className="flex items-center gap-4 px-5 py-3.5 hover:bg-indigo-50 cursor-pointer text-slate-700 text-sm font-medium transition-colors border-b border-slate-50 last:border-0"
                                    >
                                        <img
                                            src={category.image}
                                            alt={category.name}
                                            className="w-7 h-7 object-contain bg-white rounded-md border border-slate-100 p-0.5 shadow-sm"
                                            onError={(e) => {
                                                e.target.src = "https://placehold.co/100x100/e2e8f0/64748b?text=" + category.id;
                                            }}
                                        />
                                        <span>{category.name}</span>
                                    </div>
                                ))
                            ) : (
                                <div className="px-5 py-4 text-sm text-slate-500 text-center">
                                    No matching categories found.
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Target Shelf Life Requirement</label>
                <div className="flex items-center gap-3">
                    <input type="number" placeholder="180" className="w-40 px-5 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-base focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none transition-all" />
                    <span className="text-base font-semibold text-slate-500">Days</span>
                </div>
            </div>
        </div>
    );
}
function StepTwo({ isAiEnabled, setIsAiEnabled, isLiquid, moisture, setMoisture, lipid, setLipid, ph, setPh, fillingProcess, setFillingProcess }) {
    const inputClass = `w-full px-5 py-3.5 border rounded-xl text-base outline-none transition-all ${isAiEnabled ? 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed' : 'bg-slate-50 border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:bg-white text-slate-900'}`;
    const liquidDisabledClass = `w-full px-5 py-3.5 border rounded-xl text-base outline-none transition-all bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed`;

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between p-5 bg-indigo-50 border border-indigo-100 rounded-xl">
                <div className="flex items-center gap-4">
                    <div className="p-2.5 bg-indigo-100 text-indigo-600 rounded-lg"><Bot size={20} /></div>
                    <div>
                        <h4 className="text-base font-bold text-indigo-900">AI Smart-Fill Enabled</h4>
                        <p className="text-sm text-indigo-700 mt-0.5">Estimating technical values based on standard product categories.</p>
                    </div>
                </div>
                <button
                    onClick={() => setIsAiEnabled(!isAiEnabled)}
                    className={`w-14 h-8 rounded-full relative cursor-pointer focus:outline-none transition-colors duration-300 ${isAiEnabled ? 'bg-indigo-600' : 'bg-slate-300'}`}
                >
                    <span className={`absolute top-1 w-6 h-6 bg-white rounded-full shadow-sm transition-all duration-300 ${isAiEnabled ? 'right-1' : 'left-1'}`}></span>
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <label className="block text-sm font-bold text-slate-700 mb-2">Moisture / Water Activity</label>
                    <input
                        type="number" step="0.1"
                        value={moisture}
                        onChange={(e) => setMoisture(e.target.value)}
                        disabled={isAiEnabled}
                        className={inputClass}
                    />
                </div>
                <div>
                    <label className="block text-sm font-bold text-slate-700 mb-2">Lipid/Fat Content</label>
                    <select value={lipid} onChange={(e) => setLipid(e.target.value)} disabled={isAiEnabled} className={inputClass}>
                        <option>Low (&lt;5%)</option>
                        <option>Medium (5-20%)</option>
                        <option>High (&gt;20%) - Requires O2 Barrier</option>
                    </select>
                </div>

                <div>
                    <label className={`block text-sm font-bold mb-2 ${!isLiquid ? 'text-slate-400' : 'text-slate-700'}`}>
                        pH Level (Acidity)
                    </label>
                    <input
                        type={!isLiquid ? "text" : "number"} step="0.1"
                        value={!isLiquid ? "" : ph}
                        onChange={(e) => setPh(e.target.value)}
                        disabled={!isLiquid || isAiEnabled}
                        placeholder={!isLiquid ? "N/A - Solid product" : "Enter pH..."}
                        className={!isLiquid ? liquidDisabledClass : inputClass}
                    />
                </div>
                <div>
                    <label className={`block text-sm font-bold mb-2 ${!isLiquid ? 'text-slate-400' : 'text-slate-700'}`}>
                        Filling Process
                    </label>
                    <select
                        value={fillingProcess}
                        onChange={(e) => setFillingProcess(e.target.value)}
                        disabled={!isLiquid || isAiEnabled}
                        className={!isLiquid ? liquidDisabledClass : inputClass}
                    >
                        {!isLiquid ? (
                            <option>N/A - Solid product</option>
                        ) : (
                            <>
                                <option>Aseptic / Cold Fill</option>
                                <option>Hot Fill (Up to 85°C)</option>
                                <option>Retort Sterilization (121°C)</option>
                                <option>Standard Ambient Fill</option>
                            </>
                        )}
                    </select>
                </div>
            </div>
        </div>
    );
}
function StepThree({ storageTemp, setStorageTemp }) {
    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Interactive Radio Card 1 - Ambient */}
                <label
                    onClick={() => setStorageTemp("Ambient")}
                    className={`relative flex flex-col p-6 border-2 rounded-xl cursor-pointer transition-colors ${storageTemp === "Ambient"
                        ? "border-indigo-600 bg-indigo-50/50"
                        : "border-slate-200 bg-white hover:border-slate-300"
                        }`}
                >
                    <input type="radio" name="storage" className="absolute opacity-0" checked={storageTemp === "Ambient"} readOnly />
                    <div className="flex justify-between items-start mb-4">
                        <span className={`text-base font-bold ${storageTemp === "Ambient" ? "text-indigo-900" : "text-slate-900"}`}>Ambient Storage</span>
                        {storageTemp === "Ambient" ? (
                            <CheckCircle2 className="text-indigo-600 w-6 h-6" />
                        ) : (
                            <div className="w-6 h-6 border-2 border-slate-300 rounded-full" />
                        )}
                    </div>
                    <p className={`text-sm leading-relaxed ${storageTemp === "Ambient" ? "text-indigo-700/80" : "text-slate-500"}`}>
                        Standard warehouse and retail shelving. Temperatures fluctuating between 20°C and 35°C.
                    </p>
                </label>

                {/* Interactive Radio Card 2 - Cold Chain */}
                <label
                    onClick={() => setStorageTemp("Cold Chain")}
                    className={`relative flex flex-col p-6 border-2 rounded-xl cursor-pointer transition-colors ${storageTemp === "Cold Chain"
                        ? "border-indigo-600 bg-indigo-50/50"
                        : "border-slate-200 bg-white hover:border-slate-300"
                        }`}
                >
                    <input type="radio" name="storage" className="absolute opacity-0" checked={storageTemp === "Cold Chain"} readOnly />
                    <div className="flex justify-between items-start mb-4">
                        <span className={`text-base font-bold ${storageTemp === "Cold Chain" ? "text-indigo-900" : "text-slate-900"}`}>Cold Chain (Chilled)</span>
                        {storageTemp === "Cold Chain" ? (
                            <CheckCircle2 className="text-indigo-600 w-6 h-6" />
                        ) : (
                            <div className="w-6 h-6 border-2 border-slate-300 rounded-full" />
                        )}
                    </div>
                    <p className={`text-sm leading-relaxed ${storageTemp === "Cold Chain" ? "text-indigo-700/80" : "text-slate-500"}`}>
                        Strictly refrigerated logistics network. Maintained consistently between 2°C and 8°C.
                    </p>
                </label>

            </div>
        </div>
    );
}