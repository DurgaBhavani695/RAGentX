# 2026-04-26-admin-configuration-apis-design.md

## Overview
Implement admin endpoints to manage system configuration dynamically.

## Architecture
- **Router**: `app/api/endpoints/admin.py`
- **Prefix**: `/admin`
- **Tags**: `["admin"]`

## Endpoints

### 1. GET /config
- **Path**: `/admin/config`
- **Method**: `GET`
- **Description**: Returns all current configuration settings.
- **Response**: JSON dictionary of settings.

### 2. PUT /config/{key}
- **Path**: `/admin/config/{key}`
- **Method**: `PUT`
- **Description**: Updates a specific configuration value.
- **Validation**:
    - Key must exist in the `Settings` model.
    - Value type should be validated (Pydantic handles this if we update the model).
- **Implementation**: Use `setattr(settings, key, value)` to update the in-memory singleton.

## Testing Strategy
- **File**: `tests/test_api_admin.py`
- **Framework**: `pytest` + `httpx.AsyncClient` (if using async) or `TestClient`.
- **Cases**:
    - `test_get_config`: Ensure it returns a 200 and a dictionary containing known keys like `PROJECT_NAME`.
    - `test_put_config_success`: Update a key (e.g., `PROJECT_NAME`) and verify it changed.
    - `test_put_config_invalid_key`: Attempt to update a non-existent key and expect a 404 or 422 error.

## Error Handling
- Return `404 Not Found` if the key does not exist.
- Return `422 Unprocessable Entity` if the value type is incorrect (FastAPI/Pydantic default).
