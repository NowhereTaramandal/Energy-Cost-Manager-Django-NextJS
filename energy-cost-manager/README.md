# Energy Cost Manager

**A full-stack academic prototype for analysing electricity consumption and comparing estimated electricity plan costs.**

Energy Cost Manager allows users to upload historical interval electricity usage data, explore consumption patterns, and estimate what that usage would cost under electricity plans stored in the application. It ranks eligible comparison results by estimated annual cost and highlights potential differences between plans.

> **Important:** This is a university project prototype, not a commercial comparison or switching service. Calculations are estimates based on the uploaded data and configured tariffs. Stored demonstration plans must not be interpreted as verified, current market offers.

## Project objectives

- Import and validate electricity consumption data from CSV files.
- Present useful consumption statistics and visualisations.
- Compare the same historical usage profile against multiple configured electricity plans.
- Estimate annualised electricity costs, including usage and daily supply charges.
- Rank plan estimates and display indicative savings.
- Retain comparison history and allow CSV report downloads.

## Technology stack

| Layer | Technology |
| --- | --- |
| Backend | Python, Django 5.1.4, Django REST Framework 3.15.2 |
| Authentication | JSON Web Tokens (Simple JWT) |
| Administration | Django Admin with Jazzmin 3.0.5 |
| API documentation | drf-spectacular / OpenAPI / Swagger UI |
| Frontend | Next.js 15, React 19, TypeScript |
| Styling and charts | Tailwind CSS, Recharts, Lucide React |
| Local database | SQLite |
| Optional database configuration | PostgreSQL via psycopg |
| Container configuration | Docker and Docker Compose |

The backend was verified using Python 3.13 in a Windows virtual environment. For the frontend, use a Node.js release compatible with Next.js 15 and the included `package-lock.json`.

## Implemented functionality

### Accounts and access

- User registration and login.
- JWT-based API authentication and token refresh.
- Profile access and account-related screens.
- Password reset flow for the development environment.
- Administrative management through Django Admin.

### Electricity data import and analytics

- CSV upload with supported timestamp and usage columns.
- Validation of malformed values, negative consumption and duplicate readings.
- Storage of uploaded usage records and individual readings.
- Consumption summaries and daily, monthly and hourly analysis.
- Charts and dashboard views to explore electricity usage patterns.

### Plan comparison and reporting

- Stored electricity providers, plans and tariff rates.
- Flat-rate and time-of-use tariff calculations.
- Daily supply charges and usage-based charges.
- Annualised estimates derived from the uploaded data's covered period.
- Plan ranking, indicative cost differences and recommendations.
- Comparison history and downloadable CSV reports.

## Project structure

```text
energy-cost-manager/
├── backend/
│   ├── accounts/             # User accounts and authentication
│   ├── config/               # Django settings and project configuration
│   ├── energy/               # Usage, plans, comparisons and related APIs
│   │   ├── management/
│   │   │   └── commands/     # Data seeding commands
│   │   └── migrations/       # Database schema migrations
│   ├── .env.example          # Backend environment variable template
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile
│   └── manage.py
├── frontend/
│   ├── app/                  # Next.js pages and routes
│   ├── components/           # Shared interface components
│   ├── lib/                  # API helpers and TypeScript types
│   ├── .env.example          # Frontend environment variable template
│   ├── package.json
│   ├── package-lock.json
│   └── Dockerfile
├── docs/                      # Project documentation
├── sample-data/               # Sample and test CSV files
├── screenshots/               # Screenshots for demonstration
├── docker-compose.yml
├── .gitignore
└── README.md
```

This tree describes the application folder. In the development workspace, the Git repository root is one directory above `energy-cost-manager/`.

## Getting started — local development

### Prerequisites

- Python 3.13 (verified development version).
- Node.js compatible with Next.js 15 and npm.
- Git (for cloning and version control).

These instructions assume the terminal starts in the `energy-cost-manager` folder.

### 1. Set up the backend (Windows PowerShell)

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If `py -3.13` is unavailable, use the installed Python 3.13 executable to create the virtual environment. On macOS/Linux, create the environment with `python3 -m venv .venv` and activate it with `source .venv/bin/activate`.

The requirements file should include `django-jazzmin==3.0.5`, which is needed because the project enables Jazzmin in Django's installed applications.

### 2. Configure backend environment variables

The repository includes `backend/.env.example` as a reference for settings such as:

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_TIME_ZONE`
- `CORS_ALLOWED_ORIGINS`
- `FRONTEND_URL`

The current Django settings read environment variables with development defaults. Review `backend/config/settings.py` before changing the configuration. A `.env` file is **not automatically loaded** unless an environment-loading mechanism is configured; if needed, set the variables in your shell or deployment environment. Never commit real secrets.

### 3. Prepare the database and start Django

```powershell
python manage.py migrate
python manage.py seed_energy_plans
python manage.py createsuperuser
python manage.py check
python manage.py runserver
```

`seed_energy_plans` populates demonstration electricity plans for local testing. Review existing data before rerunning seed commands on a populated database.

Backend addresses:

- API base: <http://localhost:8000/api/>
- API documentation: <http://localhost:8000/api/docs/>
- Django Admin: <http://localhost:8000/admin/>

### 4. Set up and start the frontend

Open a **second terminal** in `energy-cost-manager/frontend`:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm ci
npm run dev
```

Check that `.env.local` contains the appropriate API base URL, for example:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

Open <http://localhost:3000> in your browser. Leave the Django and Next.js development servers running in their respective terminals.

**macOS/Linux:** use `cp .env.example .env.local` instead of `Copy-Item`.

### 5. Sign in and try the application

Register a user through the frontend or use a development account that you created locally. Upload a supported CSV, review the analytics, compare configured plans, inspect recommendations and history, and download a comparison report.

Do not publish account passwords, access tokens or local credential files in the repository.

## CSV input format

The application accepts supported electricity consumption CSV structures, including the following examples.

**Single timestamp column:**

```csv
timestamp,usage_kwh
2026-01-01 00:00,0.32
2026-01-01 00:30,0.25
2026-01-01 01:00,0.28
```

**Separate date and time columns:**

```csv
date,time,usage_kwh
2026-01-01,00:00,0.32
2026-01-01,00:30,0.25
2026-01-01,01:00,0.28
```

The import logic also recognises some alternative consumption column names, including `kwh`, `usage`, `consumption` and `consumption_kwh`. The importer does **not** support arbitrary CSV formats or automatic column mapping.

Consumption must be expressed in kilowatt-hours (kWh). Valid date/time formatting and appropriate reading intervals are important for meaningful comparisons. Validation can reject invalid, duplicate or negative readings. Incomplete datasets can reduce estimate reliability.

See `sample-data/` for example datasets. Choose a small, non-sensitive sample suitable for demonstration rather than committing large raw datasets.

## How electricity costs are estimated

For a given plan, the application applies the relevant configured tariff to each consumption interval:

```text
Usage cost = sum(interval consumption in kWh × applicable rate per kWh)
Supply cost = covered days × daily supply charge
Estimated period cost = usage cost + supply cost
Estimated annual cost = estimated period cost × (365 / covered days)
```

The same usage dataset is evaluated against multiple stored plans, and the estimated annual costs are ranked. Indicative savings are calculated as the difference between relevant plan estimates.

Flat-rate plans use a single usage rate. Time-of-use plans apply rates according to configured tariff periods, including periods that cross midnight.

**Interpretation:** Annualisation extrapolates the uploaded period to a year; it does not reconstruct actual annual bills. Seasonal variation, incomplete data, concessions, discounts, solar exports, demand charges and other plan-specific conditions may not be fully represented. Results are not guaranteed savings.

## API overview

The backend exposes REST endpoints for authentication, consumption uploads, analytics, energy plans and comparisons. Examples from the project's documented API structure include:

| Area | Endpoint |
| --- | --- |
| Register | `/api/auth/register/` |
| Obtain JWT | `/api/auth/token/` |
| Refresh JWT | `/api/auth/token/refresh/` |
| Current user | `/api/auth/me/` |
| Forgot password | `/api/auth/forgot-password/` |
| Reset password | `/api/auth/reset-password/` |
| Uploads | `/api/uploads/` |
| Upload analytics | `/api/uploads/{id}/analytics/` |
| Providers | `/api/providers/` |
| Plans | `/api/plans/` |
| Compare plans | `/api/compare/` |
| Comparison history | `/api/comparisons/` |
| Comparison details | `/api/comparisons/{id}/` |
| CSV comparison report | `/api/comparisons/{id}/report.csv` |

Endpoint methods, permissions, request bodies and response schemas should be checked in the running Swagger documentation at `/api/docs/`, which is the reference for the current code. Some URLs may differ as the project evolves.

## Database and migrations

The application uses SQLite for local development. Core data concepts include users, uploads, individual electricity readings, providers, plans, tariff rates, comparisons and comparison results.

Five `energy` migrations (`0001`–`0005`) were verified as applied in the development database. The migration chain includes additional energy-plan metadata such as distributor, plan reference, source URL and source-check date, as well as comparison-result snapshot information.

Verified backend checks:

```powershell
python manage.py check
python -m pip check
python manage.py showmigrations energy --plan
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
```

During verification, Django reported no system-check issues, no broken installed requirements, no missing model migrations and no unapplied migrations. Migration `0002` also generated SQL successfully. These checks do not replace a clean-install test on a new machine or database.

## Testing and verification

The following workflows were manually exercised during development:

1. Open the frontend and log in using a test account.
2. Upload a valid electricity usage CSV.
3. View consumption analytics.
4. View configured electricity plans.
5. Run a multi-plan cost comparison.
6. View plan recommendations and comparison history.
7. Download a CSV comparison report.

These are **manual smoke tests**, not a comprehensive automated test suite. Future testing should cover fresh installations, invalid and incomplete CSV inputs, edge cases in tariff matching, cost calculations, authentication, and frontend/backend integration.

## Known limitations

- **Academic prototype:** Not a production-ready electricity comparison, billing or switching service.
- **Restricted CSV formats:** Supports defined input structures rather than automatic mapping of arbitrary retailer or meter exports.
- **Manually maintained plan data:** Tariffs are stored in the application; automatic retrieval and ongoing verification of live provider offers have not been implemented.
- **Demonstration tariffs:** Seeded example plans are for testing and must not be treated as current market offers. Source metadata on a plan does not guarantee that its rates are up to date.
- **Estimated costs:** Results depend on the quality and coverage of uploaded readings and the accuracy of configured plan rules.
- **Limited personal advice:** Consumption charts and plan recommendations do not yet provide tailored behavioural energy-saving advice.
- **Development configuration:** Local defaults, SQLite and console-based email are not suitable production settings without further work.
- **Further quality assurance needed:** Broader automated tests, security review and validation against actual electricity bills remain future work.

## Recommended future improvements

1. Add flexible CSV field mapping and support for additional meter-data export formats.
2. Integrate a reliable source of current electricity offers, with update scheduling and source verification.
3. Provide personalised energy conservation suggestions based on observed usage patterns.
4. Extend tariff calculations to account for more complex pricing structures and eligibility rules.
5. Add automated unit, integration and end-to-end tests, including a clean database setup test.
6. Harden deployment security, configure production email and establish operational monitoring.

These improvements reflect project limitations and development feedback; they should not be presented as completed functionality.

## Docker configuration

The repository contains backend and frontend Dockerfiles and a `docker-compose.yml` file. A container-based setup may be attempted with:

```powershell
docker compose up --build
```

**Note:** Docker startup and end-to-end operation have not been verified as part of the checks documented here. Review Compose environment variables, database configuration and service dependencies before using this method.

## Security and repository hygiene

- Never commit `.env` files, credentials, API tokens or real account passwords.
- Do not commit the local SQLite database or database backups.
- Keep virtual environments, `node_modules/`, Next.js build output and generated media out of Git.
- Avoid committing large raw electricity datasets or personally identifiable meter data.
- Use demonstration data and placeholder account details in documentation.
- Review `git status` and `git diff --cached` before committing.

## Project status

The core academic prototype has been implemented and manually demonstrated. The Django dependency environment and existing database migration state were verified during handover preparation. Production deployment, live tariff synchronization and broader automated validation remain outside the verified scope.

## License and use

Developed for academic assessment and demonstration. No open-source licence is asserted by this README; reuse permissions depend on the repository's actual licence and applicable institutional requirements.
