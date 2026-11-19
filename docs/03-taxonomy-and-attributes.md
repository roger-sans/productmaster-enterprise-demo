# Complete synthetic taxonomy and technical attribute dictionary

This is a **newly authored fictional business classification**, expressed in English. It is not an export of any enterprise taxonomy. The database stores stable immutable node identifiers and parent links; business users navigate `Family → Subfamily → Type`.

## Hierarchy rules

- A **Family** is level 1; a **Subfamily** is level 2; a **Type** is level 3.
- A subfamily with **no** approved Type children is itself terminal. It is not assigned a fictional `Other` type.
- A subfamily **with** types is a container; accepted product classifications must reference a leaf Type.
- Identical labels (for example `Foam`) may appear under different parent nodes without identity collision.
- Stable machine codes and UUIDs, not labels, are used for references and lineage.
- A category change is subject to an attributable, independently reviewed change request.

## Entire hierarchy (all 192 nodes)

### Paint Brushes

- **Flat Brushes**
  - Classic Wood
  - Ergonomic Grip
  - Precision Edge
  - Synthetic Handle
- **Round Brushes**
  - Natural Bristle
  - Synthetic Bristle
  - Mixed Bristle
- **Detail Brushes**
  - Fine Tip
  - Artist Detail
  - Angled Tip
- **Specialty Brushes**
  - Radiator
  - Corner
  - Stencil
- **Brush Sets**
  - Starter Set
  - Professional Set

### Paint Rollers

- **Roller Frames**
  - Standard Frame
  - Heavy-Duty Frame
  - Quick Release
- **Roller Covers**
  - Microfiber
  - Foam
  - Woven Fabric
  - High Pile
- **Roller Kits**
  - Interior Kit
  - Exterior Kit
  - Specialty Kit
- **Corner Rollers** — *terminal subfamily*
- **Roller Accessories**
  - End Cap
  - Sleeve Adapter

### Mini Rollers

- **Mini Roller Kits**
  - Short Handle
  - Long Handle
  - Twin Pack
- **Mini Covers**
  - Foam
  - Microfiber
  - Flocked
- **Midi Covers**
  - Fine Finish
  - General Purpose
- **Midi Roller Kits**
  - Fixed Frame
  - Replaceable Sleeve
- **Mini Frames** — *terminal subfamily*

### Painting Accessories

- **Paint Trays**
  - Shallow
  - Deep Well
  - Disposable Insert
- **Paint Grids**
  - Metal
  - Polymer
- **Mixing Tools**
  - Hand Mixer
  - Drill Attachment
- **Paint Containers**
  - Bucket
  - Liner
  - Measuring Cup
- **Other Applicators** — *terminal subfamily*

### Extension Poles

- **Telescopic Poles**
  - Two Section
  - Three Section
- **Fixed Poles**
  - Aluminium
  - Composite
- **Pole Connectors**
  - Threaded
  - Universal
  - Quick Lock
- **Pole Accessories** — *terminal subfamily*

### Surface Protection

- **Floor Protection**
  - Paper
  - Non-Woven
  - Plastic Film
- **Masking Film**
  - Pre-Taped
  - Standard Film
- **Protective Sheets**
  - Canvas
  - Polyethylene
  - Absorbent
- **Door Protection** — *terminal subfamily*
- **Edge Protection**
  - Flexible
  - Rigid

### Adhesive Tapes

- **Masking Tape**
  - Crepe
  - Washi
  - Low Tack
  - Outdoor
- **Packaging Tape**
  - Clear
  - Brown
  - Reinforced
- **Double Sided Tape**
  - Foam
  - Film
- **Specialist Tape**
  - Anti-Slip
  - Marking
  - Repair

### Scrapers & Trowels

- **Filling Knives**
  - Rigid Blade
  - Flexible Blade
- **Scrapers**
  - Safety Scraper
  - Long Handle
  - Heavy Duty
- **Finishing Trowels**
  - Stainless
  - Carbon Steel
- **Notched Trowels**
  - Fine Notch
  - Wide Notch
- **Blade Accessories** — *terminal subfamily*

### Cleaning Supplies

- **Brush Cleaners**
  - Liquid Cleaner
  - Solid Cleaner
- **Cleaning Cloths**
  - Microfiber
  - Cotton
  - Industrial Wipe
- **Sponges**
  - Cellulose
  - Abrasive
- **Waste Collection** — *terminal subfamily*

### Coatings & Sprays

- **Colour Sprays**
  - Standard Colour
  - Metallic Finish
- **Technical Sprays**
  - Primer
  - Protective Coat
  - Lubricant
- **Marking Sprays**
  - Temporary
  - Permanent
- **Surface Treatments** — *terminal subfamily*

### Safety Gear

- **Work Gloves**
  - Disposable
  - Cut Resistant
  - Coated
- **Eye Protection**
  - Clear Lens
  - Tinted Lens
- **Respiratory Protection**
  - Particle Mask
  - Reusable Half Mask
- **Protective Clothing** — *terminal subfamily*

### Decorating Accessories

- **Wallpaper Tools**
  - Smoother
  - Seam Roller
  - Trimmer
- **Cutting Tools**
  - Utility Knife
  - Precision Cutter
- **Abrasives**
  - Sanding Block
  - Sheet
  - Disc
- **Caulking Tools**
  - Cartridge Gun
  - Finishing Tool
- **Decorative Tools** — *terminal subfamily*

### Retail Displays

- **Counter Displays**
  - Compact
  - Modular
- **Floor Displays**
  - Freestanding
  - Wall Mounted
- **Printed Materials** — *terminal subfamily*
- **Promotional Kits** — *terminal subfamily*

## Technical attribute definitions (25 total)

Each definition has a stable technical code, a business label, a data type, optional unit, optional controlled vocabulary and family-level applicability. Requiredness is **scoped to applicable families**, not globally true for all products.

| Code | Display label | Data type | Unit | Required | Example controlled options | Applies to family names containing |
|---|---|---|---|---|---|---|
| `working_width` | Working width | decimal | mm | Yes | — | Rollers, Brushes, Tapes, Protection, Trowels |
| `working_length` | Working length | decimal | mm | No | — | Rollers, Brushes, Trowels, Poles |
| `diameter` | Nominal diameter | decimal | mm | No | — | Rollers, Poles |
| `pile_height` | Fabric pile height | decimal | mm | No | — | Rollers |
| `bristle_material` | Bristle fibre | option | — | Yes | Synthetic, Natural, Mixed | Brushes |
| `bristle_density` | Bristle density | option | — | No | Soft, Medium, Firm | Brushes |
| `handle_material` | Handle material | option | — | No | Wood, Polymer, Bi-material, Metal | Brushes, Rollers, Trowels |
| `cover_material` | Cover material | option | — | Yes | Foam, Microfiber, Polyamide, Woven, Flocked | Rollers |
| `surface_finish` | Surface finish | option | — | No | Smooth, Textured, Satin, Matte | Rollers, Sprays, Trowels |
| `pack_units` | Units per pack | integer | unit | No | — | Rollers, Brushes, Tapes, Safety |
| `blade_thickness` | Blade thickness | decimal | mm | No | — | Trowels |
| `blade_material` | Blade material | option | — | Yes | Stainless Steel, Carbon Steel, Polymer | Trowels |
| `total_extension` | Maximum extension | decimal | cm | Yes | — | Poles |
| `connector_type` | Connector standard | option | — | No | Threaded, Quick Lock, Universal | Poles |
| `film_thickness` | Film thickness | decimal | micron | No | — | Protection |
| `roll_length` | Length per roll | decimal | m | Yes | — | Protection, Tapes |
| `adhesive_type` | Adhesive type | option | — | Yes | Acrylic, Rubber, Solvent-free | Tapes |
| `adhesion_level` | Adhesion level | option | — | No | Low, Medium, High | Tapes |
| `colour_family` | Colour family | option | — | No | Neutral, White, Black, Warm, Cool | Sprays, Accessories |
| `volume_ml` | Volume | integer | ml | No | — | Sprays, Cleaning |
| `material_composition` | Main composition | option | — | No | Cotton, Microfiber, Polymer, Metal, Wood | Cleaning, Safety, Accessories |
| `protection_class` | Protection class | option | — | Yes | General, Light Duty, Industrial | Safety |
| `size_designation` | Size designation | string | — | No | — | Safety, Brushes |
| `display_capacity` | Display capacity | integer | units | Yes | — | Displays |
| `recyclable_packaging` | Recyclable packaging | boolean | — | No | — | Rollers, Brushes, Protection, Tapes, Safety, Sprays, Displays, Accessories, Cleaning, Poles, Trowels |

## Example product rules

The product `Aster Microfiber Paint Roller` belongs to **Paint Rollers → Roller Covers → Microfiber** and may contain a numeric `working_width` in mm, `cover_material` as an enumerated option and `recyclable_packaging` as a boolean. It cannot arbitrarily store `protection_class` (Safety Gear) or `adhesive_type` (Adhesive Tapes).

A product classified under **Paint Rollers → Corner Rollers** has no Level-3 Type because Corner Rollers is terminal. In a flattened analytics view, `type = null` is a legitimate result, not a data-quality failure.

## Completeness and change safeguards

Creating or approving a product requires a valid terminal classification and all required technical attributes for that branch. A request that changes a classification but would invalidate existing technical values is not silently applied; it requires explicit migration handling and a new review. Option dictionaries and units are metadata, not free-form product columns.

## Why this helps ProductIntelligence

A consistent hierarchy allows comparable cohorts to be defined with adequate domain specificity. A shared family alone does not prove product equivalence: coverage analyses must also consider material, width, quality level, unit and business context. The demo never asserts approved equivalence from taxonomy labels alone.
