# 🔧 TALLY TDL SAAS INTEGRATION - IMPLEMENTATION GUIDE

## 📋 Overview

This guide provides step-by-step instructions for deploying the **ITC Shield SaaS Integration** TDL plugin in Tally Prime/ERP9.

**File:** `ITCShield_SaaS_Integration.TDL`  
**Version:** 2.0  
**Lines of Code:** 400+  
**Features:** HTTP API calls, JSON parsing, Auto-check, Manual check, Settings UI

---

## 🎯 What This TDL Does

### Automatic Compliance Checking
- **Triggers:** When saving Payment/Journal/Receipt vouchers
- **Checks:** Vendor GSTIN against ITC Shield API
- **Actions:** STOP (block), HOLD (warn), PROCEED (allow)

### Manual Compliance Checking
- **Menu:** Gateway of Tally → ITC Shield
- **Features:** Check any vendor manually, view history, configure settings

### Real-Time Integration
- **API Calls:** HTTP POST to your SaaS backend
- **Authentication:** Bearer token (API key)
- **Response:** JSON with decision, risk level, reason

---

## 📦 STEP 1: Prerequisites

### System Requirements
- ✅ Tally Prime (any version) OR Tally ERP 9.6+
- ✅ Windows 7/10/11
- ✅ Internet connection
- ✅ ITC Shield API key (from your SaaS dashboard)

### Before You Start
1. **Get API Key:**
   - Login to ITC Shield dashboard
   - Go to Settings → API Keys
   - Generate new API key
   - Copy the key (you'll need it in Step 3)

2. **Note Your API URL:**
   - Production: `https://api.itcshield.com/api/v1/compliance/check`
   - Staging: `https://staging-api.itcshield.com/api/v1/compliance/check`
   - Local: `http://localhost:8000/api/v1/compliance/check`

---

## 📥 STEP 2: Install TDL File

### Option A: Automatic Installation (Recommended)

1. **Copy TDL File:**
   ```
   Source: e:\Startup IDea\ITC_Protection_System\tally_plugin\ITCShield_SaaS_Integration.TDL
   
   Destination (Tally Prime):
   C:\Users\[YourUsername]\AppData\Local\Tally Solutions\Tally.ERP9\TDL
   
   OR (Tally ERP 9):
   C:\Program Files\Tally.ERP9\TDL
   ```

2. **Restart Tally**

3. **Enable TDL:**
   - Press `F12` (Configure)
   - Go to `TDL & Add-Ons`
   - Select `ITCShield_SaaS_Integration.TDL`
   - Set to `Yes`
   - Press `Ctrl+A` to accept

### Option B: Manual Load

1. **Open Tally**
2. Press `F12` → `TDL Configuration`
3. Click `Load TDL on Demand`
4. Browse to `ITCShield_SaaS_Integration.TDL`
5. Select and load

---

## ⚙️ STEP 3: Configure API Settings

### Method 1: Edit TDL File (Before Installation)

Open `ITCShield_SaaS_Integration.TDL` in Notepad and update:

```tdl
[#Variable]
    ;; CHANGE THESE VALUES
    ITCShield_API_URL    : String : "https://api.itcshield.com/api/v1/compliance/check"
    ITCShield_API_Key    : String : "YOUR_API_KEY_HERE"
    ITCShield_MinAmount  : Number : 50000
```

**Replace:**
- `YOUR_API_KEY_HERE` → Your actual API key from Step 1
- `50000` → Minimum amount to trigger check (in rupees)

### Method 2: Use Settings Form (After Installation)

1. Open Tally
2. Press `Alt+I` (ITC Shield menu)
3. Select `Settings`
4. Update:
   - API URL
   - API Key
   - Minimum Amount
   - Auto-check toggle
5. Click `Save`
6. Click `Test Connection` to verify

---

## 🧪 STEP 4: Test the Integration

### Test 1: Connection Test

1. Open Tally
2. Press `Alt+I`
3. Select `Settings`
4. Click `Test Connection`
5. **Expected:** "Connection Successful" message

**If Failed:**
- Check internet connection
- Verify API URL is correct
- Verify API key is valid
- Check firewall settings

### Test 2: Manual Compliance Check

1. Press `Alt+I`
2. Select `Check Vendor Compliance`
3. Enter:
   - GSTIN: `27AABCU9603R1ZM` (test GSTIN)
   - Amount: `50000`
4. Click `Check Compliance`
5. **Expected:** Popup showing compliance result

**Possible Results:**
- ✅ PROCEED - Vendor Verified
- ⚠️ HOLD - Review Required
- ❌ STOP - Do Not Proceed

### Test 3: Auto-Check on Voucher

1. Go to `Accounting Vouchers` → `Payment` (F5)
2. Select a vendor with GSTIN
3. Enter amount > ₹50,000
4. Press `Ctrl+A` to save
5. **Expected:** Compliance check runs automatically
6. **Result:** Popup shows decision

**Test Scenarios:**

| Vendor Status | Expected Result |
|--------------|-----------------|
| Active, Good Filing | PROCEED |
| Active, Poor Filing | HOLD |
| Cancelled/Suspended | STOP |
| No GSTIN | Warning message |

---

## 🔧 STEP 5: Customization Options

### Adjust Minimum Amount Threshold

**Edit in TDL:**
```tdl
ITCShield_MinAmount : Number : 100000  ;; Change to 1 lakh
```

**Or in Settings UI:**
- Alt+I → Settings → Minimum Amount → 100000

### Disable Auto-Check

**Edit in TDL:**
```tdl
ITCShield_AutoCheck : Logical : No
```

**Or in Settings UI:**
- Alt+I → Settings → Auto-Check on Voucher → No

### Change Voucher Types

**Edit in TDL (lines 85-90):**
```tdl
;; Add more voucher types
[#Form: Contra]
    On : Form Accept : Yes : Call : ITCShield_OnVoucherSave

[#Form: Sales]
    On : Form Accept : Yes : Call : ITCShield_OnVoucherSave
```

### Customize Popup Messages

**Edit in TDL (lines 260-280):**
```tdl
Set : ResultMsg : "🚫 PAYMENT BLOCKED" + $$NewLine
Set : ResultMsg : ##ResultMsg + "Contact CFO for approval"
```

---

## 📊 STEP 6: Monitor & Logs

### View Transaction Logs

**Log File Location:**
```
C:\Users\[YourUsername]\AppData\Local\Tally Solutions\Tally.ERP9\ITCShield_Log.txt
```

**Log Format:**
```
2026-02-12 10:30:45 | GSTIN: 27AABCU9603R1ZM | Amount: 50000 | Decision: PROCEED | Risk: LOW
2026-02-12 10:35:22 | GSTIN: 29AABCT1332L1ZV | Amount: 75000 | Decision: HOLD | Risk: MEDIUM
```

### Enable/Disable Logging

**Edit in TDL:**
```tdl
ITCShield_LogEnabled : Logical : Yes  ;; Set to No to disable
```

---

## 🐛 STEP 7: Troubleshooting

### Issue 1: TDL Not Loading

**Symptoms:** No ITC Shield menu appears

**Solutions:**
1. Check TDL file location
2. Verify TDL is enabled in F12 → TDL Configuration
3. Restart Tally
4. Check for syntax errors in TDL file

### Issue 2: API Connection Failed

**Symptoms:** "Connection Failed" or "Unable to reach API"

**Solutions:**
1. Check internet connection
2. Verify API URL is correct (no trailing slash)
3. Check firewall/antivirus blocking Tally
4. Verify API key is valid
5. Test API manually with Postman

### Issue 3: GSTIN Not Found

**Symptoms:** "No GSTIN found for this vendor"

**Solutions:**
1. Open Ledger Master (Alt+G → Ledgers)
2. Select vendor ledger
3. Go to `Statutory Details`
4. Add GSTIN under `GST Registration Details`
5. Save and retry

### Issue 4: Auto-Check Not Triggering

**Symptoms:** Voucher saves without compliance check

**Solutions:**
1. Check `ITCShield_AutoCheck` is set to `Yes`
2. Verify amount is above minimum threshold
3. Confirm vendor has GSTIN
4. Check voucher type is Payment/Journal/Receipt
5. Restart Tally

### Issue 5: JSON Parsing Error

**Symptoms:** Incorrect decision displayed

**Solutions:**
1. Check API response format matches expected JSON
2. Verify API returns: `decision`, `risk_level`, `reason`, `vendor_name`
3. Test API response with Postman
4. Check for special characters in response

---

## 🔒 STEP 8: Security Best Practices

### Protect API Key

1. **Never commit API key to git**
   - Add to `.gitignore`: `*.TDL`
   
2. **Use environment-specific keys**
   - Development: `dev_api_key_xxx`
   - Production: `prod_api_key_xxx`

3. **Rotate keys regularly**
   - Every 90 days
   - After employee departure
   - If compromised

### Secure TDL File

1. **Set file permissions:**
   - Right-click TDL file → Properties
   - Security → Edit
   - Remove write access for non-admins

2. **Backup TDL file:**
   - Keep copy in secure location
   - Version control (without API key)

---

## 📈 STEP 9: Performance Optimization

### Reduce API Calls

**Cache Results (Future Enhancement):**
```tdl
;; Check if GSTIN was checked in last 24 hours
;; If yes, use cached result
;; If no, make API call
```

### Timeout Configuration

**Adjust timeout (currently 10 seconds):**
```tdl
ITCShield_Timeout : Number : 5  ;; Reduce to 5 seconds
```

### Async Processing (Advanced)

For large volumes, consider:
1. Queue checks in background
2. Process during off-peak hours
3. Batch multiple checks

---

## 🚀 STEP 10: Deployment Checklist

### Pre-Deployment
- [ ] API key obtained
- [ ] API URL configured
- [ ] TDL file tested locally
- [ ] Connection test passed
- [ ] Manual check tested
- [ ] Auto-check tested
- [ ] Logging verified

### Deployment
- [ ] Copy TDL to production Tally
- [ ] Enable TDL in F12
- [ ] Configure settings
- [ ] Test connection
- [ ] Train users
- [ ] Monitor logs

### Post-Deployment
- [ ] Monitor API usage
- [ ] Check error logs
- [ ] Collect user feedback
- [ ] Optimize performance
- [ ] Update documentation

---

## 📞 Support & Resources

### Documentation
- **API Docs:** https://api.itcshield.com/docs
- **TDL Reference:** Tally Help → TDL Reference
- **Video Tutorial:** [Link to be added]

### Support Channels
- **Email:** support@itcshield.com
- **Phone:** +91-XXXX-XXXXXX
- **Chat:** https://itcshield.com/support

### Common Questions

**Q: Can I use this with Tally on Cloud?**
A: Yes, but TDL must be installed on each client machine.

**Q: Does this work offline?**
A: No, internet connection required for API calls. Offline mode coming soon.

**Q: Can I customize the decision logic?**
A: Decision logic is on the server side. Contact support for custom rules.

**Q: How many API calls per month?**
A: Depends on your subscription plan. Check dashboard for usage.

---

## 🎉 Success Criteria

You've successfully integrated ITC Shield when:

✅ Alt+I opens ITC Shield menu  
✅ Test connection succeeds  
✅ Manual check returns results  
✅ Auto-check triggers on voucher save  
✅ STOP decision blocks voucher  
✅ HOLD decision shows warning  
✅ PROCEED decision allows save  
✅ Logs are being written  

**Congratulations! Your Tally is now integrated with ITC Shield SaaS!** 🚀

---

## 📋 Quick Reference Card

### Keyboard Shortcuts
- `Alt+I` - Open ITC Shield menu
- `F12` - Tally configuration
- `Ctrl+A` - Save voucher (triggers check)

### Menu Path
Gateway of Tally → ITC Shield → [Option]

### File Locations
- **TDL:** `C:\Users\[User]\AppData\Local\Tally Solutions\Tally.ERP9\TDL\`
- **Logs:** `C:\Users\[User]\AppData\Local\Tally Solutions\Tally.ERP9\ITCShield_Log.txt`

### API Endpoints
- **Check:** `/api/v1/compliance/check`
- **History:** `/api/v1/compliance/history`
- **Health:** `/api/v1/health`

---

**Last Updated:** 2026-02-12  
**Version:** 2.0  
**Author:** ITC Shield Team
