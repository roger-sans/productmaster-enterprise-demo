"""Original fictional taxonomy and metadata for the public ProductMaster demo.

All category names and catalog records below are synthetic examples. This file
intentionally contains no identifiers, mappings or documentation from an employer.
"""
from __future__ import annotations
import random
import re
from uuid import uuid5, NAMESPACE_URL

# Family -> Subfamily -> Type. None denotes a legitimate terminal subfamily.
# Hierarchy uses a generic paint/decorating assortment, with independently
# written category names, technical codes and product specifications.
TREE = {
 "Paint Brushes": {
  "Flat Brushes": ["Classic Wood", "Ergonomic Grip", "Precision Edge", "Synthetic Handle"],
  "Round Brushes": ["Natural Bristle", "Synthetic Bristle", "Mixed Bristle"],
  "Detail Brushes": ["Fine Tip", "Artist Detail", "Angled Tip"],
  "Specialty Brushes": ["Radiator", "Corner", "Stencil"],
  "Brush Sets": ["Starter Set", "Professional Set"],
 },
 "Paint Rollers": {
  "Roller Frames": ["Standard Frame", "Heavy-Duty Frame", "Quick Release"],
  "Roller Covers": ["Microfiber", "Foam", "Woven Fabric", "High Pile"],
  "Roller Kits": ["Interior Kit", "Exterior Kit", "Specialty Kit"],
  "Corner Rollers": None,
  "Roller Accessories": ["End Cap", "Sleeve Adapter"],
 },
 "Mini Rollers": {
  "Mini Roller Kits": ["Short Handle", "Long Handle", "Twin Pack"],
  "Mini Covers": ["Foam", "Microfiber", "Flocked"],
  "Midi Covers": ["Fine Finish", "General Purpose"],
  "Midi Roller Kits": ["Fixed Frame", "Replaceable Sleeve"],
  "Mini Frames": None,
 },
 "Painting Accessories": {
  "Paint Trays": ["Shallow", "Deep Well", "Disposable Insert"],
  "Paint Grids": ["Metal", "Polymer"],
  "Mixing Tools": ["Hand Mixer", "Drill Attachment"],
  "Paint Containers": ["Bucket", "Liner", "Measuring Cup"],
  "Other Applicators": None,
 },
 "Extension Poles": {
  "Telescopic Poles": ["Two Section", "Three Section"],
  "Fixed Poles": ["Aluminium", "Composite"],
  "Pole Connectors": ["Threaded", "Universal", "Quick Lock"],
  "Pole Accessories": None,
 },
 "Surface Protection": {
  "Floor Protection": ["Paper", "Non-Woven", "Plastic Film"],
  "Masking Film": ["Pre-Taped", "Standard Film"],
  "Protective Sheets": ["Canvas", "Polyethylene", "Absorbent"],
  "Door Protection": None,
  "Edge Protection": ["Flexible", "Rigid"],
 },
 "Adhesive Tapes": {
  "Masking Tape": ["Crepe", "Washi", "Low Tack", "Outdoor"],
  "Packaging Tape": ["Clear", "Brown", "Reinforced"],
  "Double Sided Tape": ["Foam", "Film"],
  "Specialist Tape": ["Anti-Slip", "Marking", "Repair"],
 },
 "Scrapers & Trowels": {
  "Filling Knives": ["Rigid Blade", "Flexible Blade"],
  "Scrapers": ["Safety Scraper", "Long Handle", "Heavy Duty"],
  "Finishing Trowels": ["Stainless", "Carbon Steel"],
  "Notched Trowels": ["Fine Notch", "Wide Notch"],
  "Blade Accessories": None,
 },
 "Cleaning Supplies": {
  "Brush Cleaners": ["Liquid Cleaner", "Solid Cleaner"],
  "Cleaning Cloths": ["Microfiber", "Cotton", "Industrial Wipe"],
  "Sponges": ["Cellulose", "Abrasive"],
  "Waste Collection": None,
 },
 "Coatings & Sprays": {
  "Colour Sprays": ["Standard Colour", "Metallic Finish"],
  "Technical Sprays": ["Primer", "Protective Coat", "Lubricant"],
  "Marking Sprays": ["Temporary", "Permanent"],
  "Surface Treatments": None,
 },
 "Safety Gear": {
  "Work Gloves": ["Disposable", "Cut Resistant", "Coated"],
  "Eye Protection": ["Clear Lens", "Tinted Lens"],
  "Respiratory Protection": ["Particle Mask", "Reusable Half Mask"],
  "Protective Clothing": None,
 },
 "Decorating Accessories": {
  "Wallpaper Tools": ["Smoother", "Seam Roller", "Trimmer"],
  "Cutting Tools": ["Utility Knife", "Precision Cutter"],
  "Abrasives": ["Sanding Block", "Sheet", "Disc"],
  "Caulking Tools": ["Cartridge Gun", "Finishing Tool"],
  "Decorative Tools": None,
 },
 "Retail Displays": {
  "Counter Displays": ["Compact", "Modular"],
  "Floor Displays": ["Freestanding", "Wall Mounted"],
  "Printed Materials": None,
  "Promotional Kits": None,
 }
}

# code, label, type, unit, options, family keywords, required at applicable level
SPECS = [
 ("working_width", "Working width", "decimal", "mm", [], ["Rollers", "Brushes", "Tapes", "Protection", "Trowels"], True),
 ("working_length", "Working length", "decimal", "mm", [], ["Rollers", "Brushes", "Trowels", "Poles"], False),
 ("diameter", "Nominal diameter", "decimal", "mm", [], ["Rollers", "Poles"], False),
 ("pile_height", "Fabric pile height", "decimal", "mm", [], ["Rollers"], False),
 ("bristle_material", "Bristle fibre", "option", None, ["Synthetic", "Natural", "Mixed"], ["Brushes"], True),
 ("bristle_density", "Bristle density", "option", None, ["Soft", "Medium", "Firm"], ["Brushes"], False),
 ("handle_material", "Handle material", "option", None, ["Wood", "Polymer", "Bi-material", "Metal"], ["Brushes", "Rollers", "Trowels"], False),
 ("cover_material", "Cover material", "option", None, ["Foam", "Microfiber", "Polyamide", "Woven", "Flocked"], ["Rollers"], True),
 ("surface_finish", "Surface finish", "option", None, ["Smooth", "Textured", "Satin", "Matte"], ["Rollers", "Sprays", "Trowels"], False),
 ("pack_units", "Units per pack", "integer", "unit", [], ["Rollers", "Brushes", "Tapes", "Safety"], False),
 ("blade_thickness", "Blade thickness", "decimal", "mm", [], ["Trowels"], False),
 ("blade_material", "Blade material", "option", None, ["Stainless Steel", "Carbon Steel", "Polymer"], ["Trowels"], True),
 ("total_extension", "Maximum extension", "decimal", "cm", [], ["Poles"], True),
 ("connector_type", "Connector standard", "option", None, ["Threaded", "Quick Lock", "Universal"], ["Poles"], False),
 ("film_thickness", "Film thickness", "decimal", "micron", [], ["Protection"], False),
 ("roll_length", "Length per roll", "decimal", "m", [], ["Protection", "Tapes"], True),
 ("adhesive_type", "Adhesive type", "option", None, ["Acrylic", "Rubber", "Solvent-free"], ["Tapes"], True),
 ("adhesion_level", "Adhesion level", "option", None, ["Low", "Medium", "High"], ["Tapes"], False),
 ("colour_family", "Colour family", "option", None, ["Neutral", "White", "Black", "Warm", "Cool"], ["Sprays", "Accessories"], False),
 ("volume_ml", "Volume", "integer", "ml", [], ["Sprays", "Cleaning"], False),
 ("material_composition", "Main composition", "option", None, ["Cotton", "Microfiber", "Polymer", "Metal", "Wood"], ["Cleaning", "Safety", "Accessories"], False),
 ("protection_class", "Protection class", "option", None, ["General", "Light Duty", "Industrial"], ["Safety"], True),
 ("size_designation", "Size designation", "string", None, [], ["Safety", "Brushes"], False),
 ("display_capacity", "Display capacity", "integer", "units", [], ["Displays"], True),
 ("recyclable_packaging", "Recyclable packaging", "boolean", None, [], ["Rollers", "Brushes", "Protection", "Tapes", "Safety", "Sprays", "Displays", "Accessories", "Cleaning", "Poles", "Trowels"], False),
]

BRANDS = ["Aster", "Noma", "Vale", "Kora", "Westline", "Orion", "Aero", "Haven"]
RANGES = ["Core", "Trade", "Studio", "Pro", "Eco"]
SECTORS = ["Professional", "Retail", "Industrial"]
LIFECYCLES = ["Active", "Launch", "Phase-out"]
ROLES = ["Core range", "Seasonal", "Strategic", "Accessory"]
SOURCE_SYSTEMS = ["Core ERP", "Warehouse Hub", "Supplier Feed"]


def slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


def create_nodes():
    """Build stable parent-linked identities, with no fixed-depth db constraint."""
    nodes = []
    for fi, (family, subs) in enumerate(TREE.items()):
        fcode = slug(family)
        fid = str(uuid5(NAMESPACE_URL, f"synthetic.master.node.{fcode}"))
        nodes.append({"id":fid,"parent_id":None,"code":fcode,"label":family,"level":1,"position":fi+1})
        for si, (sub, types) in enumerate(subs.items()):
            scode = f"{fcode}__{slug(sub)}"
            sid = str(uuid5(NAMESPACE_URL, f"synthetic.master.node.{scode}"))
            nodes.append({"id":sid,"parent_id":fid,"code":scode,"label":sub,"level":2,"position":si+1})
            for ti, typ in enumerate(types or []):
                tcode = f"{scode}__{slug(typ)}"
                tid = str(uuid5(NAMESPACE_URL, f"synthetic.master.node.{tcode}"))
                nodes.append({"id":tid,"parent_id":sid,"code":tcode,"label":typ,"level":3,"position":ti+1})
    return nodes


def applicable_specs(family: str):
    return [s for s in SPECS if any(k.lower() in family.lower() for k in s[5])]


def sample_attr(code: str, data_type: str, options: list[str], n: int):
    rng = random.Random(17 + n * 97 + sum(map(ord, code)))
    if data_type == 'option': return options[n % len(options)]
    if data_type == 'boolean': return n % 4 != 0
    if data_type == 'string': return ['S', 'M', 'L', 'XL', '00', '1.5'][n % 6]
    if data_type == 'integer':
        if code == 'volume_ml': return [250, 400, 500, 750][n % 4]
        if code == 'display_capacity': return [12, 24, 36, 48][n % 4]
        return [1, 2, 4, 5, 10][n % 5]
    ranges = {
        'working_width':[25,35,50,75,100,150,180,230,250],
        'working_length':[75,100,180,230,300], 'diameter':[6,8,12,18,28,40],
        'pile_height':[4,6,9,12,18], 'blade_thickness':[0.5,0.7,1,1.2],
        'total_extension':[120,180,240,300], 'film_thickness':[10,20,40,60],
        'roll_length':[10,20,25,50,100]
    }
    return (ranges.get(code) or [1,2,3])[rng.randrange(len(ranges.get(code) or [1,2,3]))]


def fake_products(nodes, count=640):
    byid = {n['id']:n for n in nodes}
    leaves = [n for n in nodes if not any(x['parent_id'] == n['id'] for x in nodes)]
    out=[]
    for i in range(count):
        leaf=leaves[(i*37+3)%len(leaves)]
        path=[]; node=leaf
        while node:
            path.insert(0,node); node=byid.get(node['parent_id'])
        family=path[0]['label']; specs=applicable_specs(family)
        attrs={s[0]:sample_attr(s[0],s[2],s[4],i) for s in specs if s[6] or (i+len(s[0]))%5!=0}
        # No fictional values for inapplicable technical concepts.
        sku=f"PRD{i+1:09d}"
        out.append({
            'sku':sku, 'description':f"{BRANDS[i%len(BRANDS)]} {leaf['label']} {family[:-1] if family.endswith('s') else family} {i%7+1}",
            'classification_node_id':leaf['id'], 'brand':BRANDS[i%len(BRANDS)],
            'range_name':RANGES[(i//3)%len(RANGES)],'sector':SECTORS[(i//11)%len(SECTORS)],
            'lifecycle':LIFECYCLES[(i//23)%len(LIFECYCLES)],'business_role':ROLES[(i//13)%len(ROLES)],
            'source_system':SOURCE_SYSTEMS[(i//19)%len(SOURCE_SYSTEMS)],
            'attributes':attrs,'status':'accepted', 'version':1,
        })
    return out
