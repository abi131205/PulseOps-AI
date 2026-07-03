# PulseOps AI - GitHub Collaboration & Development Workflow Bible

This document details the branch management system, commit conventions, GitHub Actions integrations, and issue tracking boards for the PulseOps AI team.

---

## 🌿 1. Branch Strategy (Git Flow)

To ensure seamless parallel development, the team uses a structured branching structure:

```text
  main (Production ready releases)
   ▲
   │ (Release Pull Request)
  develop (Integration & testing)
   ▲
   ├── feature/frontend (React dashboard interface development)
   ├── feature/backend (FastAPI and router endpoints)
   ├── feature/analytics (RAPIDS cuDF calculations)
   └── feature/cloud (BigQuery connections and setup scripts)
```

---

## 📝 2. Commit Naming Conventions

All commits must follow the Conventional Commits structure:
`type(scope): brief description`

### 50 Specific PulseOps AI Commit Examples:

#### Features (`feat`)
1. `feat(repo): initialize workspace structure and base configure`
2. `feat(env): add .env.example with dataset profiles and port settings`
3. `feat(data): build generate_data.py for small medium large CSVs`
4. `feat(data): add emergency incident log generator tracking trauma surges`
5. `feat(cloud): create SQL tables for equipment telemetry warehouse`
6. `feat(cloud): create SQL tables for maintenance and bed occupancy logs`
7. `feat(cloud): add SQL table for emergency incident logs`
8. `feat(cloud): build upload_to_bigquery.py dataset loader script`
9. `feat(analytics): create pipeline.py with GPU cuDF groupby aggregates`
10. `feat(analytics): implement rolling average window for bed occupancy in cuDF`
11. `feat(analytics): add performance benchmarking code in pipeline.py`
12. `feat(analytics): implement development mode CPU pandas fallback`
13. `feat(backend): configure fastapi app entry point main.py`
14. `feat(backend): implement BaseSettings loader config.py`
15. `feat(backend): add /api/health verification endpoint`
16. `feat(backend): add /api/command-center stats rollup endpoint`
17. `feat(backend): add /api/benchmark timing comparative endpoint`
18. `feat(backend): add /api/equipment active inventory logs endpoint`
19. `feat(backend): add /api/recommendations priority queue endpoint`
20. `feat(backend): create decision_engine.py with OPS scoring logic`
21. `feat(backend): implement weight-based heuristic formula in decision engine`
22. `feat(backend): create recommendation_engine.py allocating resources`
23. `feat(backend): implement validation.py equipment safety checks`
24. `feat(backend): create gemini.py client explaining recommendations`
25. `feat(backend): implement local fallback briefs when API key missing`
26. `feat(frontend): initialize react project with vite scaffold`
27. `feat(frontend): set up postcss and tailwind CSS config files`
28. `feat(frontend): add outfit font and dark background styling in index.css`
29. `feat(frontend): install axios, recharts, and lucide-react packages`
30. `feat(frontend): build App.jsx sidebar layout and routing frames`
31. `feat(frontend): build Command Center page displaying stats summary cards`
32. `feat(frontend): integrate Recharts line chart showing occupancy trends`
33. `feat(frontend): build Operational Priorities recommendations table`
34. `feat(frontend): build Equipment Intelligence active telemetry status board`
35. `feat(frontend): build System Performance benchmark timer comparison card`
36. `feat(frontend): integrate Recharts bar chart showing CPU vs GPU speedup`
37. `feat(deploy): create multi-stage Dockerfile compiling React assets`
38. `feat(deploy): write deploy.sh script submitting Cloud Build image`
39. `feat(ci): build deploy.yml GitHub Actions validation pipeline`

#### Fixes (`fix`)
40. `fix(backend): resolve pydantic settings class loading errors`
41. `fix(analytics): handle missing datasets folder directory path crashes`
42. `fix(analytics): resolve pyarrow import errors during BigQuery read`
43. `fix(backend): add CORS middleware allowing Vite origin requests`
44. `fix(frontend): adjust index.css imports to resolve PostCSS build warnings`
45. `fix(frontend): bind dynamic axios data updates to sidebar triggers`
46. `fix(deploy): adjust Dockerfile working paths to copy static assets`

#### Documentation (`docs`)
47. `docs(root): compose main README.md run guidelines`
48. `docs(specs): build project context single source of truth`
49. `docs(specs): build technical design bible database schemas`
50. `docs(specs): build github workflow collaboration guide`

---

## 🛠️ 3. Continuous Integration Configuration

The GitHub Action in `.github/workflows/deploy.yml` triggers on all pushes to `main` and `develop` to verify frontend production builds and backend syntax checks.
