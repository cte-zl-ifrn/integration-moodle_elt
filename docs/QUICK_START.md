# Quick Start Guide - Moodle ELT Integration

Get your Moodle ELT pipeline up and running in 15 minutes!

## Prerequisites Checklist

- [ ] Docker installed (version 20.10+)
- [ ] Docker Compose installed (version 2.0+)
- [ ] 4 Moodle instances accessible
- [ ] Moodle Web Services enabled on each instance
- [ ] API tokens generated for each instance

## Step-by-Step Setup

### 1️⃣ Clone & Configure (2 minutes)

```bash
# Clone the repository
git clone https://github.com/cte-zl-ifrn/integration-moodle_elt.git
cd integration-moodle_elt

# Create configuration file
cp .env.example .env

# Edit .env with your Moodle credentials
nano .env
# OR
vim .env
```

Update these variables in `.env`:
```env
moodle1_url=https://your-moodle1.com
moodle1_token=your_actual_token_here

moodle2_url=https://your-moodle2.com
moodle2_token=your_actual_token_here

moodle3_url=https://your-moodle3.com
moodle3_token=your_actual_token_here

moodle4_url=https://your-moodle4.com
moodle4_token=your_actual_token_here
```

### 2️⃣ Start Services (3 minutes)

```bash
# Run the setup script
./setup.sh

# Wait for services to start (2-3 minutes)
# Monitor startup progress
docker-compose logs -f
```

### 3️⃣ Configure Airflow (5 minutes)

**A. Access Airflow UI**
- Open browser: http://localhost:8080
- Login: `admin` / `admin`

**B. Add Moodle Variables**

Go to **Admin** → **Variables** and add:

| Key | Value |
|-----|-------|
| `moodle1_url` | `https://your-moodle1.com` |
| `moodle1_token` | `your_token_1` |
| `moodle2_url` | `https://your-moodle2.com` |
| `moodle2_token` | `your_token_2` |
| `moodle3_url` | `https://your-moodle3.com` |
| `moodle3_token` | `your_token_3` |
| `moodle4_url` | `https://your-moodle4.com` |
| `moodle4_token` | `your_token_4` |

**C. Configure PostgreSQL Connection**

Go to **Admin** → **Connections** and add:

| Field | Value |
|-------|-------|
| Connection ID | `postgres_moodle` |
| Connection Type | `Postgres` |
| Host | `postgres` |
| Schema | `airflow` |
| Login | `airflow` |
| Password | `airflow` |
| Port | `5432` |

Click **Test** then **Save**.

### 4️⃣ Enable & Run DAGs (3 minutes)

**A. Enable DAGs**

In Airflow UI, toggle these DAGs to **ON**:
- `moodle1_elt`
- `moodle2_elt`
- `moodle3_elt`
- `moodle4_elt`

**B. Trigger First Run**

Click the ▶️ play button on `moodle1_elt` to trigger manually.

Watch the progress in the **Graph** or **Grid** view.

### 5️⃣ Verify Data (2 minutes)

**Check Database**

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U airflow -d airflow

# Check raw data
SELECT instance, entity, COUNT(*) as records 
FROM moodle_raw 
GROUP BY instance, entity;

# Check staging data
SELECT COUNT(*) FROM moodle_stg.users;
SELECT COUNT(*) FROM moodle_stg.courses;

# Check mart data
SELECT instance, COUNT(*) as records 
FROM moodle_mart.course_performance 
GROUP BY instance;

# Exit
\q
```

### 6️⃣ Access Superset (Optional)

- Open browser: http://localhost:8088
- Login: `admin` / `admin`
- Add PostgreSQL database connection
- Create dashboards from `moodle_mart.course_performance`

## Verification Commands

```bash
# Check all services are running
docker-compose ps

# View Airflow logs
docker-compose logs airflow-scheduler
docker-compose logs airflow-webserver

# Check DAG status
docker-compose exec airflow-scheduler airflow dags list

# Test Moodle API connection
curl "https://your-moodle1.com/webservice/rest/server.php" \
  -d "wstoken=YOUR_TOKEN" \
  -d "wsfunction=core_webservice_get_site_info" \
  -d "moodlewsrestformat=json"
```

## Common Issues & Solutions

### Issue: Services won't start
**Solution:**
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Issue: DAG import errors
**Solution:**
```bash
# Check for Python syntax errors
docker-compose exec airflow-scheduler python -m py_compile /opt/airflow/dags/moodle1_dag.py

# View scheduler logs
docker-compose logs airflow-scheduler
```

### Issue: Can't connect to Moodle API
**Solution:**
1. Verify URL is correct (no trailing slash)
2. Test token with curl command above
3. Check Moodle Web Services are enabled
4. Verify API user has required capabilities

### Issue: PostgreSQL connection failed
**Solution:**
1. Check connection settings in Airflow
2. Verify postgres service is running: `docker-compose ps postgres`
3. Test connection: `docker-compose exec postgres pg_isready -U airflow`

## Next Steps

✅ **Schedule Configuration**
- DAGs run daily at 2 AM by default
- Modify schedule in each DAG file if needed

✅ **Monitor Performance**
- Check task execution times in Airflow UI
- Monitor PostgreSQL query performance

✅ **Create Dashboards**
- Use Superset to visualize `moodle_mart.course_performance`
- Create reports for stakeholders

✅ **Customize**
- Add more entities to extract
- Modify SQL transforms for your needs
- Create additional mart tables

## Support

- 📚 Full documentation: [README.md](../README.md)
- 🔧 API reference: [MOODLE_API_REFERENCE.md](MOODLE_API_REFERENCE.md)
- 🤝 Contributing: [CONTRIBUTING.md](../CONTRIBUTING.md)
- 📝 Changelog: [CHANGELOG.md](../CHANGELOG.md)

## Troubleshooting Resources

- Airflow docs: https://airflow.apache.org/docs/
- Moodle Web Services: https://docs.moodle.org/en/Using_web_services
- PostgreSQL docs: https://www.postgresql.org/docs/
- Docker Compose: https://docs.docker.com/compose/

---

**Success!** 🎉 Your Moodle ELT pipeline is now running!
