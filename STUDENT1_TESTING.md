# Student 1 Implementation - Testing & Next Steps

## ✅ What We Just Built

You now have a **fully functional Student 1 Input Layer** with:

1. **Database Connection** (`database.py`) - PostgreSQL connection pooling
2. **ORM Models** (`models.py`) - Asset, Event, SBOM, GoldenBaseline tables
3. **Pydantic Schemas** (`schemas.py`) - Request/response validation
4. **Event Collector** - Real event ingestion & querying
5. **Asset Management** - Full CRUD for assets
6. **SBOM Generator** - Component tracking (stub for phase 2)
7. **Drift Detection** - Golden baseline comparison

---

## 🚀 How to Test Student 1

### Option 1: Run Locally (Fast Testing)

**Prerequisites:**
- PostgreSQL running on localhost:5432
- Python 3.11+
- Virtual environment

**Steps:**

```bash
# 1. Navigate to student-1-input-layer
cd c:\Users\User\Desktop\Sentry\project-sentinel\student-1-input-layer

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start PostgreSQL (ensure .env has correct credentials)
# Update DATABASE_URL in database.py if needed

# 5. Run the server
python main.py
```

**Server will start at:** http://localhost:8000

**API Documentation:** http://localhost:8000/docs (Swagger UI)

---

### Option 2: Run with Docker Compose (Recommended)

**Steps:**

```bash
# 1. Update .env file
cp .env.example .env
# Edit .env with secure password

# 2. Start only PostgreSQL + Student 1
docker-compose up -d postgres
docker-compose up -d student-1-event-collector
```

**Wait for health check:**
```bash
curl http://localhost:8001/health
```

**API Documentation:** http://localhost:8001/docs

---

## 📝 Test Scenarios (Using curl)

### 1. Create an Asset

```bash
curl -X POST http://localhost:8001/api/v1/discovery/assets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-server-01",
    "ip_address": "192.168.1.100",
    "hostname": "web-server-01.local",
    "os_type": "Ubuntu Linux 22.04",
    "asset_type": "server",
    "asset_criticality": 8,
    "owner_team": "Platform Team"
  }'
```

**Expected:** Returns asset with UUID (copy the `id` for next steps)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "web-server-01",
  "ip_address": "192.168.1.100",
  ...
}
```

---

### 2. List All Assets

```bash
curl http://localhost:8001/api/v1/discovery/assets
```

**Expected:** 
```json
{
  "total": 1,
  "assets": [...]
}
```

---

### 3. Ingest a Security Event

Replace `ASSET_ID` with the UUID from step 1:

```bash
curl -X POST http://localhost:8001/api/v1/events/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "ASSET_ID",
    "event_type": "Auth",
    "source_ip": "203.0.113.5",
    "user_id": "john.doe",
    "action": "login",
    "status": "success",
    "severity": 5,
    "raw_data": {"mfa": "enabled", "duration_ms": 1234}
  }'
```

**Expected:** Event saved with UUID

---

### 4. List Events (All)

```bash
curl http://localhost:8001/api/v1/events/
```

---

### 5. List Events (Filtered)

```bash
# Filter by event type
curl "http://localhost:8001/api/v1/events/?event_type=Auth&limit=10"

# Filter by user
curl "http://localhost:8001/api/v1/events/?user_id=john.doe"

# Filter by severity
curl "http://localhost:8001/api/v1/events/?severity_min=5&severity_max=10"
```

---

### 6. Get Events for Specific Asset

Replace `ASSET_ID`:

```bash
curl "http://localhost:8001/api/v1/discovery/assets/ASSET_ID/events"
```

---

### 7. Create Golden Baseline

```bash
curl -X POST http://localhost:8001/api/v1/drift/baseline/ASSET_ID \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "ASSET_ID",
    "file_hash": "abc123def456...",
    "config_hash": "xyz789...",
    "created_by": "admin"
  }'
```

---

### 8. Check Drift Against Baseline

```bash
curl -X POST http://localhost:8001/api/v1/drift/check/ASSET_ID \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "ASSET_ID",
    "current_file_hash": "abc123def456...",
    "current_config_hash": "different_hash"
  }'
```

**Expected:** `drift_detected: true` if hashes don't match

---

## 📊 Verify Database Persistence

Connect to PostgreSQL and verify data was saved:

```bash
# Connect to database
docker-compose exec postgres psql -U sentinel_user -d sentinel

# List assets
SELECT id, name, ip_address, asset_criticality FROM assets;

# List events
SELECT id, event_type, action, status, created_at FROM events LIMIT 10;

# Check baselines
SELECT asset_id, baseline_time FROM golden_baseline;
```

---

## 🔧 Next Steps

### Phase 2: Implement Remaining Modules

**Priority 1: Student 3 (Intelligence Layer)** (~2 hours)
- Implement risk scoring engine
- Add basic AI advisory
- Create playbook library

**Priority 2: Student 2 (Enrichment Layer)** (~3 hours)
- GeoIP engine with MaxMind
- Basic MITRE ATT&CK mapping
- CTI indicator checking

**Priority 3: Frontend Dashboard** (~4 hours)
- React components
- Real-time WebSocket
- Risk visualization

---

## 🐛 Troubleshooting

### Database Connection Error

**Error:** `psycopg2.OperationalError: could not connect to server`

**Fix:**
1. Verify PostgreSQL is running: `docker-compose ps postgres`
2. Check DATABASE_URL in `.env`
3. Ensure credentials are correct

### Port Already in Use

**Error:** `Address already in use (:8001)`

**Fix:**
```bash
# Change port in docker-compose.yml
ports:
  - "8011:8000"  # Changed from 8001
```

### Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'src'`

**Fix:**
```bash
# Ensure you're in student-1-input-layer directory
cd student-1-input-layer

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📋 Checklist

- [ ] Student 1 server running
- [ ] Create asset successfully
- [ ] List assets works
- [ ] Ingest 5+ events
- [ ] Filter events by type/user
- [ ] Get asset-specific events
- [ ] Create baseline
- [ ] Check drift detection
- [ ] Verify data in PostgreSQL
- [ ] Test Swagger UI documentation

---

## 🎯 Success Criteria

Student 1 is **production-ready** when:
✅ All CRUD operations work
✅ Database persistence verified
✅ Error handling working
✅ API documentation complete
✅ 5+ test events in database
✅ Zero connection errors

---

**Ready to test? Start with Option 2 (Docker) - it's the fastest!** 🚀
