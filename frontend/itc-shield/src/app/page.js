"use client";
import { useState, useEffect } from "react";
import { useAuth } from "@/app/context/AuthContext";
import AppLayout from "@/components/layout/AppLayout";
import StatCard from "@/components/ui/StatCard";
import Card, { CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Badge from "@/components/ui/Badge";
import BatchUpload from "@/components/BatchUpload";
import BatchStatus from "@/components/BatchStatus";
import {
  Shield,
  Users,
  AlertTriangle,
  TrendingUp,
  Search,
  Download,
  CheckCircle,
  XCircle,
  Clock,
  FileUp,
  History
} from "lucide-react";
import toast from "react-hot-toast";

import api, { getAuthConfig } from "@/lib/api";

export default function Dashboard() {
  const { session } = useAuth();
  const [activeTab, setActiveTab] = useState("single"); // single, batch, history
  const [gstin, setGstin] = useState("");
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [batchJobId, setBatchJobId] = useState(null);
  const [recentChecks, setRecentChecks] = useState([]);

  const fetchRecentChecks = async () => {
    try {
      const token = session?.access_token;
      if (!token) return;

      const data = await api.get('/compliance/history?limit=5', getAuthConfig(token));
      setRecentChecks(data);
    } catch (error) {
      console.error("Failed to fetch recent checks:", error);
    }
  };

  // Fetch recent checks on mount and when session changes
  useEffect(() => {
    if (session?.access_token) {
      fetchRecentChecks();
    }
  }, [session]);

  const handleCheck = async () => {
    if (!gstin || gstin.length !== 15) {
      toast.error("Please enter a valid 15-character GSTIN");
      return;
    }

    if (!amount) {
      toast.error("Please enter an invoice amount");
      return;
    }

    setLoading(true);
    try {
      const token = session?.access_token;
      if (!token) throw new Error("Not authenticated");

      const data = await api.post('/compliance/check', {
        gstin: gstin.toUpperCase(),
        amount: parseFloat(amount),
        party_name: "Vendor Check",
      }, getAuthConfig(token));

      setResult(data);
      console.log("Compliance Result:", data);
      console.log("Compliance Result:", data);
      toast.success("Compliance check completed");

      // Update recent checks list
      fetchRecentChecks();

      // Auto-scroll to result
      setTimeout(() => {
        document.getElementById("result-section")?.scrollIntoView({ behavior: "smooth", block: "center" });
      }, 100);
    } catch (error) {
      console.error("Check error:", error);
      toast.error(error.response?.data?.detail || error.message || "Failed to perform compliance check");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCertificate = async () => {
    if (!result?.check_id) {
      toast.error("No check result available");
      return;
    }

    try {
      const token = session?.access_token;
      if (!token) throw new Error("Not authenticated");

      const blob = await api.get(
        `/compliance/certificate/${result.check_id}`,
        {
          ...getAuthConfig(token),
          responseType: 'blob'
        }
      );
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ITC_Shield_Certificate_${result.gstin}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast.success("Certificate downloaded successfully");
    } catch (error) {
      console.error("Download error:", error);
      toast.error("Failed to download certificate");
    }
  };

  const handleSingleCheckReset = () => {
    setGstin("");
    setAmount("");
    setResult(null);
    toast.dismiss();
  };

  const handleBatchReset = () => {
    setBatchJobId(null);
    toast.dismiss();
  };

  const handleBatchUploadSuccess = (data) => {
    setBatchJobId(data.job_id);
    toast.dismiss('batch-upload');
    toast.loading(
      <div className="font-medium">
        🚀 Batch uploaded!
        <div className="text-sm font-normal opacity-80 mt-1">
          Tracking processing status...
        </div>
      </div>,
      { id: 'batch-upload', duration: 4000 }
    );
  };

  const handleBatchComplete = (data) => {
    toast.dismiss('batch-upload');
    toast.success(
      <div className="font-medium">
        ✅ Batch Processing Complete!
        <div className="text-sm font-normal opacity-80 mt-1">
          {data.success_count} Successful • {data.failed_count} Failed
        </div>
      </div>,
      { id: 'batch-complete', duration: 5000 }
    );
  };

  const getDecisionBadge = (decision) => {
    switch (decision) {
      case "RELEASE":
        return <Badge variant="success">APPROVED</Badge>;
      case "HOLD":
        return <Badge variant="warning">REVIEW REQUIRED</Badge>;
      case "STOP":
        return <Badge variant="danger">BLOCKED</Badge>;
      default:
        return <Badge variant="default">{decision}</Badge>;
    }
  };

  const tabs = [
    { id: "single", label: "Single Check", icon: Search },
    { id: "batch", label: "Batch Upload", icon: FileUp },
    { id: "history", label: "History", icon: History },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Monitor vendor compliance and GST filing status</p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Compliance Score"
            value="94%"
            change="+2.5% from last month"
            trend="up"
            icon={Shield}
          />
          <StatCard
            title="Total Vendors"
            value="1,234"
            change="+12 this week"
            trend="up"
            icon={Users}
          />
          <StatCard
            title="Risk Alerts"
            value="8"
            change="-3 from yesterday"
            trend="down"
            icon={AlertTriangle}
          />
          <StatCard
            title="Checks Today"
            value="156"
            change="+23% vs average"
            trend="up"
            icon={TrendingUp}
          />
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="flex gap-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-1 py-4 border-b-2 font-medium text-sm transition-colors
                    ${activeTab === tab.id
                      ? "border-blue-600 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="mt-6">
          {/* Single Check Tab */}
          {activeTab === "single" && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Quick Compliance Check</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      placeholder="Enter GSTIN (e.g., 33AAJCG9959L1ZT)"
                      value={gstin}
                      onChange={(e) => setGstin(e.target.value.toUpperCase())}
                      className="w-full"
                      maxLength={15}
                    />
                    <div className="relative">
                      <Input
                        type="number"
                        placeholder="Invoice Amount (₹)"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        className="w-full"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end pt-4">
                    <Button onClick={handleCheck} disabled={loading} className="w-full md:w-auto">
                      <Search className="w-4 h-4 mr-2" />
                      {loading ? "Checking Compliance..." : "Check Compliance"}
                    </Button>
                  </div>

                  {result && (
                    <div id="result-section" className="mt-6 p-6 bg-gray-50 rounded-lg space-y-4 border border-blue-100 shadow-sm">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">Decision</p>
                          <div className="mt-1">{getDecisionBadge(result.decision)}</div>
                        </div>
                        <div className="flex gap-2">
                          <Button onClick={handleSingleCheckReset} variant="ghost" className="text-gray-600 hover:text-gray-900">
                            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                            Start New Check
                          </Button>
                          <Button onClick={handleDownloadCertificate} variant="secondary">
                            <Download className="w-4 h-4 mr-2" />
                            Download Certificate
                          </Button>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                        <div>
                          <p className="text-sm text-gray-600">GSTIN</p>
                          <p className="font-medium text-gray-900">{result.gstin}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Vendor Name</p>
                          <p className="font-medium text-gray-900">{result.vendor_name || "N/A"}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Risk Level</p>
                          <p className="font-medium text-gray-900">{result.risk_level}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Timestamp</p>
                          <p className="font-medium text-xs mt-1 text-gray-900">
                            {result.timestamp ? new Date(result.timestamp).toLocaleString() : new Date().toLocaleString()}
                          </p>
                        </div>
                      </div>

                      <div className="pt-4 border-t">
                        <p className="text-sm text-gray-600">Reason</p>
                        <p className="mt-1 text-gray-900">{result.message}</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Recent Checks */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Recent Checks</CardTitle>
                    <button className="text-sm text-blue-600 hover:text-blue-700">
                      View All
                    </button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">

                    {recentChecks.length === 0 ? (
                      <p className="text-center text-gray-500 py-4">No recent checks found.</p>
                    ) : (
                      recentChecks.map((check, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{check.vendor_name || "Unknown Vendor"}</p>
                            <p className="text-sm text-gray-600">{check.gstin}</p>
                          </div>
                          <div className="flex items-center gap-4">
                            {check.decision === "RELEASE" && (
                              <Badge variant="success">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Approved
                              </Badge>
                            )}
                            {check.decision === "HOLD" && (
                              <Badge variant="warning">
                                <Clock className="w-3 h-3 mr-1" />
                                Review
                              </Badge>
                            )}
                            {check.decision === "STOP" && (
                              <Badge variant="danger">
                                <XCircle className="w-3 h-3 mr-1" />
                                Blocked
                              </Badge>
                            )}
                            <span className="text-sm text-gray-500">
                              {new Date(check.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Batch Upload Tab */}
          {activeTab === "batch" && (
            <div className="space-y-6">
              {!batchJobId ? (
                <BatchUpload onUploadSuccess={handleBatchUploadSuccess} />
              ) : (
                <div className="space-y-6">
                  <BatchStatus jobId={batchJobId} onComplete={handleBatchComplete} onReset={handleBatchReset} />
                  <div className="text-center">
                    <Button
                      onClick={() => setBatchJobId(null)}
                      variant="ghost"
                    >
                      Upload Another Batch
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* History Tab */}
          {activeTab === "history" && (
            <Card>
              <CardHeader>
                <CardTitle>Compliance Check History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12 text-gray-500">
                  <History className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p>History feature coming soon</p>
                  <p className="text-sm mt-2">
                    This will show all your past compliance checks with filtering and search
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
