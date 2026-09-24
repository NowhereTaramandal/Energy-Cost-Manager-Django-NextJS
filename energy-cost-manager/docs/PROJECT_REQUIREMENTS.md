# Project Requirements

## Objective
The Energy Cost Manager lets a user import historical electricity interval data, analyse consumption, compare stored electricity tariffs, estimate annual cost and display possible savings.

## Functional requirements
1. User can register, sign in, reset a password and edit a profile.
2. User can upload CSV interval data.
3. System validates missing values, invalid dates, duplicates and negative usage.
4. System stores readings against the authenticated user.
5. System provides daily, monthly and time-of-day analytics.
6. Administrator can manage providers, plans, rates and effective dates.
7. System supports flat and time-of-use usage charges plus daily supply charges.
8. User can select a current plan and compare all active plans.
9. System provides an auditable usage-cost and supply-cost breakdown.
10. System ranks results by estimated annual cost and calculates potential saving versus the current plan.
11. User can view historical comparisons and download a CSV report.
12. API documentation is available through Swagger/OpenAPI.

## Non-functional requirements
- Authentication-protected user data.
- Responsive web UI.
- PostgreSQL production compatibility.
- Configuration through environment variables.
- Clear separation between Django REST backend and Node.js/Next.js frontend.
- Transparent calculations rather than opaque recommendation logic.

## Scope notes
The demonstration seed data is fictional. Production-grade retail comparison would also need plan eligibility, postcode/distributor constraints, GST treatment, discounts, controlled-load tariffs, solar feed-in tariffs, demand charges and tariff effective-date validation where applicable.
