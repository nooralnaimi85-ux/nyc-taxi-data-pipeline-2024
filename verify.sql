SELECT * FROM pipeline_audit;
SELECT count(*) AS fact_count FROM fact_trips;
SELECT count(*) AS month_count, sum(trips) AS monthly_total FROM monthly_summary;
SELECT sum(trips) AS hourly_total FROM hourly_summary;
SELECT sum(trips) AS payment_total FROM payment_summary;
SELECT * FROM monthly_summary;
SELECT * FROM hourly_summary;
SELECT * FROM payment_summary;
SELECT * FROM location_summary;
