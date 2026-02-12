# GSP Provider Migration Guide

## Overview
Currently, the system is integrated with **Sandbox.co.in (Zoop)**. If you switch to another GSP (e.g., ClearTax, Masters India, Cygnet), you will need to update the following code.

## 1. Environment Variables (`.env`)
You will need to replace the Zoop keys with your new provider's keys.
```bash
# Remove these
# ZOOP_CLIENT_ID=...
# ZOOP_CLIENT_SECRET=...

# Add new provider keys
NEW_GSP_CLIENT_ID=...
NEW_GSP_CLIENT_SECRET=...
NEW_GSP_BASE_URL=...
```

## 2. Config File (`backend/app/config.py`)
Update the `Settings` class to read the new environment variables.

## 3. GSP Service Logic (`backend/app/services/gsp.py`)
This is where 90% of the changes will happen.

### A. Authentication (`_get_access_token`)
Different providers use different auth mechanisms.
*   **Current:** Custom Header Auth (`x-api-key`, `x-api-secret`).
*   **New Provider:** Might use OAuth2 (Bearer Token), Basic Auth, or Certificate-based auth.
*   **Action:** Rewrite `_get_access_token` to match the new provider's documentation.

### B. API Endpoints (`get_filing_history`)
*   **Current:** `.../gst/compliance/public/gstrs/track`
*   **New Provider:** Will have a completely different URL (e.g., `.../v1/returns/status`).
*   **Action:** Update the `track_url` variable.

### C. Response Parsing
*   **Current:**
    ```python
    outer_data = response_json.get("data", {})
    filed_list = inner_data.get("EFiledlist", [])
    ```
*   **New Provider:** The JSON structure will be different. You will need to inspect their response and update the parsing logic to extract:
    *   Return Type (`GSTR3B`, `GSTR1`)
    *   Filing Date
    *   Status (`Filed`, `Not Filed`)

## Summary Checklist
- [ ] Get API Documentation from new GSP.
- [ ] Update `.env` with new credentials.
- [ ] Create a new class `NewGSPProvider` in `gsp.py` (or modify `SandboxGSPProvider`).
- [ ] Implement `_get_access_token` for new auth.
- [ ] Implement `get_filing_history` mapping their JSON to our format.
