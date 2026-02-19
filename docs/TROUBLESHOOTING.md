# Troubleshooting Guide

Common issues and their solutions for the Moodle ELT Integration.

## Table of Contents
- [Service Issues](#service-issues)
- [DAG Issues](#dag-issues)
- [Database Issues](#database-issues)
- [API Connection Issues](#api-connection-issues)
- [Performance Issues](#performance-issues)

## Service Issues

### Services won't start

**Symptoms:** `docker-compose up` fails or services crash

**Solutions:**

1. Check Docker daemon is running:
   ```bash
   docker ps
   ```

2. Check port conflicts:
   ```bash
   # Check if ports are already in use
   lsof -i :8080  # Airflow
   lsof -i :5432  # PostgreSQL
   lsof -i :8088  # Superset
   ```

3. Check logs:
   ```bash
   docker-compose logs
   ```

4. Reset environment:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

### Airflow webserver won't start

**Symptoms:** Can't access http://localhost:8080

**Solutions:**

1. Check webserver logs:
   ```bash
   docker-compose logs airflow-webserver
   ```

2. Verify initialization completed:
   ```bash
   docker-compose logs airflow-init
   ```

3. Restart webserver:
   ```bash
   docker-compose restart airflow-webserver
   ```

## DAG Issues

### DAGs not appearing in UI

**Symptoms:** No DAGs visible in Airflow UI

**Solutions:**

1. Check DAG files syntax:
   ```bash
   docker-compose exec airflow-scheduler python -m py_compile /opt/airflow/dags/moodle1_dag.py
   ```

2. Check scheduler logs:
   ```bash
   docker-compose logs airflow-scheduler | grep -i error
   ```

3. List DAGs via CLI:
   ```bash
   docker-compose exec airflow-scheduler airflow dags list
   ```

4. Check file permissions:
   ```bash
   ls -la dags/
   ```

### DAG import errors

**Symptoms:** "Broken DAG" in Airflow UI

**Solutions:**

1. View detailed error:
   - Click on DAG name in UI
   - Look for red error message

2. Check Python dependencies:
   ```bash
   docker-compose exec airflow-scheduler pip list | grep -i postgres
   docker-compose exec airflow-scheduler pip list | grep -i requests
   ```

3. Test imports manually:
   ```bash
   docker-compose exec airflow-scheduler python -c "from dags.utils.moodle_api import MoodleAPIClient"
   ```

### Tasks failing

**Symptoms:** Red task boxes in DAG graph

**Solutions:**

1. Check task logs:
   - Click on task in graph view
   - Click "Log" button
   - Read error messages

2. Common task failures:

   **Extract tasks failing:**
   - Check Moodle Variables are set correctly
   - Verify API token is valid
   - Check Moodle API is accessible

   **Load tasks failing:**
   - Check PostgreSQL connection exists
   - Verify database permissions
   - Check for duplicate data

   **Transform tasks failing:**
   - Check SQL syntax in sql/ files
   - Verify source data exists in moodle_raw
   - Check for data type mismatches

## Database Issues

### Can't connect to PostgreSQL

**Symptoms:** "Connection refused" or "Could not connect"

**Solutions:**

1. Check PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   ```

2. Test connection:
   ```bash
   docker-compose exec postgres pg_isready -U airflow
   ```

3. Verify connection in Airflow:
   - Admin → Connections → postgres_moodle
   - Click "Test"

4. Check credentials in .env file

### Data not appearing in tables

**Symptoms:** Empty tables after DAG runs

**Solutions:**

1. Check raw data ingestion:
   ```sql
   SELECT instance, entity, COUNT(*) 
   FROM moodle_raw 
   GROUP BY instance, entity;
   ```

2. Check for errors in load tasks:
   ```bash
   docker-compose logs airflow-scheduler | grep -i "load_"
   ```

3. Verify extract tasks succeeded:
   - Check task status in Airflow UI
   - Check XCom values contain data

4. Check SQL transforms:
   ```bash
   # Run transform manually
   docker-compose exec postgres psql -U airflow -d airflow -f /path/to/transform.sql
   ```

### Duplicate key violations

**Symptoms:** "duplicate key value violates unique constraint"

**Solutions:**

1. Check UPSERT logic in SQL files
2. Verify hash_content deduplication
3. Manually clean duplicates:
   ```sql
   DELETE FROM moodle_raw 
   WHERE id NOT IN (
     SELECT MIN(id) 
     FROM moodle_raw 
     GROUP BY instance, entity, moodle_id, ts_extract
   );
   ```

## API Connection Issues

### Invalid token error

**Symptoms:** "Invalid token" from Moodle API

**Solutions:**

1. Regenerate token in Moodle:
   - Site Admin → Server → Web services → Manage tokens
   - Delete old token
   - Create new token
   - Update Airflow Variable

2. Verify token format (no spaces, correct length)

3. Test token directly:
   ```bash
   curl "https://your-moodle.com/webservice/rest/server.php" \
     -d "wstoken=YOUR_TOKEN" \
     -d "wsfunction=core_webservice_get_site_info" \
     -d "moodlewsrestformat=json"
   ```

### Function not available error

**Symptoms:** "This function is not available"

**Solutions:**

1. Add function to Web Service:
   - Site Admin → Server → Web services → External services
   - Edit "Airflow ELT Integration" service
   - Add missing function

2. Verify user has required capabilities

3. Check function name is correct in code

### Rate limiting / Timeout

**Symptoms:** "Connection timeout" or slow extractions

**Solutions:**

1. Increase timeout in moodle_api.py:
   ```python
   MoodleAPIClient(base_url=url, token=token, timeout=60)
   ```

2. Adjust rate limiting:
   ```python
   MoodleAPIClient(base_url=url, token=token, rate_limit_delay=2.0)
   ```

3. Add retry logic in DAG:
   ```python
   default_args = {
       'retries': 3,
       'retry_delay': timedelta(minutes=5)
   }
   ```

### SSL certificate errors

**Symptoms:** "SSL: CERTIFICATE_VERIFY_FAILED"

**Solutions:**

1. For development only (NOT production):
   ```python
   import urllib3
   urllib3.disable_warnings()
   ```

2. Proper solution - install CA certificates:
   ```bash
   # Update CA certificates in Docker container
   docker-compose exec airflow-scheduler update-ca-certificates
   ```

## Performance Issues

### Slow DAG execution

**Symptoms:** DAG takes hours to complete

**Solutions:**

1. Check parallel execution:
   - Review task dependencies in graph
   - Ensure independent tasks run in parallel

2. Optimize API calls:
   - Reduce rate_limit_delay if Moodle allows
   - Batch requests where possible

3. Database optimization:
   ```sql
   -- Add indexes
   CREATE INDEX CONCURRENTLY idx_moodle_raw_lookup 
   ON moodle_raw(instance, entity, moodle_id);
   
   -- Analyze tables
   ANALYZE moodle_raw;
   ANALYZE moodle_stg.users;
   ```

4. Check for bottlenecks:
   ```bash
   # Monitor task duration in Airflow UI
   # Check which tasks are slowest
   ```

### Database running out of space

**Symptoms:** "No space left on device"

**Solutions:**

1. Clean old data:
   ```sql
   -- Delete data older than 90 days
   DELETE FROM moodle_raw 
   WHERE ts_extract < NOW() - INTERVAL '90 days';
   ```

2. Monitor database size:
   ```sql
   SELECT 
     pg_size_pretty(pg_database_size('airflow')) as db_size;
   ```

3. Increase Docker volume size:
   ```bash
   docker volume inspect integration-moodle_elt_postgres-db-volume
   ```

### Memory issues

**Symptoms:** Tasks killed by OOM killer

**Solutions:**

1. Increase Docker memory limits in docker-compose.yml:
   ```yaml
   services:
     airflow-scheduler:
       mem_limit: 4g
   ```

2. Process data in smaller batches:
   ```python
   # Instead of loading all at once
   for batch in chunks(data, 1000):
       process_batch(batch)
   ```

## Monitoring Commands

```bash
# Check all services status
docker-compose ps

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f airflow-scheduler
docker-compose logs -f postgres

# Check DAG status
docker-compose exec airflow-scheduler airflow dags list

# Check database connections
docker-compose exec postgres psql -U airflow -c "SELECT * FROM pg_stat_activity;"

# Monitor resource usage
docker stats
```

## Getting Help

If you can't resolve the issue:

1. Check [GitHub Issues](https://github.com/cte-zl-ifrn/integration-moodle_elt/issues)
2. Review [Airflow documentation](https://airflow.apache.org/docs/)
3. Check [Moodle Web Services docs](https://docs.moodle.org/en/Using_web_services)
4. Open a new issue with:
   - Clear description of problem
   - Steps to reproduce
   - Relevant logs
   - Environment details
