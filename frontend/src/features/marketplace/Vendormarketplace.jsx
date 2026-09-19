import React, { useState } from 'react';
import Navbar from '../../components/Navbar';
import {
    Search, Star, ShieldCheck, MapPin, Truck,
    Package, Filter, ExternalLink, Award, Layers, CheckCircle2
} from 'lucide-react';

export default function VendorMarketplace() {
    const [searchQuery, setSearchQuery] = useState("");
    const [activeFilter, setActiveFilter] = useState("All");

    // Comprehensive Food & Beverage Packaging Vendors Catalog
    const vendors = [
        {
            id: 1,
            name: "FlexiPack Solutions Ltd.",
            packagingType: "Metallized Barrier Pouches",
            category: "Flexible",
            rating: 4.8,
            reviews: 142,
            location: "Mumbai, Maharashtra",
            specialty: "Metallized PET / PE Laminates (3-Ply)",
            suitableFor: "Dry snacks, savouries, spices, roasted nuts",
            moq: "10,000 units",
            leadTime: "12 Days",
            fssaiVerified: true,
            ecoFriendly: false,
            tags: ["High O2 Barrier", "Nitrogen Flush", "Ziplock Ready"]
        },
        {
            id: 2,
            name: "AsepticTech Systems",
            packagingType: "Aseptic Brick Cartons",
            category: "Liquid & Aseptic",
            rating: 4.9,
            reviews: 198,
            location: "Pune, Maharashtra",
            specialty: "6-Layer Paperboard/Alu/PE Aseptic Cartons",
            suitableFor: "Juices, RTD tea/coffee, milk, plant-based dairy",
            moq: "50,000 units",
            leadTime: "20 Days",
            fssaiVerified: true,
            ecoFriendly: true,
            tags: ["Long Shelf Life", "UHT Compatible", "FSC Certified"]
        },
        {
            id: 3,
            name: "Apex Liquid Pouches",
            packagingType: "Spouted Stand-Up Pouches",
            category: "Liquid & Aseptic",
            rating: 4.7,
            reviews: 110,
            location: "Bengaluru, Karnataka",
            specialty: "PET / ALU / NYLON / CPP with Center/Corner Spout",
            suitableFor: "Fruit juices, purees, edible oils, sauces",
            moq: "15,000 units",
            leadTime: "14 Days",
            fssaiVerified: true,
            ecoFriendly: false,
            tags: ["Hot Fill (85°C)", "Spill-Proof Spout", "High Puncture Resistance"]
        },
        {
            id: 4,
            name: "IndoRetort Packaging",
            packagingType: "Retort Pouches & Trays",
            category: "Retort & Barrier",
            rating: 4.9,
            reviews: 86,
            location: "Hyderabad, Telangana",
            specialty: "4-Ply High-Barrier Retort Laminates (PET/ALU/OPA/R-CPP)",
            suitableFor: "Ready-to-Eat (RTE) curries, gravies, meat, baby foods",
            moq: "20,000 units",
            leadTime: "18 Days",
            fssaiVerified: true,
            ecoFriendly: false,
            tags: ["121°C Autoclave Safe", "Zero OTR", "24-Month Shelf Life"]
        },
        {
            id: 5,
            name: "PurePoly Containers",
            packagingType: "Rigid PET & HDPE Bottles",
            category: "Rigid Plastic",
            rating: 4.6,
            reviews: 230,
            location: "Ahmedabad, Gujarat",
            specialty: "Hot-Fill PET Bottles & Wide-Mouth HDPE Jars",
            suitableFor: "Cold-pressed juices, dairy drinks, honey, nut butters",
            moq: "8,000 units",
            leadTime: "7 Days",
            fssaiVerified: true,
            ecoFriendly: true,
            tags: ["Food Grade Resin", "Hot Fill Capable", "100% Recyclable (Code 1)"]
        },
        {
            id: 6,
            name: "Silica Glass Works",
            packagingType: "Flint & Amber Glass Bottles",
            category: "Glass & Metal",
            rating: 4.8,
            reviews: 165,
            location: "Firozabad, Uttar Pradesh",
            specialty: "USP Type III Soda-Lime Glass Bottles & Lug Jars",
            suitableFor: "High-acid citrus juices, jams, pickles, syrups, oils",
            moq: "12,000 units",
            leadTime: "10 Days",
            fssaiVerified: true,
            ecoFriendly: true,
            tags: ["100% Inert", "Zero Leaching", "Hermetic Lug Cap Ready"]
        },
        {
            id: 7,
            name: "Bharat Can & Metal Closures",
            packagingType: "Aluminum Beverage Cans & TFS Tins",
            category: "Glass & Metal",
            rating: 4.7,
            reviews: 140,
            location: "Chennai, Tamil Nadu",
            specialty: "2-Piece Drawn Aluminum Beverage Cans (250ml / 330ml)",
            suitableFor: "Sparkling fruit juices, RTD beverages, cold brew, tonic",
            moq: "40,000 units",
            leadTime: "15 Days",
            fssaiVerified: true,
            ecoFriendly: true,
            tags: ["Light Block 100%", "Infinitely Recyclable", "Internal BPA-NI Lining"]
        },
        {
            id: 8,
            name: "EcoWrap Bio-Plastics",
            packagingType: "Compostable PLA & Mono-PE Pouches",
            category: "Eco-Friendly",
            rating: 4.9,
            reviews: 95,
            location: "Coimbatore, Tamil Nadu",
            specialty: "Certified Industrial Compostable (PLA/PBAT) & Mono-PE",
            suitableFor: "Organic snacks, confectionery, flour, grains, dried fruits",
            moq: "5,000 units",
            leadTime: "10 Days",
            fssaiVerified: true,
            ecoFriendly: true,
            tags: ["EPR Credit Ready", "ASTM D6400 Certified", "Mono-material Recycle"]
        },
        {
            id: 9,
            name: "CanisterKraft Technologies",
            packagingType: "Composite Cans & Kraft Paper Pouches",
            category: "Paper & Board",
            rating: 4.6,
            reviews: 78,
            location: "Gurugram, Haryana",
            specialty: "Spiral-Wound Paperboard Canisters with Foil Barrier & Peel-Off Membrane",
            suitableFor: "Nutritional powders, protein mix, tea, confectionery, chips",
            moq: "5,000 units",
            leadTime: "12 Days",
            fssaiVerified: true,
            ecoFriendly: true,
            tags: ["Aroma Tight", "Tamper Evident Membrane", "Premium Shelf Appeal"]
        },
        {
            id: 10,
            name: "CryoVac Barrier Films",
            packagingType: "Thermoforming Vacuum & MAP Films",
            category: "Flexible",
            rating: 4.7,
            reviews: 84,
            location: "Vadodara, Gujarat",
            specialty: "9-Layer Co-extruded EVOH High-Barrier Skin & Lid Films",
            suitableFor: "Fresh cut fruits, paneer, cheese, processed meat, seafood",
            moq: "15,000 units",
            leadTime: "14 Days",
            fssaiVerified: true,
            ecoFriendly: false,
            tags: ["Ultra Low OTR/WVTR", "Anti-Fog Coating", "Gas Flushing Ready"]
        }
    ];

    // Filter Categories list
    const filterCategories = [
        "All",
        "Flexible",
        "Liquid & Aseptic",
        "Retort & Barrier",
        "Rigid Plastic",
        "Glass & Metal",
        "Eco-Friendly",
        "Paper & Board"
    ];

    // Multi-variable search and category filtering
    const filteredVendors = vendors.filter(vendor => {
        const matchesSearch =
            vendor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            vendor.specialty.toLowerCase().includes(searchQuery.toLowerCase()) ||
            vendor.packagingType.toLowerCase().includes(searchQuery.toLowerCase()) ||
            vendor.suitableFor.toLowerCase().includes(searchQuery.toLowerCase());

        if (activeFilter === "All") return matchesSearch;
        return matchesSearch && vendor.category === activeFilter;
    });

    return (
        <div className="min-h-screen bg-slate-50 font-sans flex flex-col">
            <Navbar />

            <div className="flex-1 max-w-[1500px] w-full mx-auto px-6 lg:px-12 py-10">

                {/* Page Header */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
                    <div>
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-700 text-xs font-bold rounded-full mb-3 border border-indigo-100">
                            <Layers className="w-3.5 h-3.5" /> FSSAI-Compliant Packaging Sourcing
                        </div>
                        <h1 className="text-3xl lg:text-4xl font-extrabold text-slate-900 tracking-tight">Vendor Marketplace</h1>
                        <p className="text-slate-500 mt-2 text-base">Direct procurement access to certified converters for flexible, rigid, aseptic, and eco-friendly formats.</p>
                    </div>

                    {/* Search Bar */}
                    <div className="flex items-center gap-3 w-full md:w-auto">
                        <div className="relative flex-1 md:w-96">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                <Search className="h-5 w-5 text-slate-400" />
                            </div>
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search pouches, aseptic cartons, PET bottles, glass..."
                                className="w-full pl-11 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none shadow-sm transition-all"
                            />
                        </div>
                        <button className="p-3 bg-white border border-slate-200 text-slate-600 rounded-xl hover:bg-slate-50 hover:text-indigo-600 shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 flex-shrink-0">
                            <Filter className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Category Filter Pills */}
                <div className="flex items-center gap-2.5 mb-8 overflow-x-auto pb-2 scrollbar-hide">
                    {filterCategories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => setActiveFilter(cat)}
                            className={`px-5 py-2.5 rounded-xl text-sm font-bold whitespace-nowrap transition-all shadow-sm border ${activeFilter === cat
                                    ? 'bg-slate-900 text-white border-slate-900 shadow-slate-900/10'
                                    : 'bg-white text-slate-600 border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 hover:text-indigo-700'
                                }`}
                        >
                            {cat}
                        </button>
                    ))}
                </div>

                {/* Vendors Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredVendors.map((vendor) => (
                        <div
                            key={vendor.id}
                            className="bg-white rounded-2xl border border-slate-200 p-7 shadow-sm hover:shadow-xl hover:border-indigo-300 transition-all flex flex-col justify-between group"
                        >
                            <div>
                                {/* Header & Badges */}
                                <div className="flex justify-between items-start mb-3">
                                    <div>
                                        <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-md">
                                            {vendor.packagingType}
                                        </span>
                                        <h3 className="text-xl font-bold text-slate-900 mt-2 group-hover:text-indigo-600 transition-colors">
                                            {vendor.name}
                                        </h3>
                                    </div>

                                    {vendor.fssaiVerified && (
                                        <div className="flex items-center gap-1 px-2 py-1 bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-lg text-xs font-bold shrink-0">
                                            <ShieldCheck className="w-4 h-4" />
                                            <span>FSSAI</span>
                                        </div>
                                    )}
                                </div>

                                {/* Rating & Location */}
                                <div className="flex items-center gap-3 text-xs text-slate-500 font-medium mb-4">
                                    <div className="flex items-center gap-1 text-amber-500 font-bold">
                                        <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                                        <span>{vendor.rating}</span>
                                        <span className="text-slate-400 font-normal">({vendor.reviews})</span>
                                    </div>
                                    <span>•</span>
                                    <div className="flex items-center gap-1">
                                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                                        <span className="truncate">{vendor.location}</span>
                                    </div>
                                </div>

                                {/* Technical Material Spec */}
                                <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-100 mb-4">
                                    <div className="flex items-center gap-1.5 text-slate-400 mb-1">
                                        <Package className="w-3.5 h-3.5 text-indigo-600" />
                                        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Material Specification</span>
                                    </div>
                                    <p className="text-sm font-bold text-slate-800 leading-snug">{vendor.specialty}</p>

                                    <div className="mt-2.5 pt-2.5 border-t border-slate-200/60">
                                        <p className="text-xs text-slate-500 leading-relaxed">
                                            <strong className="text-slate-700">Suitable For:</strong> {vendor.suitableFor}
                                        </p>
                                    </div>
                                </div>

                                {/* Feature Badges */}
                                <div className="flex flex-wrap gap-1.5 mb-6">
                                    {vendor.tags.map(tag => (
                                        <span key={tag} className="px-2.5 py-1 bg-slate-100 text-slate-600 rounded-md text-[11px] font-semibold">
                                            {tag}
                                        </span>
                                    ))}
                                    {vendor.ecoFriendly && (
                                        <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-md text-[11px] font-bold flex items-center gap-1">
                                            <Award className="w-3 h-3" /> Eco Choice
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Specs and Order Info Footer */}
                            <div>
                                <div className="grid grid-cols-2 gap-3 py-3 border-t border-slate-100 text-xs mb-4">
                                    <div>
                                        <span className="text-slate-400 block font-medium">Min. Order (MOQ)</span>
                                        <span className="font-bold text-slate-900 text-sm">{vendor.moq}</span>
                                    </div>
                                    <div>
                                        <span className="text-slate-400 block font-medium">Mfg. Lead Time</span>
                                        <span className="font-bold text-slate-900 text-sm flex items-center gap-1 mt-0.5">
                                            <Truck className="w-3.5 h-3.5 text-slate-500" /> {vendor.leadTime}
                                        </span>
                                    </div>
                                </div>

                                {/* Quote Action */}
                                <button className="w-full py-3 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-indigo-600 transition-colors flex items-center justify-center gap-2 shadow-sm focus:ring-4 focus:ring-slate-200">
                                    Request Sample / RFQ <ExternalLink className="w-4 h-4" />
                                </button>
                            </div>

                        </div>
                    ))}
                </div>

                {/* Empty State */}
                {filteredVendors.length === 0 && (
                    <div className="text-center py-20 bg-white rounded-2xl border border-slate-200 mt-6">
                        <Package className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                        <h3 className="text-lg font-bold text-slate-900">No packaging suppliers found</h3>
                        <p className="text-slate-500 mt-1">Try refining your search keyword or switching category tabs.</p>
                    </div>
                )}

            </div>
        </div>
    );
}