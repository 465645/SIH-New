"""Packaging material reference catalogue.

Barrier figures are indicative industry typical values for the stated reference
thickness, measured under the conventional test conditions:
    OTR  - cc / m2 / day  at 23 C, 0% RH   (ASTM D3985)
    WVTR - g  / m2 / day  at 38 C, 90% RH  (ASTM F1249)

Real films vary by supplier, grade and coating; these figures are used to size a
specification, which the vendor then confirms against their own datasheet.
"""

MATERIALS = [
    # ------------- Mono-layer flexibles: low barrier, low cost, recyclable -------------
    dict(code="LDPE", name="Mono-layer LDPE Pouch", family="Flexible",
         otr=7800, wvtr=18, ref_thickness_um=50,
         thickness_min_um=30, thickness_max_um=200, tensile_strength_mpa=12,
         max_fill_temp_c=60, min_service_temp_c=-50, sealability="Heat seal",
         is_breathable=False, map_suitable=False, liquid_suitable=True, retort_safe=False,
         cost_per_m2=11.0, recyclable=True, compostable=False, epr_score=90,
         notes="Cheapest food-contact film. Poor oxygen barrier - short shelf life only."),

    dict(code="HDPE", name="HDPE Film / Rigid Bottle", family="Rigid",
         otr=2200, wvtr=6, ref_thickness_um=50,
         thickness_min_um=40, thickness_max_um=500, tensile_strength_mpa=28,
         max_fill_temp_c=80, min_service_temp_c=-40, sealability="Induction",
         is_breathable=False, map_suitable=False, liquid_suitable=True, retort_safe=False,
         cost_per_m2=16.0, recyclable=True, compostable=False, epr_score=85,
         notes="Good moisture barrier and stiffness. Standard for edible oils."),

    dict(code="BOPP", name="Mono-layer BOPP Film", family="Flexible",
         otr=2400, wvtr=6.5, ref_thickness_um=20,
         thickness_min_um=15, thickness_max_um=60, tensile_strength_mpa=140,
         max_fill_temp_c=70, min_service_temp_c=-30, sealability="Heat seal",
         is_breathable=False, map_suitable=False, liquid_suitable=False, retort_safe=False,
         cost_per_m2=13.0, recyclable=True, compostable=False, epr_score=80,
         notes="Clear, stiff, good print surface. Moderate moisture barrier."),

    dict(code="PET", name="PET Film / Bottle", family="Rigid",
         otr=120, wvtr=45, ref_thickness_um=12,
         thickness_min_um=12, thickness_max_um=350, tensile_strength_mpa=180,
         max_fill_temp_c=70, min_service_temp_c=-40, sealability="Heat seal",
         is_breathable=False, map_suitable=True, liquid_suitable=True, retort_safe=False,
         cost_per_m2=19.0, recyclable=True, compostable=False, epr_score=88,
         notes="Good O2 barrier, weak moisture barrier. Widely recycled (rPET stream)."),

    dict(code="PET-HOTFILL", name="Hot-Fill PET Bottle", family="Rigid",
         otr=110, wvtr=42, ref_thickness_um=300,
         thickness_min_um=250, thickness_max_um=400, tensile_strength_mpa=180,
         max_fill_temp_c=92, min_service_temp_c=-20, sealability="Induction",
         is_breathable=False, map_suitable=False, liquid_suitable=True, retort_safe=False,
         cost_per_m2=24.0, recyclable=True, compostable=False, epr_score=86,
         notes="Heat-set crystallised neck withstands 85-92 C fill for juices and RTD."),

    # ------------------------------ Mid barrier ------------------------------
    dict(code="PA-NYLON", name="Nylon (PA) / PE Laminate", family="Flexible",
         otr=45, wvtr=170, ref_thickness_um=15,
         thickness_min_um=15, thickness_max_um=100, tensile_strength_mpa=75,
         max_fill_temp_c=95, min_service_temp_c=-60, sealability="Heat seal",
         is_breathable=False, map_suitable=True, liquid_suitable=True, retort_safe=False,
         cost_per_m2=27.0, recyclable=False, compostable=False, epr_score=40,
         notes="Excellent puncture resistance and O2 barrier, poor moisture barrier. "
               "Standard for vacuum and MAP meat and cheese."),

    dict(code="PVDC-BOPP", name="PVDC-Coated BOPP Film", family="Flexible",
         otr=9, wvtr=3.0, ref_thickness_um=25,
         thickness_min_um=20, thickness_max_um=60, tensile_strength_mpa=130,
         max_fill_temp_c=80, min_service_temp_c=-30, sealability="Heat seal",
         is_breathable=False, map_suitable=True, liquid_suitable=False, retort_safe=False,
         cost_per_m2=29.0, recyclable=False, compostable=False, epr_score=35,
         notes="Good dual barrier while staying transparent. Chlorine content hurts EPR."),

    dict(code="EVOH", name="EVOH Co-extruded Barrier Film", family="Flexible",
         otr=0.6, wvtr=22, ref_thickness_um=15,
         thickness_min_um=15, thickness_max_um=120, tensile_strength_mpa=80,
         max_fill_temp_c=95, min_service_temp_c=-40, sealability="Heat seal",
         is_breathable=False, map_suitable=True, liquid_suitable=True, retort_safe=False,
         cost_per_m2=34.0, recyclable=False, compostable=False, epr_score=45,
         notes="Outstanding O2 barrier but humidity-sensitive - must sit between PE layers."),

    # -------------------------- High / ultra-high barrier --------------------------
    dict(code="MET-PET", name="Metallized PET / PE Pouch", family="Flexible",
         otr=1.2, wvtr=0.7, ref_thickness_um=12,
         thickness_min_um=40, thickness_max_um=120, tensile_strength_mpa=150,
         max_fill_temp_c=85, min_service_temp_c=-40, sealability="Heat seal",
         is_breathable=False, map_suitable=True, liquid_suitable=False, retort_safe=False,
         cost_per_m2=31.0, recyclable=False, compostable=False, epr_score=45,
         notes="Workhorse high-barrier snack laminate. Opaque, so it also blocks "
               "light-driven oxidation."),

    dict(code="ALU-FOIL", name="3-Ply Aluminium Foil Laminate", family="Flexible",
         otr=0.05, wvtr=0.05, ref_thickness_um=9,
         thickness_min_um=60, thickness_max_um=150, tensile_strength_mpa=110,
         max_fill_temp_c=121, min_service_temp_c=-60, sealability="Heat seal",
         is_breathable=False, map_suitable=True, liquid_suitable=True, retort_safe=True,
         cost_per_m2=44.0, recyclable=False, compostable=False, epr_score=30,
         notes="Near-absolute barrier. Multi-material laminate is hard to recycle."),

    dict(code="RETORT-4PLY", name="4-Ply Retort Pouch (PET/ALU/OPA/CPP)", family="Flexible",
         otr=0.03, wvtr=0.04, ref_thickness_um=110,
         thickness_min_um=90, thickness_max_um=150, tensile_strength_mpa=120,
         max_fill_temp_c=135, min_service_temp_c=-40, sealability="Heat seal",
         is_breathable=False, map_suitable=False, liquid_suitable=True, retort_safe=True,
         cost_per_m2=58.0, recyclable=False, compostable=False, epr_score=28,
         notes="Survives 121 C autoclave sterilisation. For shelf-stable RTE curries."),

    dict(code="ASEPTIC-CARTON", name="6-Layer Aseptic Brick Carton", family="Paper-based",
         otr=0.08, wvtr=0.09, ref_thickness_um=380,
         thickness_min_um=350, thickness_max_um=450, tensile_strength_mpa=60,
         max_fill_temp_c=30, min_service_temp_c=-10, sealability="Heat seal",
         is_breathable=False, map_suitable=False, liquid_suitable=True, retort_safe=False,
         cost_per_m2=38.0, recyclable=False, compostable=False, epr_score=60,
         notes="Paper/Alu/PE. Ambient-stable liquids for 6-12 months after UHT cold fill."),

    dict(code="SPOUT-POUCH", name="Spouted Stand-Up Pouch (PET/ALU/PA/CPP)", family="Flexible",
         otr=0.06, wvtr=0.06, ref_thickness_um=120,
         thickness_min_um=100, thickness_max_um=160, tensile_strength_mpa=115,
         max_fill_temp_c=90, min_service_temp_c=-20, sealability="Heat seal",
         is_breathable=False, map_suitable=False, liquid_suitable=True, retort_safe=False,
         cost_per_m2=52.0, recyclable=False, compostable=False, epr_score=32,
         notes="High-barrier liquid pouch with a resealable spout. Hot fill to 85 C."),

    dict(code="GLASS-JAR", name="Glass Jar with Lug Cap", family="Rigid",
         otr=0.0, wvtr=0.0, ref_thickness_um=2000,
         thickness_min_um=1500, thickness_max_um=4000, tensile_strength_mpa=50,
         max_fill_temp_c=135, min_service_temp_c=-20, sealability="Induction",
         is_breathable=False, map_suitable=True, liquid_suitable=True, retort_safe=True,
         cost_per_m2=95.0, recyclable=True, compostable=False, epr_score=95,
         notes="Absolute barrier and infinitely recyclable, but heavy and fragile."),

    # -------------------------- Breathable / fresh produce --------------------------
    dict(code="MICRO-BOPP", name="Micro-perforated BOPP Film", family="Breathable",
         otr=120000, wvtr=65, ref_thickness_um=30,
         thickness_min_um=20, thickness_max_um=50, tensile_strength_mpa=130,
         max_fill_temp_c=40, min_service_temp_c=-5, sealability="Heat seal",
         is_breathable=True, map_suitable=True, liquid_suitable=False, retort_safe=False,
         cost_per_m2=17.0, recyclable=True, compostable=False, epr_score=75,
         notes="Laser micro-perforations tuned to respiration rate, for equilibrium MAP "
               "of fresh fruit and vegetables."),

    dict(code="MACRO-PE", name="Macro-perforated PE Bag", family="Breathable",
         otr=900000, wvtr=140, ref_thickness_um=35,
         thickness_min_um=25, thickness_max_um=60, tensile_strength_mpa=11,
         max_fill_temp_c=40, min_service_temp_c=-5, sealability="Heat seal",
         is_breathable=True, map_suitable=False, liquid_suitable=False, retort_safe=False,
         cost_per_m2=9.0, recyclable=True, compostable=False, epr_score=85,
         notes="Vented bag for very high respiration produce such as leafy greens and "
               "mushrooms. No atmosphere control, condensation management only."),

    # ----------------------------- Sustainable alternatives -----------------------------
    dict(code="PLA", name="PLA Compostable Film", family="Flexible",
         otr=700, wvtr=210, ref_thickness_um=25,
         thickness_min_um=20, thickness_max_um=60, tensile_strength_mpa=55,
         max_fill_temp_c=45, min_service_temp_c=-10, sealability="Heat seal",
         is_breathable=False, map_suitable=False, liquid_suitable=False, retort_safe=False,
         cost_per_m2=33.0, recyclable=False, compostable=True, epr_score=92,
         notes="Industrially compostable. Weak barrier and low heat tolerance, so "
               "short shelf life ambient dry goods only."),

    dict(code="PAPER-PE", name="Kraft Paper / PE Laminate", family="Paper-based",
         otr=1800, wvtr=14, ref_thickness_um=80,
         thickness_min_um=60, thickness_max_um=160, tensile_strength_mpa=35,
         max_fill_temp_c=60, min_service_temp_c=-20, sealability="Heat seal",
         is_breathable=False, map_suitable=False, liquid_suitable=False, retort_safe=False,
         cost_per_m2=21.0, recyclable=True, compostable=False, epr_score=78,
         notes="Paper look with a moisture-barrier liner. Good for flour, sugar and tea."),
]
