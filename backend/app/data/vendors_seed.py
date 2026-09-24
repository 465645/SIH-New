"""Seed vendors and their catalogues.

Ported from the hardcoded array that previously lived in the marketplace page,
extended with the tiered MOQ pricing the PRD calls for and linked to the
packaging material codes so a recommendation can be matched to real supply.

Prices are indicative per-unit rates for a 250 g stand-up pouch at each MOQ
break, in INR.
"""

VENDORS = [
    dict(
        name="FlexiPack Solutions Ltd.", location="Mumbai, Maharashtra",
        rating=4.8, reviews=142, fssai_verified=True, eco_friendly=False,
        lead_time_days=12,
        about="Rotogravure converter specialising in metallized barrier laminates "
              "for the Indian snack sector.",
        products=[
            dict(material_code="MET-PET", title="Metallized PET/PE Barrier Pouch",
                 structure="MET-PET12 / PE60", thickness_um=72,
                 min_order_qty=10000, lead_time_days=12,
                 tiers=[(10000, 3.10), (50000, 2.72), (100000, 2.44)]),
            dict(material_code="BOPP", title="BOPP Printed Pillow Pouch",
                 structure="BOPP20 / BOPP25", thickness_um=45,
                 min_order_qty=25000, lead_time_days=10,
                 tiers=[(25000, 1.35), (75000, 1.18), (150000, 1.02)]),
        ],
    ),
    dict(
        name="AsepticTech Systems", location="Pune, Maharashtra",
        rating=4.9, reviews=198, fssai_verified=True, eco_friendly=True,
        lead_time_days=20,
        about="Aseptic carton systems and filling lines for dairy and beverage.",
        products=[
            dict(material_code="ASEPTIC-CARTON", title="6-Layer Aseptic Brick Carton",
                 structure="Paper / ALU7 / PE", thickness_um=380,
                 min_order_qty=50000, lead_time_days=20,
                 tiers=[(50000, 4.35), (200000, 3.88), (500000, 3.42)]),
        ],
    ),
    dict(
        name="Apex Liquid Pouches", location="Bengaluru, Karnataka",
        rating=4.7, reviews=110, fssai_verified=True, eco_friendly=False,
        lead_time_days=14,
        about="Spouted and stand-up pouches for liquids, purees and edible oil.",
        products=[
            dict(material_code="SPOUT-POUCH", title="Spouted Stand-Up Pouch",
                 structure="PET12 / ALU7 / NY15 / CPP80", thickness_um=120,
                 min_order_qty=15000, lead_time_days=14,
                 tiers=[(15000, 6.10), (60000, 5.35), (120000, 4.80)]),
            dict(material_code="PET-HOTFILL", title="Hot-Fill PET Bottle 500 ml",
                 structure="Heat-set PET", thickness_um=300,
                 min_order_qty=20000, lead_time_days=16,
                 tiers=[(20000, 8.40), (80000, 7.30), (200000, 6.55)]),
        ],
    ),
    dict(
        name="IndoRetort Packaging", location="Hyderabad, Telangana",
        rating=4.9, reviews=86, fssai_verified=True, eco_friendly=False,
        lead_time_days=18,
        about="Autoclave-rated retort laminates and trays for shelf-stable RTE.",
        products=[
            dict(material_code="RETORT-4PLY", title="4-Ply Retort Pouch",
                 structure="PET12 / ALU9 / OPA15 / RCPP70", thickness_um=110,
                 min_order_qty=20000, lead_time_days=18,
                 tiers=[(20000, 7.20), (75000, 6.35), (150000, 5.70)]),
            dict(material_code="ALU-FOIL", title="3-Ply Aluminium Foil Laminate",
                 structure="PET12 / ALU9 / PE50", thickness_um=71,
                 min_order_qty=15000, lead_time_days=15,
                 tiers=[(15000, 4.60), (60000, 4.05), (120000, 3.62)]),
        ],
    ),
    dict(
        name="GreenLeaf Sustainable Packaging", location="Coimbatore, Tamil Nadu",
        rating=4.6, reviews=73, fssai_verified=True, eco_friendly=True,
        lead_time_days=16,
        about="Compostable films and paper-based laminates. EPR registered.",
        products=[
            dict(material_code="PLA", title="PLA Compostable Film Pouch",
                 structure="PLA25 / PLA30", thickness_um=55,
                 min_order_qty=10000, lead_time_days=16,
                 tiers=[(10000, 3.45), (40000, 3.05), (100000, 2.78)]),
            dict(material_code="PAPER-PE", title="Kraft Paper / PE Laminate Bag",
                 structure="Kraft60 / PE30", thickness_um=90,
                 min_order_qty=10000, lead_time_days=12,
                 tiers=[(10000, 2.30), (50000, 2.02), (120000, 1.80)]),
        ],
    ),
    dict(
        name="FreshVent Produce Films", location="Nashik, Maharashtra",
        rating=4.5, reviews=54, fssai_verified=True, eco_friendly=True,
        lead_time_days=10,
        about="Laser micro-perforation and vented bags for fruit and vegetable "
              "export. Perforation tuned per commodity.",
        products=[
            dict(material_code="MICRO-BOPP", title="Micro-perforated BOPP Produce Film",
                 structure="BOPP30, laser perforated", thickness_um=30,
                 min_order_qty=20000, lead_time_days=10,
                 tiers=[(20000, 1.75), (80000, 1.52), (200000, 1.34)]),
            dict(material_code="MACRO-PE", title="Vented PE Produce Bag",
                 structure="LDPE35, macro perforated", thickness_um=35,
                 min_order_qty=25000, lead_time_days=8,
                 tiers=[(25000, 0.92), (100000, 0.80), (250000, 0.70)]),
        ],
    ),
    dict(
        name="PurePoly Containers", location="Ahmedabad, Gujarat",
        rating=4.4, reviews=97, fssai_verified=True, eco_friendly=False,
        lead_time_days=11,
        about="Blow-moulded HDPE and PET rigid containers for oils and condiments.",
        products=[
            dict(material_code="HDPE", title="HDPE Rigid Bottle 1 L",
                 structure="HDPE, 3-layer", thickness_um=450,
                 min_order_qty=10000, lead_time_days=11,
                 tiers=[(10000, 9.20), (50000, 8.10), (120000, 7.25)]),
            dict(material_code="LDPE", title="Mono-layer LDPE Pouch",
                 structure="LDPE50", thickness_um=50,
                 min_order_qty=30000, lead_time_days=7,
                 tiers=[(30000, 1.05), (100000, 0.92), (250000, 0.82)]),
        ],
    ),
    dict(
        name="CrystalGlass Packaging", location="Firozabad, Uttar Pradesh",
        rating=4.3, reviews=61, fssai_verified=True, eco_friendly=True,
        lead_time_days=22,
        about="Food-grade glass jars and bottles with lug and continuous-thread caps.",
        products=[
            dict(material_code="GLASS-JAR", title="Glass Jar 400 g with Lug Cap",
                 structure="Flint glass + lacquered steel lug cap", thickness_um=2000,
                 min_order_qty=5000, lead_time_days=22,
                 tiers=[(5000, 14.50), (25000, 12.80), (60000, 11.40)]),
        ],
    ),
]
