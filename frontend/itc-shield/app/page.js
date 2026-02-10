"use client";
import { useState, useEffect } from "react";
import { useAuth } from "./context/AuthContext";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Test scenarios for quick testing
const TEST_SCENARIOS = [
  { label: "S1 - Cancelled", gstin: "01AABCU9603R1ZX", badge: "STOP" },
  { label: "S2 - Suspended", gstin: "02AABCU9603R1ZX", badge: "STOP" },
  { label: "S3 - Non-Filer", gstin: "03AABCU9603R1ZX", badge: "STOP" },
  { label: "H1 - Late Filer", gstin: "04AABCU9603R1ZX", badge: "HOLD" },
  { label: "H2 - New Vendor", gstin: "05AABCU9603R1ZX", badge: "HOLD" },
  { label: "H3 - Name Mismatch", gstin: "06AABCU9603R1ZX", badge: "HOLD" },
  { label: "R1 - Compliant", gstin: "33AABCU9603R1ZX", badge: "RELEASE" },
];

export default function Home() {
  const { user, isAuthenticated, logout, loading } = useAuth();
  const [gstin, setGstin] = useState("");
  const [checkLoading, setCheckLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const checkCompliance = async (gstinToCheck) => {
    const targetGstin = gstinToCheck || gstin;

    if (!targetGstin || targetGstin.length !== 15) {
      setError("Please enter a valid 15-character GSTIN");
      return;
    }

    setCheckLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/check_compliance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          gstin: targetGstin.toUpperCase(),
          amount: 100000,
          party_name: "Vendor Check",
        }),
      });

      if (!response.ok) {
        throw new Error("API request failed");
      }

      const data = await response.json();
      setResult(data);
      setGstin(targetGstin.toUpperCase());
    } catch (err) {
      setError("Failed to connect to server. Make sure the backend is running.");
      console.error(err);
    } finally {
      setCheckLoading(false);
    }
  };

  const handleScenarioClick = (scenario) => {
    setGstin(scenario.gstin);
    checkCompliance(scenario.gstin);
  };

  const getResultClass = () => {
    if (!result) return "";
    switch (result.decision) {
      case "STOP": return "result-stop";
      case "HOLD": return "result-hold";
      case "RELEASE": return "result-release";
      default: return "";
    }
  };

  const getIcon = () => {
    if (!result) return "";
    switch (result.decision) {
      case "STOP": return "🚫";
      case "HOLD": return "⚠️";
      case "RELEASE": return "✅";
      default: return "";
    }
  };

  return (
    <main className="container">
      {/* User Header Bar */}
      <div style={{
        display: "flex",
        justifyContent: "flex-end",
        alignItems: "center",
        padding: "1rem",
        gap: "1rem",
        borderBottom: "1px solid rgba(59, 130, 246, 0.2)",
        marginBottom: "1rem"
      }}>
        {isAuthenticated ? (
          <>
            <span style={{ color: "#94a3b8" }}>👤 {user?.name || user?.email}</span>
            <button
              onClick={logout}
              style={{
                padding: "0.5rem 1rem",
                background: "transparent",
                border: "1px solid #ef4444",
                color: "#ef4444",
                borderRadius: "6px",
                cursor: "pointer"
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link href="/login" style={{ color: "#60a5fa" }}>Login</Link>
            <Link href="/register" style={{
              padding: "0.5rem 1rem",
              background: "linear-gradient(135deg, #1e40af, #3b82f6)",
              color: "white",
              borderRadius: "6px",
              textDecoration: "none"
            }}>Sign Up</Link>
          </>
        )}
      </div>

      <header className="header">
        <h1>🛡️ TaxPay Guard</h1>
        <p>GST Vendor Compliance Check | Rule 37A Protection</p>
        <a href="/batch" style={{
          color: "#60a5fa",
          marginTop: "0.5rem",
          display: "inline-block",
          padding: "0.5rem 1rem",
          border: "1px solid #60a5fa",
          borderRadius: "6px"
        }}>
          📦 Batch Upload (Check 500+ Vendors)
        </a>
      </header>

      {/* GSTIN Check Form */}
      <div className="card">
        <div className="form-group">
          <label htmlFor="gstin">Enter Vendor GSTIN</label>
          <input
            id="gstin"
            type="text"
            maxLength={15}
            placeholder="e.g., 29AABCU9603R1ZX"
            value={gstin}
            onChange={(e) => setGstin(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === "Enter" && checkCompliance()}
          />
        </div>

        <button
          className="btn btn-primary"
          onClick={() => checkCompliance()}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Checking...
            </>
          ) : (
            <>
              🔍 Check Compliance
            </>
          )}
        </button>

        {error && (
          <p style={{ color: "var(--danger)", marginTop: "1rem", textAlign: "center" }}>
            {error}
          </p>
        )}
      </div>

      {/* Result Display */}
      {result && (
        <div className={`result-card ${getResultClass()}`}>
          <div className="result-icon">{getIcon()}</div>
          <div className="result-title">{result.title}</div>
          <div className="result-vendor">
            <strong>{result.vendor_name || "Unknown Vendor"}</strong>
            <br />
            GSTIN: {result.gstin}
          </div>
          <div className="result-message">{result.message}</div>
          <div className="result-meta">
            <span>📋 Rule: <strong>{result.rule_id}</strong></span>
            <span>⚡ Risk: <strong>{result.risk_level}</strong></span>
            <span>🕐 {result.timestamp}</span>
            <span>📊 Source: {result.data_source}</span>
          </div>
          {result.check_id && (
            <a
              href={`${API_URL}/certificate/${result.check_id}`}
              className="btn btn-download"
              style={{
                marginTop: "1rem",
                display: "inline-flex",
                alignItems: "center",
                gap: "0.5rem",
                background: "linear-gradient(135deg, #1e40af, #3b82f6)",
                color: "white",
                padding: "0.75rem 1.5rem",
                borderRadius: "8px",
                textDecoration: "none",
                fontWeight: "600"
              }}
            >
              📄 Download Certificate
            </a>
          )}
        </div>
      )}

      {/* Test Scenarios */}
      <div className="card">
        <h3 style={{ marginBottom: "1rem" }}>🧪 Test Scenarios</h3>
        <p style={{ color: "var(--text-muted)", marginBottom: "1rem" }}>
          Click any scenario to test the decision engine:
        </p>
        <div className="scenarios">
          {TEST_SCENARIOS.map((scenario) => (
            <div
              key={scenario.gstin}
              className="scenario-card"
              onClick={() => handleScenarioClick(scenario)}
            >
              <h4>
                <span className={`badge badge-${scenario.badge.toLowerCase()}`}>
                  {scenario.badge}
                </span>
                {" "}{scenario.label}
              </h4>
              <code>{scenario.gstin}</code>
            </div>
          ))}
        </div>
      </div>

      <footer className="footer">
        <p>TaxPay Guard v1.0 | Data shown is for demo purposes</p>
        <p style={{ marginTop: "0.5rem" }}>
          ⚠️ Connect real GSP API for production use
        </p>
      </footer>
    </main>
  );
}
