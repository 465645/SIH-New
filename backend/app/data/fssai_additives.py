"""FSSAI additive and preservative reference data.

Sources: FSS (Food Products Standards and Food Additives) Regulations 2011 and
its amendments, and the FSS (Prohibition and Restrictions on Sales) Regulations.

IMPORTANT: limits are category-dependent and are amended regularly. The figures
here are indicative and are meant to flag a likely problem for a human to verify
against the current gazette, not to certify a product as compliant. Every result
this module returns carries that caveat.

Limits are in ppm (mg/kg) of the final product unless stated otherwise.
"""

# Additives prohibited in food outright, or prohibited in the named use.
BANNED_SUBSTANCES = {
    "potassium bromate": dict(
        ins="924", aliases=["bromate", "kbro3", "e924"],
        reason="Banned as a flour treatment agent in India since June 2016 "
               "(possible carcinogen).",
        legal_basis="FSSAI notification, 2016"),
    "brominated vegetable oil": dict(
        ins="443", aliases=["bvo"],
        reason="Prohibited as a stabiliser in beverages.",
        legal_basis="FSS (Food Products Standards and Food Additives) Regulations"),
    "borax": dict(
        ins="285", aliases=["boric acid", "sodium borate", "suhaga"],
        reason="Not permitted in food. Cumulative toxin.",
        legal_basis="FSS (Prohibition and Restrictions on Sales) Regulations"),
    "calcium carbide": dict(
        ins=None, aliases=["carbide", "masala"],
        reason="Prohibited for artificial ripening of fruit. Releases arsenic and "
               "phosphorus impurities.",
        legal_basis="FSS (Prohibition and Restrictions on Sales) Regulations, 2011, "
                    "Regulation 2.3.5"),
    "sudan red": dict(
        ins=None, aliases=["sudan i", "sudan ii", "sudan iii", "sudan iv", "sudan dye"],
        reason="Non-permitted industrial dye. Genotoxic carcinogen.",
        legal_basis="Not in the permitted colour list"),
    "metanil yellow": dict(
        ins=None, aliases=["metanil"],
        reason="Non-permitted industrial dye, commonly adulterated into turmeric "
               "and besan.",
        legal_basis="Not in the permitted colour list"),
    "rhodamine b": dict(
        ins=None, aliases=["rhodamine"],
        reason="Non-permitted industrial dye.",
        legal_basis="Not in the permitted colour list"),
    "malachite green": dict(
        ins=None, aliases=[],
        reason="Non-permitted dye, found as an adulterant in green vegetables and "
               "as an antifungal in fish.",
        legal_basis="Not in the permitted colour list"),
    "melamine": dict(
        ins=None, aliases=[],
        reason="Adulterant used to inflate apparent protein content. Nephrotoxic.",
        legal_basis="Not a permitted food substance"),
    "argemone oil": dict(
        ins=None, aliases=["argemone", "katkar"],
        reason="Adulterant in mustard oil. Causes epidemic dropsy.",
        legal_basis="FSS (Prohibition and Restrictions on Sales) Regulations"),
}


# Permitted additives. `limits` maps an FSSAI category keyword to a ppm ceiling;
# `default_limit_ppm` applies when no specific category matches.
PERMITTED_ADDITIVES = {
    "sorbic acid": dict(
        ins="200", function="Preservative (antimicrobial)",
        aliases=["sorbate", "e200"],
        default_limit_ppm=1000,
        limits={"bakery": 1000, "dairy": 1000, "beverages": 300,
                "confectionery": 1500, "prepared foods": 1000},
        notes="Effective against yeasts and moulds below pH 6.5."),

    "potassium sorbate": dict(
        ins="202", function="Preservative (antimicrobial)",
        aliases=["e202"],
        default_limit_ppm=1000,
        limits={"bakery": 1000, "dairy": 1000, "beverages": 300,
                "confectionery": 1500, "fruits": 1000, "prepared foods": 1000},
        notes="Most common sorbate salt. Expressed as sorbic acid."),

    "benzoic acid": dict(
        ins="210", function="Preservative (antimicrobial)",
        aliases=["e210"],
        default_limit_ppm=600,
        limits={"beverages": 600, "fruits": 750, "salts": 750,
                "prepared foods": 600},
        notes="Only effective below pH 4.5. Not permitted in most dairy."),

    "sodium benzoate": dict(
        ins="211", function="Preservative (antimicrobial)",
        aliases=["e211"],
        default_limit_ppm=600,
        limits={"beverages": 600, "fruits": 750, "salts": 750,
                "prepared foods": 600},
        notes="With ascorbic acid (INS 300) in a beverage it can form trace "
              "benzene. Review the combination."),

    "sulphur dioxide": dict(
        ins="220", function="Preservative / antioxidant",
        aliases=["so2", "e220", "sulfur dioxide"],
        default_limit_ppm=350,
        limits={"fruits": 2000, "beverages": 350, "sweeteners": 70,
                "cereals": 150},
        notes="Allergen. Must be declared when above 10 ppm in the final product."),

    "sodium metabisulphite": dict(
        ins="223", function="Preservative / antioxidant",
        aliases=["e223", "metabisulfite", "sodium metabisulfite"],
        default_limit_ppm=350,
        limits={"fruits": 2000, "beverages": 350, "cereals": 150},
        notes="Declared as sulphites. Allergen labelling applies above 10 ppm."),

    "nisin": dict(
        ins="234", function="Preservative (bacteriocin)",
        aliases=["e234"],
        default_limit_ppm=12.5,
        limits={"dairy": 12.5, "prepared foods": 12.5},
        notes="Targets Gram-positive spore formers. Widely used in processed cheese."),

    "sodium nitrite": dict(
        ins="250", function="Preservative / colour fixative",
        aliases=["e250", "nitrite"],
        default_limit_ppm=150,
        limits={"meat": 150, "prepared foods": 150},
        notes="Cured meat only. Forms nitrosamines at high heat - keep to the "
              "minimum that achieves the antimicrobial effect."),

    "sodium propionate": dict(
        ins="281", function="Preservative (antifungal)",
        aliases=["e281", "propionate"],
        default_limit_ppm=2000,
        limits={"bakery": 2000, "dairy": 3000},
        notes="The standard mould inhibitor in bread."),

    "calcium propionate": dict(
        ins="282", function="Preservative (antifungal)",
        aliases=["e282"],
        default_limit_ppm=2000,
        limits={"bakery": 2000},
        notes="Bread and baked goods. Does not inhibit yeast."),

    "ascorbic acid": dict(
        ins="300", function="Antioxidant",
        aliases=["e300", "vitamin c"],
        default_limit_ppm=None,
        limits={},
        notes="GMP level - no numerical ceiling. Watch the benzoate combination "
              "in beverages."),

    "bha": dict(
        ins="320", function="Antioxidant",
        aliases=["butylated hydroxyanisole", "e320"],
        default_limit_ppm=200,
        limits={"fats and oils": 200, "ready-to-eat savouries": 200},
        notes="Calculated on the fat content, not the whole product."),

    "bht": dict(
        ins="321", function="Antioxidant",
        aliases=["butylated hydroxytoluene", "e321"],
        default_limit_ppm=200,
        limits={"fats and oils": 200, "ready-to-eat savouries": 200},
        notes="Calculated on the fat content. Often paired with BHA."),

    "tbhq": dict(
        ins="319", function="Antioxidant",
        aliases=["tertiary butylhydroquinone", "e319"],
        default_limit_ppm=200,
        limits={"fats and oils": 200, "ready-to-eat savouries": 200},
        notes="Most effective antioxidant for frying oils. On fat basis."),

    "citric acid": dict(
        ins="330", function="Acidity regulator",
        aliases=["e330"],
        default_limit_ppm=None, limits={},
        notes="GMP level."),

    "monosodium glutamate": dict(
        ins="621", function="Flavour enhancer",
        aliases=["msg", "e621", "aji-no-moto"],
        default_limit_ppm=None,
        limits={},
        notes="GMP level, but must be declared on the label and is not permitted "
              "in foods for infants below 12 months."),

    "aspartame": dict(
        ins="951", function="Sweetener",
        aliases=["e951"],
        default_limit_ppm=700,
        limits={"beverages": 700, "confectionery": 1000},
        notes="Mandatory declaration: 'Contains a source of phenylalanine'. "
              "Not permitted in foods for infants and young children."),

    "sucralose": dict(
        ins="955", function="Sweetener",
        aliases=["e955"],
        default_limit_ppm=300,
        limits={"beverages": 300, "confectionery": 1500, "dairy": 400},
        notes="Heat stable, suitable for baked applications."),

    "saccharin": dict(
        ins="954", function="Sweetener",
        aliases=["e954", "sodium saccharin"],
        default_limit_ppm=100,
        limits={"beverages": 100, "confectionery": 500},
        notes="Not permitted in foods for infants and young children."),

    "tartrazine": dict(
        ins="102", function="Colour",
        aliases=["e102", "yellow 5"],
        default_limit_ppm=100,
        limits={"beverages": 100, "confectionery": 100, "bakery": 100},
        notes="Permitted synthetic colour. Total synthetic colour in a food must "
              "not exceed 100 ppm."),

    "sunset yellow": dict(
        ins="110", function="Colour",
        aliases=["e110", "sunset yellow fcf"],
        default_limit_ppm=100,
        limits={"beverages": 100, "confectionery": 100},
        notes="Counts toward the 100 ppm combined synthetic colour ceiling."),
}


# Additives that should not appear together, with the reason.
INTERACTION_WARNINGS = [
    (("sodium benzoate", "ascorbic acid"),
     "Benzoate with ascorbic acid in an acidic beverage can form trace benzene, "
     "especially with heat or light exposure. Substitute sorbate, or remove the "
     "added ascorbic acid."),
    (("benzoic acid", "ascorbic acid"),
     "Same benzene formation risk as the sodium salt."),
    (("sodium nitrite", "ascorbic acid"),
     "Not a hazard - ascorbate is in fact added deliberately to suppress "
     "nitrosamine formation. No action needed."),
]


# Additives not permitted in food for infants and young children (below 24 months).
INFANT_PROHIBITED = [
    "monosodium glutamate", "aspartame", "saccharin", "sucralose",
    "tartrazine", "sunset yellow", "sodium benzoate", "benzoic acid",
]
