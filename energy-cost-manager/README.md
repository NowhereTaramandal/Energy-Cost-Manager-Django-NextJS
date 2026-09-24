# Energy Cost Manager

A full-stack university/project starter that analyses interval electricity usage and estimates what the same historical profile could cost under multiple stored energy tariffs.

## Stack

- **Backend:** Django 5 + Django REST Framework + JWT
- **Frontend:** Next.js 15 (Node.js) + React + TypeScript + Tailwind + Recharts
- **Database:** SQLite locally, PostgreSQL-ready for production/Docker
- **Admin:** Django Admin for providers, plans, tariff rates, users and uploads

## Included features

- User registration, JWT login, profile editing and password-reset flow
- CSV upload and validation
- Interval usage parsing (`timestamp,usage_kwh` or `date,time,usage_kwh`)
- Duplicate, invalid-date and negative-usage validation
- Daily, monthly and hourly consumption analytics
- Flat and time-of-use tariffs
- Daily supply charges
- Cost calculation and annualisation
- Multi-plan comparison
- Recommendation ordering by estimated annual cost
- Potential saving against a selected current plan
- Comparison history
- Downloadable CSV reports
- Django Admin
- OpenAPI/Swagger docs
- Fictional demonstration tariff seed data
- Sample interval CSV
- Docker Compose setup

> **Important:** The seeded provider names/rates are demonstration data, not verified current retail offers. Replace them with approved/verified tariff data before presenting estimates as real-world plan comparisons.

## Local setup

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_energy_plans
python manage.py createsuperuser
python manage.py runserver
```

Backend: `http://localhost:8000`  
Swagger: `http://localhost:8000/api/docs/`  
Admin: `http://localhost:8000/admin/`

### 2. Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Frontend: `http://localhost:3000`

### 3. Sample data

After registering/login, upload:

`sample-data/sample_usage.csv`

Then open **Compare Plans**, optionally select a current plan, and click **Compare plans**.

## CSV format

Option A:

```csv
timestamp,usage_kwh
2026-01-01 00:00,0.32
2026-01-01 00:30,0.25
```

Option B:

```csv
date,time,usage_kwh
2026-01-01,00:00,0.32
2026-01-01,00:30,0.25
```

Accepted usage aliases include `kwh`, `usage`, `consumption`, and `consumption_kwh`.

## Cost logic

For each reading, the backend selects the matching tariff rate and calculates:

```text
usage cost = Σ(interval kWh × applicable $/kWh)
supply cost = covered days × daily supply charge
historical cost = usage cost + supply cost
estimated annual cost = historical cost × (365 / covered days)
potential saving = current plan annual estimate - alternative annual estimate
```

The system intentionally keeps this calculation transparent instead of pretending to use AI.

## API summary

- `POST /api/auth/register/`
- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`
- `GET/PATCH /api/auth/me/`
- `POST /api/auth/forgot-password/`
- `POST /api/auth/reset-password/`
- `GET/POST /api/uploads/`
- `GET /api/uploads/{id}/analytics/`
- `GET /api/providers/`
- `GET /api/plans/`
- `POST /api/compare/`
- `GET /api/comparisons/`
- `GET /api/comparisons/{id}/`
- `GET /api/comparisons/{id}/report.csv`

## Docker

```bash
docker compose up --build
```

The Docker configuration uses PostgreSQL. Create a superuser with:

```bash
docker compose exec backend python manage.py createsuperuser
```

## Production notes

Before production deployment:

1. Set a strong `DJANGO_SECRET_KEY`.
2. Set `DJANGO_DEBUG=False`.
3. Set exact `DJANGO_ALLOWED_HOSTS`, CORS and trusted frontend origins.
4. Use PostgreSQL and persistent media storage.
5. Replace console email with a real transactional email provider.
6. Load only verified/current tariff data and record effective dates.
7. Add retailer-specific eligibility, discounts, solar feed-in, controlled-load and tax rules if they matter to your use case.
8. Add background jobs for very large interval CSV files.

## Suggested assessment demonstration

1. Register/login.
2. Upload the sample CSV.
3. Show validation and usage analytics.
4. Open energy plans and explain flat vs time-of-use rates.
5. Run a comparison with a current plan selected.
6. Explain the transparent calculation breakdown.
7. Show recommendations and potential savings.
8. Download the report.
9. Show Django Admin managing providers/rates.

## Project structure

```text
energy-cost-manager/
├── backend/       Django REST API
├── frontend/      Next.js / Node.js web app
├── sample-data/   CSV demonstration dataset
├── docker-compose.yml
└── README.md
```
