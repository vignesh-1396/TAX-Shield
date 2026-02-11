"use client";
import { useState, useEffect } from "react";
import { Loader2, CheckCircle, AlertCircle, FileText } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { useAuth } from "@/app/context/AuthContext";
import toast from "react-hot-toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function BatchStatus({ jobId, onComplete }) {
    const { session } = useAuth();
    const [status, setStatus] = useState("processing"); // processing, completed, failed
    const [stats, setStats] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!jobId) return;

        let intervalId;

        const checkStatus = async () => {
            try {
                const token = session?.access_token;
                if (!token) return; // Wait for auth

                const response = await fetch(`${API_URL}/api/v1/batch/status/${jobId}`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    throw new Error("Failed to fetch status");
                }

                const data = await response.json();

                if (data.status === "completed") {
                    setStatus("completed");
                    setStats(data);
                    clearInterval(intervalId);
                    if (onComplete) onComplete(data);
                } else if (data.status === "failed") {
                    setStatus("failed");
                    setError(data.error || "Batch processing failed");
                    clearInterval(intervalId);
                }
                // If processing, do nothing (continue polling)
            } catch (err) {
                console.error("Status check error:", err);
                // Don't set error state immediately to avoid flashing on transient failures
            }
        };

        // Check immediately
        checkStatus();

        // Poll every 3 seconds
        intervalId = setInterval(checkStatus, 3000);

        return () => clearInterval(intervalId);
    }, [jobId, session, onComplete]);

    if (status === "processing") {
        return (
            <Card className="p-6">
                <div className="flex flex-col items-center justify-center py-8 text-center space-y-4">
                    <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
                    <div>
                        <h3 className="text-lg font-medium text-gray-900">Processing Batch...</h3>
                        <p className="text-gray-500">Retrieving compliance data for your vendors</p>
                    </div>
                </div>
            </Card>
        );
    }

    if (status === "failed") {
        return (
            <Card className="p-6 border-red-200 bg-red-50">
                <div className="flex flex-col items-center justify-center py-8 text-center space-y-4">
                    <AlertCircle className="w-12 h-12 text-red-600" />
                    <div>
                        <h3 className="text-lg font-medium text-red-900">Processing Failed</h3>
                        <p className="text-red-700">{error}</p>
                    </div>
                </div>
            </Card>
        );
    }

    if (status === "completed" && stats) {
        return (
            <Card className="p-6 border-green-200 bg-green-50">
                <div className="flex flex-col items-center justify-center py-8 text-center space-y-4">
                    <CheckCircle className="w-12 h-12 text-green-600" />
                    <div>
                        <h3 className="text-lg font-medium text-green-900">Batch Completed</h3>
                        <p className="text-green-700">
                            Processed {stats.total_records} records.
                            Found {stats.risk_summary?.high_risk || 0} high risk vendors.
                        </p>
                    </div>
                    {/* Link to results or action button could go here */}
                </div>
            </Card>
        );
    }

    return null;
}
