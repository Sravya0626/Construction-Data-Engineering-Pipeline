-- Illustrative dbt model; assumes source configuration has been added.
SELECT project_id, SUM(amount) AS actual_cost
FROM {{ source('construction', 'expenses') }}
GROUP BY project_id
