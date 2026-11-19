# Publish the independent ProductMaster demo to a personal GitHub repository

This folder is **ready to initialise as a separate repository**. It has no remote, employer origin or embedded `.git` history.

## Recommended steps

1. Extract the ZIP locally and open a terminal inside `productmaster-complete`.
2. Review `README.md`, `docs/09-disclosure-and-limits.md` and the source code, including suitability for publication under your employment agreements.
3. Create a new empty GitHub repository in your own account, for example `productmaster-enterprise-demo`. Choose **Public** only after reviewing the project. Do not add a second README or `.gitignore` during creation; both are already provided.
4. Initialise and push the files (replace `YOUR_GITHUB_USERNAME`):

```bash
git init
git branch -M main
git add .
git status --short
git commit -m "Build synthetic ProductMaster and explainable ProductIntelligence demo"
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/productmaster-enterprise-demo.git
git push -u origin main
```

5. Add the GitHub repository link wherever you present your personal technical portfolio. **Do not claim** the synthetic UI and data were deployed at an employer or that fictional outcomes were measured.

## Suggested repository metadata

**Name:** `productmaster-enterprise-demo`

**Description:** `End-to-end synthetic ProductMaster: governed taxonomy, technical attributes, cross-functional change approvals and explainable ProductIntelligence. FastAPI + SQLite.`

**Topics:** `product-owner`, `data-governance`, `master-data-management`, `product-information-management`, `fastapi`, `data-products`, `taxonomy`, `data-quality`, `product-analytics`

**Preview image:** `assets/01-overview.png`

## Safety checks

- `.gitignore` excludes generated SQLite databases, credentials, `.env` and virtual environments.
- The tracked `sample_data/` files contain **fictional** product examples only.
- Avoid adding corporate screenshots, exports or documentation in follow-up commits.
- The `data/` folder will be regenerated on first local start.
- The application has **simulated actors, no real authentication**. Keep runtime access on localhost; do not publish the API as a public hosted service without implementing actual access controls.
