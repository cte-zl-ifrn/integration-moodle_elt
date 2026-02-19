"""
Moodle 1 ELT DAG - Extract, Load, Transform
Extracts data from Moodle instance 1 via Web Services API,
loads raw JSON to PostgreSQL, transforms to staging tables,
and aggregates to mart for Superset dashboards.
"""

from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable

import sys
sys.path.insert(0, str(Path(__file__).parent))

from utils.moodle_api import (
    MoodleAPIClient,
    prepare_raw_record,
    validate_json_schema,
    compute_hash,
    get_moodle_instance_config,
    parse_moodle_config
)

logger = logging.getLogger(__name__)

# DAG Configuration
MOODLE_INSTANCE = 'moodle4'
POSTGRES_CONN_ID = 'postgres_moodle'

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


def get_moodle_client() -> MoodleAPIClient:
    """
    Initialize Moodle API client from Airflow Variables.
    Supports both comma-separated lists and individual instance variables.
    """
    try:
        # Try to get individual instance variables first (legacy support)
        base_url = Variable.get(f'{MOODLE_INSTANCE}_url')
        token = Variable.get(f'{MOODLE_INSTANCE}_token')
        logger.info(f"Using individual variables for {MOODLE_INSTANCE}")
    except KeyError:
        # Fall back to comma-separated configuration
        try:
            urls_str = Variable.get('MOODLE_URLS')
            tokens_str = Variable.get('MOODLE_TOKENS')
            
            # Parse and get configuration for this instance
            config = get_moodle_instance_config(MOODLE_INSTANCE, urls_str, tokens_str)
            base_url = config['url']
            token = config['token']
            logger.info(f"Using comma-separated configuration for {MOODLE_INSTANCE}")
        except KeyError as e:
            raise ValueError(
                f"Missing Moodle configuration for {MOODLE_INSTANCE}. "
                f"Please configure either:\n"
                f"1. Individual variables: {MOODLE_INSTANCE}_url and {MOODLE_INSTANCE}_token\n"
                f"2. Comma-separated lists: MOODLE_URLS and MOODLE_TOKENS"
            ) from e
    
    return MoodleAPIClient(base_url=base_url, token=token)


def extract_users(**context):
    """Extract all users from Moodle."""
    logger.info(f"Extracting users from {MOODLE_INSTANCE}")
    
    client = get_moodle_client()
    users = client.get_users()
    
    logger.info(f"Extracted {len(users)} users")
    
    # Push to XCom for load task
    context['ti'].xcom_push(key='users', value=users)
    return len(users)


def extract_courses(**context):
    """Extract all courses from Moodle."""
    logger.info(f"Extracting courses from {MOODLE_INSTANCE}")
    
    client = get_moodle_client()
    courses = client.get_courses()
    
    logger.info(f"Extracted {len(courses)} courses")
    
    # Push to XCom
    context['ti'].xcom_push(key='courses', value=courses)
    return len(courses)


def extract_roles(**context):
    """Extract all roles from Moodle."""
    logger.info(f"Extracting roles from {MOODLE_INSTANCE}")
    
    client = get_moodle_client()
    roles = client.get_roles()
    
    logger.info(f"Extracted {len(roles)} roles")
    
    context['ti'].xcom_push(key='roles', value=roles)
    return len(roles)


def extract_enrolments(**context):
    """Extract enrolments (enrolled users per course) from Moodle."""
    logger.info(f"Extracting enrolments from {MOODLE_INSTANCE}")
    
    client = get_moodle_client()
    
    # Get courses first
    ti = context['ti']
    courses = ti.xcom_pull(task_ids='extract_courses', key='courses')
    
    all_enrolments = []
    for course in courses:
        course_id = course.get('id')
        if course_id:
            try:
                enrolled_users = client.get_enrolled_users(course_id)
                # Add course_id to each enrolment record
                for user in enrolled_users:
                    user['course_id'] = course_id
                all_enrolments.extend(enrolled_users)
            except Exception as e:
                logger.error(f"Failed to get enrolments for course {course_id}: {e}")
    
    logger.info(f"Extracted {len(all_enrolments)} enrolments")
    
    context['ti'].xcom_push(key='enrolments', value=all_enrolments)
    return len(all_enrolments)


def extract_enrolment_methods(**context):
    """Extract enrolment methods from Moodle."""
    logger.info(f"Extracting enrolment methods from {MOODLE_INSTANCE}")
    
    client = get_moodle_client()
    
    # Get courses first
    ti = context['ti']
    courses = ti.xcom_pull(task_ids='extract_courses', key='courses')
    
    all_methods = []
    for course in courses:
        course_id = course.get('id')
        if course_id:
            try:
                methods = client.get_enrolment_methods(course_id)
                for method in methods:
                    method['course_id'] = course_id
                all_methods.extend(methods)
            except Exception as e:
                logger.error(f"Failed to get enrolment methods for course {course_id}: {e}")
    
    logger.info(f"Extracted {len(all_methods)} enrolment methods")
    
    context['ti'].xcom_push(key='enrolment_methods', value=all_methods)
    return len(all_methods)


def extract_grade_items(**context):
    """Extract grade items from Moodle."""
    logger.info(f"Extracting grade items from {MOODLE_INSTANCE}")
    
    client = get_moodle_client()
    
    # Get courses first
    ti = context['ti']
    courses = ti.xcom_pull(task_ids='extract_courses', key='courses')
    
    all_grade_items = []
    for course in courses:
        course_id = course.get('id')
        if course_id:
            try:
                items = client.get_course_grade_items(course_id)
                for item in items:
                    item['course_id'] = course_id
                all_grade_items.extend(items)
            except Exception as e:
                logger.error(f"Failed to get grade items for course {course_id}: {e}")
    
    logger.info(f"Extracted {len(all_grade_items)} grade items")
    
    context['ti'].xcom_push(key='grade_items', value=all_grade_items)
    return len(all_grade_items)


def extract_grades(**context):
    """Extract grades from Moodle."""
    logger.info(f"Extracting grades from {MOODLE_INSTANCE}")
    
    client = get_moodle_client()
    
    # Get courses and users
    ti = context['ti']
    courses = ti.xcom_pull(task_ids='extract_courses', key='courses')
    
    all_grades = []
    for course in courses:
        course_id = course.get('id')
        if course_id:
            try:
                grades = client.get_grades(course_id)
                for grade in grades:
                    grade['course_id'] = course_id
                all_grades.extend(grades)
            except Exception as e:
                logger.error(f"Failed to get grades for course {course_id}: {e}")
    
    logger.info(f"Extracted {len(all_grades)} grades")
    
    context['ti'].xcom_push(key='grades', value=all_grades)
    return len(all_grades)


def extract_completions(**context):
    """Extract course completions from Moodle."""
    logger.info(f"Extracting completions from {MOODLE_INSTANCE}")
    
    client = get_moodle_client()
    
    # Get enrolments (course + user combinations)
    ti = context['ti']
    enrolments = ti.xcom_pull(task_ids='extract_enrolments', key='enrolments')
    
    all_completions = []
    for enrolment in enrolments:
        course_id = enrolment.get('course_id')
        user_id = enrolment.get('id')
        
        if course_id and user_id:
            try:
                completion = client.get_course_completion(course_id, user_id)
                completion['course_id'] = course_id
                completion['userid'] = user_id
                all_completions.append(completion)
            except Exception as e:
                logger.warning(f"Failed to get completion for course {course_id}, user {user_id}: {e}")
    
    logger.info(f"Extracted {len(all_completions)} completions")
    
    context['ti'].xcom_push(key='completions', value=all_completions)
    return len(all_completions)


def load_raw_data(entity: str, **context):
    """
    Load extracted data into moodle_raw table.
    
    Args:
        entity: Entity type (user, course, etc.)
    """
    logger.info(f"Loading {entity} data to moodle_raw")
    
    ti = context['ti']
    data = ti.xcom_pull(task_ids=f'extract_{entity}', key=entity)
    
    if not data:
        logger.warning(f"No {entity} data to load")
        return 0
    
    # Prepare records
    records = []
    for item in data:
        moodle_id = item.get('id') or item.get('course_id')
        
        # Validate schema
        try:
            validate_json_schema(item, entity.rstrip('s'))  # Remove plural
        except ValueError as e:
            logger.warning(f"Schema validation failed: {e}")
        
        record = prepare_raw_record(
            instance=MOODLE_INSTANCE,
            entity=entity.rstrip('s'),  # Remove plural (users -> user)
            moodle_id=moodle_id,
            data=item
        )
        records.append(record)
    
    # Bulk insert to PostgreSQL
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    
    insert_sql = """
        INSERT INTO moodle_raw (instance, entity, moodle_id, data_json, ts_extract, hash_content)
        VALUES (%s, %s, %s, %s, %s, decode(%s, 'hex'))
        ON CONFLICT (instance, entity, moodle_id, ts_extract) DO NOTHING
    """
    
    conn = hook.get_conn()
    cursor = conn.cursor()
    
    try:
        for record in records:
            cursor.execute(insert_sql, (
                record['instance'],
                record['entity'],
                record['moodle_id'],
                record['data_json'],
                record['ts_extract'],
                record['hash_content']
            ))
        conn.commit()
        logger.info(f"Loaded {len(records)} {entity} records to moodle_raw")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to load {entity} data: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    
    return len(records)


def update_ckan_metadata(**context):
    """Update CKAN metadata catalog (placeholder for future implementation)."""
    logger.info(f"Updating CKAN metadata for {MOODLE_INSTANCE}")
    
    # Get statistics from previous tasks
    ti = context['ti']
    
    metadata = {
        'instance': MOODLE_INSTANCE,
        'last_update': datetime.utcnow().isoformat(),
        'statistics': {
            'users': ti.xcom_pull(task_ids='extract_users'),
            'courses': ti.xcom_pull(task_ids='extract_courses'),
            'roles': ti.xcom_pull(task_ids='extract_roles'),
            'enrolments': ti.xcom_pull(task_ids='extract_enrolments'),
            'grade_items': ti.xcom_pull(task_ids='extract_grade_items'),
            'grades': ti.xcom_pull(task_ids='extract_grades'),
            'completions': ti.xcom_pull(task_ids='extract_completions'),
        }
    }
    
    logger.info(f"CKAN Metadata: {json.dumps(metadata, indent=2)}")
    
    # TODO: Implement actual CKAN API integration
    # For now, just log the metadata
    
    return metadata


# Create DAG
with DAG(
    dag_id=f'{MOODLE_INSTANCE}_elt',
    default_args=default_args,
    description=f'ELT pipeline for {MOODLE_INSTANCE} - Extract from Moodle API, Load to PostgreSQL, Transform to staging/mart',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
    tags=['moodle', 'elt', MOODLE_INSTANCE],
) as dag:
    
    # ========================================
    # PHASE 1: CREATE SCHEMAS
    # ========================================
    create_raw_schema = PostgresOperator(
        task_id='create_raw_schema',
        postgres_conn_id=POSTGRES_CONN_ID,
        sql='sql/01_create_raw.sql'
    )
    
    # ========================================
    # PHASE 2: EXTRACT (Parallel)
    # ========================================
    extract_users_task = PythonOperator(
        task_id='extract_users',
        python_callable=extract_users
    )
    
    extract_courses_task = PythonOperator(
        task_id='extract_courses',
        python_callable=extract_courses
    )
    
    extract_roles_task = PythonOperator(
        task_id='extract_roles',
        python_callable=extract_roles
    )
    
    # These depend on courses
    extract_enrolments_task = PythonOperator(
        task_id='extract_enrolments',
        python_callable=extract_enrolments
    )
    
    extract_enrolment_methods_task = PythonOperator(
        task_id='extract_enrolment_methods',
        python_callable=extract_enrolment_methods
    )
    
    extract_grade_items_task = PythonOperator(
        task_id='extract_grade_items',
        python_callable=extract_grade_items
    )
    
    extract_grades_task = PythonOperator(
        task_id='extract_grades',
        python_callable=extract_grades
    )
    
    # This depends on enrolments
    extract_completions_task = PythonOperator(
        task_id='extract_completions',
        python_callable=extract_completions
    )
    
    # ========================================
    # PHASE 3: LOAD RAW (Parallel)
    # ========================================
    load_users = PythonOperator(
        task_id='load_users',
        python_callable=load_raw_data,
        op_kwargs={'entity': 'users'}
    )
    
    load_courses = PythonOperator(
        task_id='load_courses',
        python_callable=load_raw_data,
        op_kwargs={'entity': 'courses'}
    )
    
    load_roles = PythonOperator(
        task_id='load_roles',
        python_callable=load_raw_data,
        op_kwargs={'entity': 'roles'}
    )
    
    load_enrolments = PythonOperator(
        task_id='load_enrolments',
        python_callable=load_raw_data,
        op_kwargs={'entity': 'enrolments'}
    )
    
    load_enrolment_methods = PythonOperator(
        task_id='load_enrolment_methods',
        python_callable=load_raw_data,
        op_kwargs={'entity': 'enrolment_methods'}
    )
    
    load_grade_items = PythonOperator(
        task_id='load_grade_items',
        python_callable=load_raw_data,
        op_kwargs={'entity': 'grade_items'}
    )
    
    load_grades = PythonOperator(
        task_id='load_grades',
        python_callable=load_raw_data,
        op_kwargs={'entity': 'grades'}
    )
    
    load_completions = PythonOperator(
        task_id='load_completions',
        python_callable=load_raw_data,
        op_kwargs={'entity': 'completions'}
    )
    
    # ========================================
    # PHASE 4: TRANSFORM TO STAGING (Sequential)
    # ========================================
    transform_users = PostgresOperator(
        task_id='transform_users',
        postgres_conn_id=POSTGRES_CONN_ID,
        sql='sql/02_transform_users.sql'
    )
    
    transform_courses = PostgresOperator(
        task_id='transform_courses',
        postgres_conn_id=POSTGRES_CONN_ID,
        sql='sql/03_transform_courses.sql'
    )
    
    transform_enrolments = PostgresOperator(
        task_id='transform_enrolments',
        postgres_conn_id=POSTGRES_CONN_ID,
        sql='sql/04_transform_enrolments.sql'
    )
    
    transform_roles = PostgresOperator(
        task_id='transform_roles',
        postgres_conn_id=POSTGRES_CONN_ID,
        sql='sql/05_transform_roles.sql'
    )
    
    transform_grade_items = PostgresOperator(
        task_id='transform_grade_items',
        postgres_conn_id=POSTGRES_CONN_ID,
        sql='sql/06_transform_grade_items.sql'
    )
    
    transform_grades = PostgresOperator(
        task_id='transform_grades',
        postgres_conn_id=POSTGRES_CONN_ID,
        sql='sql/07_transform_grades.sql'
    )
    
    transform_completions = PostgresOperator(
        task_id='transform_completions',
        postgres_conn_id=POSTGRES_CONN_ID,
        sql='sql/08_transform_completions.sql'
    )
    
    # ========================================
    # PHASE 5: AGGREGATE TO MART
    # ========================================
    build_mart_performance = PostgresOperator(
        task_id='build_mart_performance',
        postgres_conn_id=POSTGRES_CONN_ID,
        sql='sql/99_mart_performance.sql'
    )
    
    # ========================================
    # PHASE 6: CKAN METADATA UPDATE
    # ========================================
    update_ckan = PythonOperator(
        task_id='update_ckan_metadata',
        python_callable=update_ckan_metadata
    )
    
    # ========================================
    # DEFINE TASK DEPENDENCIES
    # ========================================
    
    # Schema creation first
    create_raw_schema >> [extract_users_task, extract_courses_task, extract_roles_task]
    
    # Extract dependencies
    extract_courses_task >> [
        extract_enrolments_task,
        extract_enrolment_methods_task,
        extract_grade_items_task,
        extract_grades_task
    ]
    
    extract_enrolments_task >> extract_completions_task
    
    # Load dependencies (extract -> load for each entity)
    extract_users_task >> load_users
    extract_courses_task >> load_courses
    extract_roles_task >> load_roles
    extract_enrolments_task >> load_enrolments
    extract_enrolment_methods_task >> load_enrolment_methods
    extract_grade_items_task >> load_grade_items
    extract_grades_task >> load_grades
    extract_completions_task >> load_completions
    
    # Transform dependencies (load -> transform for each entity)
    load_users >> transform_users
    load_courses >> transform_courses
    load_enrolments >> transform_enrolments
    load_roles >> transform_roles
    load_grade_items >> transform_grade_items
    load_grades >> transform_grades
    load_completions >> transform_completions
    
    # Mart depends on all transforms
    [
        transform_users,
        transform_courses,
        transform_enrolments,
        transform_roles,
        transform_grade_items,
        transform_grades,
        transform_completions
    ] >> build_mart_performance
    
    # CKAN update at the end
    build_mart_performance >> update_ckan
