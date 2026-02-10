"use client";
import { useState, useRef } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function BatchPage() {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.name.endsWith('.csv')) {
            setFile(selectedFile);
            setError("");
        } else {
            setError("Please select a CSV file");
            setFile(null);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError("Please select a file first");
            return;
        }

        setUploading(true);
        setError("");
        setResult(null);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch(`${API_URL}/api/v1/batch/upload`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail?.message || data.detail || "Upload failed");
            }

            setResult(data);
        } catch (err) {
            setError(err.message || "Failed to upload batch");
            console.error(err);
        } finally {
            setUploading(false);
        }
    };

    const getStatusColor = () => {
        if (!result) return "";
        switch (result.status) {
            case "COMPLETED": return "#22c55e";
            case "PROCESSING": return "#f59e0b";
            case "FAILED": return "#ef4444";
            default: return "#3b82f6";
        }
    };

    return (
        <main className="container">
            <header className="header">
                <h1>📦 Batch Upload</h1>
                <p>Check multiple vendors at once via CSV upload</p>
                <Link href="/" style={{ color: "#60a5fa", marginTop: "0.5rem", display: "inline-block" }}>
                    ← Back to Single Check
                </Link>
            </header>

            {/* Upload Section */}
            <div className="card">
                <h3 style={{ marginBottom: "1rem" }}>📄 Upload Vendor CSV</h3>

                <div
                    className="dropzone"
                    onClick={() => fileInputRef.current?.click()}
                    style={{
                        border: "2px dashed #3b82f6",
                        borderRadius: "12px",
                        padding: "2rem",
                        textAlign: "center",
                        cursor: "pointer",
                        background: file ? "rgba(59, 130, 246, 0.1)" : "transparent",
                        transition: "all 0.3s ease"
                    }}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".csv"
                        onChange={handleFileChange}
                        style={{ display: "none" }}
                    />
                    {file ? (
                        <>
                            <div style={{ fontSize: "2rem" }}>✅</div>
                            <p style={{ fontWeight: "600" }}>{file.name}</p>
                            <p style={{ color: "var(--text-muted)" }}>
                                {(file.size / 1024).toFixed(1)} KB
                            </p>
                        </>
                    ) : (
                        <>
                            <div style={{ fontSize: "2rem" }}>📁</div>
                            <p>Drop CSV file here or click to browse</p>
                            <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
                                Required columns: GSTIN, Vendor Name, Amount
                            </p>
                        </>
                    )}
                </div>

                <button
                    className="btn btn-primary"
                    onClick={handleUpload}
                    disabled={!file || uploading}
                    style={{ marginTop: "1rem", width: "100%" }}
                >
                    {uploading ? (
                        <>
                            <span className="spinner"></span>
                            Processing batch...
                        </>
                    ) : (
                        <>🚀 Start Batch Processing</>
                    )}
                </button>

                {error && (
                    <p style={{ color: "var(--danger)", marginTop: "1rem", textAlign: "center" }}>
                        ❌ {error}
                    </p>
                )}
            </div>

            {/* Results Section */}
            {result && (
                <div className="card" style={{ borderLeft: `4px solid ${getStatusColor()}` }}>
                    <h3 style={{ marginBottom: "1rem" }}>
                        {result.status === "COMPLETED" ? "✅" : "⏳"} Batch Result
                    </h3>

                    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", marginBottom: "1rem" }}>
                        <div className="stat-card">
                            <div className="stat-value">{result.total || 0}</div>
                            <div className="stat-label">Total</div>
                        </div>
                        <div className="stat-card" style={{ borderColor: "#22c55e" }}>
                            <div className="stat-value" style={{ color: "#22c55e" }}>{result.success || 0}</div>
                            <div className="stat-label">Success</div>
                        </div>
                        <div className="stat-card" style={{ borderColor: "#ef4444" }}>
                            <div className="stat-value" style={{ color: "#ef4444" }}>{result.failed || 0}</div>
                            <div className="stat-label">Failed</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{result.progress_percent || 100}%</div>
                            <div className="stat-label">Progress</div>
                        </div>
                    </div>

                    {result.status === "COMPLETED" && result.job_id && (
                        <a
                            href={`${API_URL}/api/v1/batch/download/${result.job_id}`}
                            className="btn btn-download"
                            style={{
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "0.5rem",
                                background: "linear-gradient(135deg, #1e40af, #3b82f6)",
                                color: "white",
                                padding: "1rem 2rem",
                                borderRadius: "8px",
                                textDecoration: "none",
                                fontWeight: "600",
                                width: "100%",
                                justifyContent: "center"
                            }}
                        >
                            📥 Download All Certificates (ZIP)
                        </a>
                    )}

                    {result.parse_errors && result.parse_errors.length > 0 && (
                        <div style={{ marginTop: "1rem", padding: "1rem", background: "rgba(239, 68, 68, 0.1)", borderRadius: "8px" }}>
                            <strong>⚠️ CSV Errors:</strong>
                            <ul style={{ margin: "0.5rem 0 0 1rem" }}>
                                {result.parse_errors.map((err, i) => (
                                    <li key={i} style={{ color: "#f87171" }}>{err}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {/* CSV Template */}
            <div className="card">
                <h3 style={{ marginBottom: "1rem" }}>📋 CSV Template</h3>
                <p style={{ color: "var(--text-muted)", marginBottom: "1rem" }}>
                    Your CSV should have the following format:
                </p>
                <pre style={{
                    background: "#1e293b",
                    padding: "1rem",
                    borderRadius: "8px",
                    overflow: "auto",
                    fontSize: "0.875rem"
                }}>
                    {`GSTIN,Vendor Name,Amount
33AABCU9603R1ZX,Good Vendor Pvt Ltd,50000
27AADCB2230M1Z5,Another Supplier,75000
29AABCT1234F1ZP,Test Company Ltd,100000`}
                </pre>
            </div>

            <footer className="footer">
                <p>TaxPay Guard v1.0 | Batch Processing Module</p>
            </footer>

            <style jsx>{`
        .stat-card {
          background: rgba(30, 64, 175, 0.1);
          border: 1px solid rgba(59, 130, 246, 0.3);
          border-radius: 8px;
          padding: 1rem;
          text-align: center;
        }
        .stat-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: #60a5fa;
        }
        .stat-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-transform: uppercase;
        }
      `}</style>
        </main>
    );
}
