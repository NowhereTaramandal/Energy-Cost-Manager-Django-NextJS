# Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ USAGE_UPLOAD : owns
    USAGE_UPLOAD ||--o{ USAGE_READING : contains
    USER ||--o{ COMPARISON : creates
    USAGE_UPLOAD ||--o{ COMPARISON : analysed_in
    ENERGY_PROVIDER ||--o{ ENERGY_PLAN : offers
    ENERGY_PLAN ||--o{ TARIFF_RATE : has
    ENERGY_PLAN ||--o{ COMPARISON : current_plan
    COMPARISON ||--o{ COMPARISON_RESULT : contains
    ENERGY_PLAN ||--o{ COMPARISON_RESULT : evaluated_as
```

## Main relationships
- One user can own many uploads.
- One upload can contain many interval readings.
- One provider can have many plans.
- One plan can have one or more tariff rates.
- One comparison uses one uploaded usage dataset and can optionally identify a current plan.
- One comparison contains a result for each successfully evaluated active plan.
