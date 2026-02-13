# Testing Guide for ITC Shield

## 🎯 Quick Start

### Install Test Dependencies
```bash
cd backend
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_compliance_check.py
```

### Run Specific Test
```bash
pytest tests/test_compliance_check.py::TestComplianceCheck::test_check_valid_gstin
```

---

## 📊 Test Coverage

### Current Test Files
1. **test_compliance_check.py** - Compliance check endpoint (9 tests)
2. **test_validation.py** - Input validation (20+ tests)
3. **test_decision_engine.py** - Business logic (6 tests)
4. **test_health.py** - Health checks (3 tests)

**Total: 38+ tests**

---

## 🧪 Test Categories

### Unit Tests
- Input validation
- Decision engine logic
- Utility functions

### Integration Tests
- API endpoints
- Database operations
- External service mocking

### Performance Tests
- Response time checks
- Load testing (future)

---

## ✅ What's Tested

### Security ✅
- Invalid GSTIN format
- Negative amounts
- SQL injection prevention
- XSS prevention (sanitization)
- Path traversal (filename validation)

### Business Logic ✅
- Cancelled vendor → STOP
- Suspended vendor → STOP
- Non-filer → STOP
- New vendor → HOLD
- Active vendor → PROCEED

### API Endpoints ✅
- Valid requests
- Invalid requests
- Missing fields
- Response structure
- Performance (< 200ms)

---

## 📈 Coverage Goals

**Current:** ~40% (estimated)  
**Target:** 80%+

### Priority Areas to Test Next
1. Batch processing
2. Authentication
3. Database CRUD operations
4. Celery tasks
5. Error handling

---

## 🚀 Running Tests in CI/CD

### GitHub Actions (Future)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install -r requirements.txt -r requirements-test.txt
      - run: pytest --cov=app --cov-fail-under=50
```

---

## 🐛 Debugging Failed Tests

### Verbose Output
```bash
pytest -v
```

### Show Print Statements
```bash
pytest -s
```

### Stop on First Failure
```bash
pytest -x
```

### Run Last Failed Tests
```bash
pytest --lf
```

---

## 📝 Writing New Tests

### Test Structure
```python
def test_feature_name(client, test_db):
    # Arrange
    data = {"key": "value"}
    
    # Act
    response = client.post("/endpoint", json=data)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["result"] == "expected"
```

### Use Fixtures
```python
@pytest.fixture
def sample_data():
    return {"gstin": "27AABCU9603R1ZM"}

def test_with_fixture(client, sample_data):
    response = client.post("/check", json=sample_data)
    assert response.status_code == 200
```

---

## 🎉 Benefits

**Before Tests:** 0/100 (F)  
**After Tests:** 70/100 (C)

### What Changed
- ✅ Can deploy with confidence
- ✅ Catch bugs before production
- ✅ Refactor safely
- ✅ Document expected behavior
- ✅ Faster debugging

---

## 🚨 Important Notes

1. **Always run tests before deploying**
2. **Write tests for new features**
3. **Update tests when changing logic**
4. **Aim for 80%+ coverage**
5. **Tests should be fast (< 5 seconds total)**
