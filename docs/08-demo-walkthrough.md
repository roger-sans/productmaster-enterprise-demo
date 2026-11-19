# Fifteen-minute Product Owner demo walkthrough

This is a suggested **portfolio demonstration script**, not a record of actual enterprise meetings.

## 0–2 min · Explain the problem

Start on **Overview**. Introduce the challenge of contradictory departmental vocabularies and how a governed product master creates a shared language. Point out the division between ProductMaster and ProductIntelligence. Explain that all products and measurements are synthetic.

## 2–5 min · Walk through the taxonomy

Go to **Taxonomy** → expand **Paint Rollers** → **Roller Covers**. Explain family, subfamily and type; show sibling categories and stable machine codes. Click a terminal subfamily such as **Corner Rollers** and explain why a missing Type is **valid when a subfamily has no type children**, whereas a nonterminal parent would not be valid for accepted products.

## 5–7 min · Show governed specifications

Open **Attribute library** and filter for `Working width`, `Cover material`, `Adhesive type` or `Recyclable packaging`. Explain datatype, allowed options, units, applicability and requiredness. Open a **Product catalogue** item and show product-specific values, source mapping and lineage.

## 7–11 min · Demonstrate controlled decisions

Choose a product in the catalogue. Click **Propose governed change**. Select a destination in the same family, provide a rationale and simulated department/actor. Submit. The master record remains unchanged. On **Governance**, review as a different actor, approve and reopen the product. The new classification and version appear, with an audit event. Repeat a separate request and reject to show the master stays unchanged. Do not pretend the demo actors are authenticated.

## 11–13 min · Show ProductIntelligence

Open **ProductIntelligence**. Contrast products with complete observations against products with partial evidence. Explain a 90-day historical sales rate and a 30-day illustrative shortfall, plus why missing or zero demand cannot be treated as a valid 0-day coverage figure. Clarify that no purchasing or source-system action is executed.

## 13–15 min · Close with Product Owner leadership

Open **Product strategy**. Highlight the priority order: align departments, agree data ownership, deliver a trusted master, formalise corrections, and only then build analytical value. Discuss trade-offs, acceptance criteria, nonfunctional work and adoption. Recognise the difference between this finished **local portfolio demonstration** and a real certified production system.

## Technical challenge

To show engineering maturity, run `pytest -q`, review the versioned OpenAPI specification at `/docs` and explain how to migrate the persistence module to protected relational storage with SSO and release gates.
