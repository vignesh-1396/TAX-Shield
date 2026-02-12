"use client";
import { useState } from "react";
import { Shield, CheckCircle, XCircle, Loader2, AlertCircle } from "lucide-react";
import Card, { CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import toast from "react-hot-toast";
import { api } from "@/services/api";

const STEPS = {
    DISCONNECTED: "disconnected",
    REQUESTING_OTP: "requesting_otp",
    VERIFYING_OTP: "verifying_otp",
    CONNECTED: "connected",
    SYNCING: "syncing"
};

export default function ConnectGST() {
    const [step, setStep] = useState(STEPS.DISCONNECTED);
    const [gstin, setGstin] = useState("");
    const [otp, setOtp] = useState("");
    const [transactionId, setTransactionId] = useState("");
    const [connectionStatus, setConnectionStatus] = useState(null);
    const [loading, setLoading] = useState(false);

    // Request OTP
    const handleRequestOTP = async () => {
        if (!gstin || gstin.length !== 15) {
            toast.error("Please enter a valid 15-digit GSTIN");
            return;
        }

        setLoading(true);
        setStep(STEPS.REQUESTING_OTP);

        try {
            const response = await api.post("/gst/connect", {
                gstin: gstin.toUpperCase(),
                username: gstin.toUpperCase()
            });

            setTransactionId(response.transaction_id);
            setStep(STEPS.VERIFYING_OTP);
            toast.success("OTP sent to your registered mobile number");
        } catch (error) {
            console.error("OTP request failed:", error);
            toast.error(error.response?.data?.detail || "Failed to request OTP");
            setStep(STEPS.DISCONNECTED);
        } finally {
            setLoading(false);
        }
    };

    // Verify OTP
    const handleVerifyOTP = async () => {
        if (!otp || otp.length !== 6) {
            toast.error("Please enter a valid 6-digit OTP");
            return;
        }

        setLoading(true);

        try {
            const response = await api.post("/gst/verify", {
                gstin: gstin.toUpperCase(),
                otp: otp,
                transaction_id: transactionId
            });

            setConnectionStatus({
                gstin: gstin.toUpperCase(),
                is_connected: true,
                token_expiry: response.token_expiry
            });
            setStep(STEPS.CONNECTED);
            toast.success("GSTIN connected successfully!");

            // Auto-sync GSTR-2B data for current month
            handleSyncGSTR2B();
        } catch (error) {
            console.error("OTP verification failed:", error);
            toast.error(error.response?.data?.detail || "Invalid OTP. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    // Sync GSTR-2B Data
    const handleSyncGSTR2B = async () => {
        setLoading(true);
        setStep(STEPS.SYNCING);

        try {
            // Get current month in MMYYYY format
            const now = new Date();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const year = now.getFullYear();
            const returnPeriod = `${month}${year}`;

            const response = await api.post("/gst/sync", {
                gstin: gstin.toUpperCase(),
                return_period: returnPeriod
            });

            toast.success(`Synced ${response.total_invoices} invoices from GSTR-2B`);
            setStep(STEPS.CONNECTED);
        } catch (error) {
            console.error("GSTR-2B sync failed:", error);
            toast.error(error.response?.data?.detail || "Failed to sync GSTR-2B data");
            setStep(STEPS.CONNECTED);
        } finally {
            setLoading(false);
        }
    };

    // Disconnect GSTIN
    const handleDisconnect = async () => {
        if (!confirm("Are you sure you want to disconnect this GSTIN?")) {
            return;
        }

        setLoading(true);

        try {
            await api.delete(`/gst/disconnect/${gstin.toUpperCase()}`);

            setStep(STEPS.DISCONNECTED);
            setConnectionStatus(null);
            setGstin("");
            setOtp("");
            setTransactionId("");
            toast.success("GSTIN disconnected successfully");
        } catch (error) {
            console.error("Disconnect failed:", error);
            toast.error("Failed to disconnect GSTIN");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <Shield className="w-5 h-5 text-blue-600" />
                    <CardTitle>GSTR-2B Integration</CardTitle>
                </div>
            </CardHeader>
            <CardContent>
                {/* Disconnected State */}
                {step === STEPS.DISCONNECTED && (
                    <div className="space-y-4">
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <div className="flex items-start gap-3">
                                <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                                <div>
                                    <h4 className="font-medium text-blue-900">Connect your GSTIN</h4>
                                    <p className="text-sm text-blue-700 mt-1">
                                        Connect your GSTIN to automatically fetch GSTR-2B data and enable
                                        invoice reconciliation. This helps verify vendor compliance.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Enter your GSTIN
                            </label>
                            <Input
                                value={gstin}
                                onChange={(e) => setGstin(e.target.value.toUpperCase())}
                                placeholder="29AABCT1332L1ZZ"
                                maxLength={15}
                                className="font-mono"
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                15-digit GSTIN registered on GST Portal
                            </p>
                        </div>

                        <Button
                            onClick={handleRequestOTP}
                            disabled={loading || gstin.length !== 15}
                            isLoading={loading}
                            className="w-full"
                        >
                            {loading ? "Requesting OTP..." : "Request OTP"}
                        </Button>
                    </div>
                )}

                {/* OTP Verification State */}
                {step === STEPS.VERIFYING_OTP && (
                    <div className="space-y-4">
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <div className="flex items-start gap-3">
                                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                                <div>
                                    <h4 className="font-medium text-green-900">OTP Sent</h4>
                                    <p className="text-sm text-green-700 mt-1">
                                        A 6-digit OTP has been sent to your registered mobile number.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Enter OTP
                            </label>
                            <Input
                                type="text"
                                value={otp}
                                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                                placeholder="123456"
                                maxLength={6}
                                className="font-mono text-center text-2xl tracking-widest"
                            />
                        </div>

                        <div className="flex gap-2">
                            <Button
                                onClick={handleVerifyOTP}
                                disabled={loading || otp.length !== 6}
                                isLoading={loading}
                                className="flex-1"
                            >
                                {loading ? "Verifying..." : "Verify OTP"}
                            </Button>
                            <Button
                                onClick={() => {
                                    setStep(STEPS.DISCONNECTED);
                                    setOtp("");
                                    setTransactionId("");
                                }}
                                variant="outline"
                            >
                                Cancel
                            </Button>
                        </div>
                    </div>
                )}

                {/* Connected State */}
                {step === STEPS.CONNECTED && connectionStatus && (
                    <div className="space-y-4">
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <div className="flex items-start gap-3">
                                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                                <div className="flex-1">
                                    <h4 className="font-medium text-green-900">Connected</h4>
                                    <p className="text-sm text-green-700 mt-1">
                                        GSTIN: <span className="font-mono">{connectionStatus.gstin}</span>
                                    </p>
                                    <p className="text-xs text-green-600 mt-1">
                                        Token expires: {new Date(connectionStatus.token_expiry).toLocaleString()}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="flex gap-2">
                            <Button
                                onClick={handleSyncGSTR2B}
                                disabled={loading}
                                isLoading={loading}
                                className="flex-1"
                            >
                                {loading ? "Syncing..." : "Sync GSTR-2B Data"}
                            </Button>
                            <Button
                                onClick={handleDisconnect}
                                variant="outline"
                                disabled={loading}
                            >
                                Disconnect
                            </Button>
                        </div>
                    </div>
                )}

                {/* Syncing State */}
                {step === STEPS.SYNCING && (
                    <div className="flex items-center justify-center py-8">
                        <div className="text-center">
                            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
                            <p className="text-gray-600">Downloading GSTR-2B data...</p>
                            <p className="text-sm text-gray-500 mt-1">This may take a few moments</p>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
