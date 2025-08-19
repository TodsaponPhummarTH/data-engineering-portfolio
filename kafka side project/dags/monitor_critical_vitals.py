from airflow import DAG
from datetime import datetime
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    dag_id='monitor_critical_vitals',  # shows on Airflow UI must be Unique
    description='Monitor critical vitals from IoT devices',
    start_date=datetime(2024, 1, 1),  # is when the DAG will start running
    schedule_interval='@daily',  # run once a day
    catchup=False  # do not run for past dates which u dont know why we need that??
) as dag:
    #check fever
    check_fever = PostgresOperator(
        task_id='check_fever',
        postgres_conn_id='postgres_default',
        sql='''
        SELECT 
            COUNT(*) AS fever_count,
            device_id,
            DATE(timestamp) AS reading_date
        FROM 
            iot_readings
        WHERE
            temperature > 39.0
        GROUP BY 
            device_id, 
            DATE(timestamp)
        ORDER BY 
            reading_date DESC,
            device_id;
        ''',
        do_xcom_push=False
    )
    #check low heart rate
    check_low_heart_rate = PostgresOperator(
        task_id='check_low_heart_rate',
        postgres_conn_id='postgres_default',
        sql='''
        SELECT id,device_id ,patient_id,heart_rate ,
        case when heart_rate < 60 then 'Risk bradycardia'
        when heart_rate > 140 then 'Risk tachycardia' else 'Normal' end as potential_risk
        FROM iot_readings 
        order by 
        heart_rate desc
        ;     
        ''',
        do_xcom_push=False
    )
    # check oxygen level SP02
    check_low_spo2 = PostgresOperator(
        task_id='check_low_spo2',
        postgres_conn_id='postgres_default',
        sql='''
        SELECT 
            device_id,
            patient_id,
            spo2,
            DATE(timestamp),
            CASE
                WHEN spo2 < 90 THEN 'SEVERE_HYPOXEMIA'
                WHEN spo2 >= 90 AND spo2 <= 92 THEN 'MODERATE_HYPOXEMIA'
                WHEN spo2 >= 93 AND spo2 <= 94 THEN 'MILD_HYPOXEMIA'
                ELSE 'NORMAL'
            END AS oxygen_status
        FROM 
            iot_readings
        WHERE 
            spo2 < 95  -- Focus on all concerning SPO2 readings
            AND timestamp > NOW() - INTERVAL '24 hours'
        ORDER BY 
            spo2 ASC,  -- Most severe cases first
            timestamp DESC
        ''',
        do_xcom_push=False
    )