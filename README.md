# Moodle ELT Integration - 4 Instances → PostgreSQL Central

Complete ELT (Extract, Load, Transform) pipeline for integrating 4 Moodle instances into a centralized PostgreSQL data warehouse, optimized for Superset dashboards and CKAN publication.

## 🎯 Overview

This project implements 4 parallel Airflow DAGs that:
- **Extract** data from 4 Moodle instances (3 cloud + 1 on-premise) via Web Services API
- **Load** raw JSON data into PostgreSQL landing zone (`moodle_raw`)
- **Transform** data into normalized staging tables (`moodle_stg.*`)
- **Aggregate** into analytics-ready mart tables (`moodle_mart.*`)
- **Publish** metadata to CKAN data catalog

## 📊 Data Entities Extracted

Each Moodle instance extracts 8 priority entities:

1. **Users** → `core_user_get_users` (all users)
2. **Courses** → `core_course_get_courses` (all courses)
3. **Roles** → `core_role_get_all_roles` (all roles)
4. **Enrolments** → `core_enrol_get_enrolled_users` (student enrollments by course)
5. **Enrolment Methods** → `core_enrol_get_course_enrolment_methods`
6. **Grade Items** → `gradereport_user_get_grade_items` (assessment items)
7. **Grades** → `gradereport_user_get_grades_table` (student grades)
8. **Completions** → `core_completion_get_course_completion_status`

## 🏗️ Architecture

```
┌─────────────────┐
│  Moodle 1-4     │
│  Web Services   │
└────────┬────────┘
         │ Extract (API)
         ▼
┌─────────────────┐
│  moodle_raw     │  ← Raw JSON Landing Zone
│  (JSONB)        │
└────────┬────────┘
         │ Transform (SQL)
         ▼
┌─────────────────┐
│  moodle_stg.*   │  ← Normalized Staging Tables
│  - users        │     (users, courses, grades, etc.)
│  - courses      │
│  - enrolments   │
│  - grades       │
└────────┬────────┘
         │ Aggregate (SQL)
         ▼
┌─────────────────┐
│  moodle_mart.*  │  ← Analytics Mart (Superset Ready)
│  - course_      │
│    performance  │
└─────────────────┘
```

## 🗄️ Database Schema

### Layer 1: Raw JSON Landing Zone

```sql
CREATE TABLE moodle_raw (
    id BIGSERIAL PRIMARY KEY,
    instance VARCHAR(50),      -- 'moodle1', 'moodle2', etc.
    entity VARCHAR(50),        -- 'user', 'course', 'grade', etc.
    moodle_id BIGINT,          -- Original Moodle ID
    data_json JSONB,
    ts_extract TIMESTAMPTZ,
    hash_content BYTEA         -- MD5 for deduplication
);
```

### Layer 2: Staging Tables (Normalized)

- `moodle_stg.users` - User profiles
- `moodle_stg.courses` - Course catalog
- `moodle_stg.enrolments` - Student enrollments
- `moodle_stg.roles` - User roles
- `moodle_stg.grade_items` - Assessment items
- `moodle_stg.grades` - Student grades
- `moodle_stg.completions` - Course completion status

### Layer 3: Mart Tables (Aggregated)

- `moodle_mart.course_performance` - Student performance by course (Superset ready)

See `dags/sql/` directory for complete SQL schemas.

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 4 Moodle instances with Web Services enabled
- Moodle API tokens for each instance

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/cte-zl-ifrn/integration-moodle_elt.git
   cd integration-moodle_elt
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Moodle URLs and tokens
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Access Airflow UI**
   - URL: http://localhost:8080
   - Username: `admin`
   - Password: `admin` (change in `.env`)

5. **Access Superset**
   - URL: http://localhost:8088
   - Username: `admin`
   - Password: `admin`

6. **Configure Airflow Variables**
   
   In Airflow UI, go to Admin → Variables and add:
   - `moodle1_url` = `https://your-moodle1.com`
   - `moodle1_token` = `your_web_services_token`
   - Repeat for `moodle2`, `moodle3`, `moodle4`

7. **Create PostgreSQL Connection**
   
   In Airflow UI, go to Admin → Connections and add:
   - Connection ID: `postgres_moodle`
   - Connection Type: `Postgres`
   - Host: `postgres`
   - Schema: `airflow`
   - Login: `airflow`
   - Password: `airflow`
   - Port: `5432`

### Enable DAGs

In Airflow UI, enable the DAGs:
- `moodle1_elt`
- `moodle2_elt`
- `moodle3_elt`
- `moodle4_elt`

Each DAG runs daily at 2 AM by default. You can trigger manually for testing.

## 📁 Project Structure

```
.
├── dags/
│   ├── moodle1_dag.py          # DAG for Moodle instance 1
│   ├── moodle2_dag.py          # DAG for Moodle instance 2
│   ├── moodle3_dag.py          # DAG for Moodle instance 3
│   ├── moodle4_dag.py          # DAG for Moodle instance 4
│   ├── sql/
│   │   ├── 01_create_raw.sql           # Raw table schema
│   │   ├── 02_transform_users.sql      # User staging transform
│   │   ├── 03_transform_courses.sql    # Course staging transform
│   │   ├── 04_transform_enrolments.sql # Enrolment staging transform
│   │   ├── 05_transform_roles.sql      # Role staging transform
│   │   ├── 06_transform_grade_items.sql# Grade item staging transform
│   │   ├── 07_transform_grades.sql     # Grade staging transform
│   │   ├── 08_transform_completions.sql# Completion staging transform
│   │   └── 99_mart_performance.sql     # Mart aggregation
│   └── utils/
│       └── moodle_api.py       # Moodle API client library
├── docker-compose.yml          # Docker services configuration
├── init-db.sql                 # PostgreSQL initialization
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🔧 Configuration

### Moodle Web Services Setup

For each Moodle instance, enable Web Services:

1. **Enable Web Services**
   - Site Admin → Advanced Features → Enable web services: ✓

2. **Enable REST Protocol**
   - Site Admin → Plugins → Web Services → Manage Protocols → Enable REST

3. **Create Service**
   - Site Admin → Server → Web Services → External Services
   - Add new service: "Airflow ELT Integration"
   - Add required functions (see list above)

4. **Generate Token**
   - Site Admin → Server → Web Services → Manage Tokens
   - Create token for your integration user

### DAG Schedule

Default: Daily at 2 AM UTC (`0 2 * * *`)

Modify in each DAG file:
```python
schedule_interval='0 2 * * *'  # Cron expression
```

## 🛠️ Customization

### Adding New Entities

1. Add extraction function to DAG:
   ```python
   def extract_new_entity(**context):
       client = get_moodle_client()
       data = client._call_api('new_moodle_function')
       context['ti'].xcom_push(key='new_entity', value=data)
   ```

2. Create staging SQL transform: `dags/sql/XX_transform_new_entity.sql`

3. Add tasks to DAG and wire dependencies

### Modifying Mart Queries

Edit `dags/sql/99_mart_performance.sql` to customize aggregations for your dashboards.

## 🔍 Monitoring

### Airflow UI
- View DAG runs, task logs, and execution times
- Monitor failures and retry attempts

### PostgreSQL Queries
```sql
-- Check raw data ingestion
SELECT instance, entity, COUNT(*) as records, MAX(ts_extract) as last_extract
FROM moodle_raw
GROUP BY instance, entity
ORDER BY instance, entity;

-- Check staging table counts
SELECT 
  (SELECT COUNT(*) FROM moodle_stg.users) as users,
  (SELECT COUNT(*) FROM moodle_stg.courses) as courses,
  (SELECT COUNT(*) FROM moodle_stg.enrolments) as enrolments;

-- Check mart aggregation
SELECT instance, COUNT(*) as student_course_records
FROM moodle_mart.course_performance
GROUP BY instance;
```

## 🔐 Security Features

- ✅ Rate limiting (1s between API calls)
- ✅ Retry logic with exponential backoff
- ✅ UPSERT operations (deduplication via hash)
- ✅ JSON schema validation
- ✅ Connection pooling
- ✅ Timeout handling

## 🐛 Troubleshooting

### DAG Import Errors
```bash
docker-compose exec airflow-scheduler airflow dags list
docker-compose logs airflow-scheduler
```

### API Connection Issues
- Verify Moodle URLs are accessible
- Check API tokens are valid
- Ensure Web Services functions are enabled

### Database Connection Issues
```bash
docker-compose exec postgres psql -U airflow -d airflow -c "\dt moodle_raw*"
```

## 📚 Dependencies

- Apache Airflow 3.1+
- PostgreSQL 15+
- Moodle 4.5+
- Apache Superset (latest)

See `requirements.txt` for Python packages.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Moodle Community for Web Services documentation
- Apache Airflow team for the orchestration platform
- CKAN for data catalog capabilities
