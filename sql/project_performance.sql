WITH spend AS (
  SELECT project_id, SUM(amount) AS actual_cost
  FROM expenses GROUP BY project_id
), delays AS (
  SELECT project_id,
         SUM(CASE WHEN julianday(actual_date) > julianday(planned_date) THEN 1 ELSE 0 END) AS delayed_milestones,
         SUM(CASE WHEN julianday(actual_date) > julianday(planned_date)
             THEN CAST(julianday(actual_date) - julianday(planned_date) AS INTEGER) ELSE 0 END) AS total_delay_days
  FROM milestones GROUP BY project_id
)
SELECT p.project_id, p.project_name,
       ROUND(p.budget, 2) AS budget,
       ROUND(COALESCE(s.actual_cost, 0), 2) AS actual_cost,
       ROUND(p.budget - COALESCE(s.actual_cost, 0), 2) AS budget_variance,
       ROUND(100.0 * COALESCE(s.actual_cost, 0) / p.budget, 2) AS budget_utilization_pct,
       COALESCE(d.delayed_milestones, 0) AS delayed_milestones,
       COALESCE(d.total_delay_days, 0) AS total_delay_days,
       CASE WHEN COALESCE(s.actual_cost, 0) > p.budget THEN 'OVER_BUDGET' ELSE 'WITHIN_BUDGET' END AS budget_status
FROM projects p
LEFT JOIN spend s ON p.project_id = s.project_id
LEFT JOIN delays d ON p.project_id = d.project_id
ORDER BY p.project_id;
