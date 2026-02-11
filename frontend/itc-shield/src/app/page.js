"use client";
import { useState } from "react";
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

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Dashboard() {
  const { session } = useAuth();
  const [activeTab, setActiveTab] = useState("single"); // single, batch, history
  const [gstin, setGstin] = useState("");
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [batchJobId, setBatchJobId] = useState(null);

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

      const response = await fetch(`${API_URL}/api/v1/compliance/check`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          gstin: gstin.toUpperCase(),
          amount: parseFloat(amount),
          party_name: "Vendor Check",
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "API request failed");
      }

      const data = await response.json();
      setResult(data);
      toast.success("Compliance check completed");
    } catch (error) {
      console.error("Check error:", error);
      toast.error(error.message || "Failed to perform compliance check");
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

      const response = await fetch(
        `${API_URL}/api/v1/compliance/certificate/${result.check_id}`,
        {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        }
      );

      if (!response.ok) throw new Error("Download failed");

      const blob = await response.blob();
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

  const handleBatchUploadSuccess = (data) => {
    setBatchJobId(data.job_id);
    toast.dismiss('batch-upload');
    toast.success("Batch uploaded! Tracking progress...", { id: 'batch-upload' });
  };

  const handleBatchComplete = (data) => {
    toast.dismiss('batch-complete');
    toast.success(`Batch processing complete! ${data.success_count} successful, ${data.failed_count} failed`, { id: 'batch-complete' });
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
                    <div className="mt-6 p-6 bg-gray-50 rounded-lg space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">Decision</p>
                          <div className="mt-1">{getDecisionBadge(result.decision)}</div>
                        </div>
                        <Button onClick={handleDownloadCertificate} variant="secondary">
                          <Download className="w-4 h-4 mr-2" />
                          Download Certificate
                        </Button>
                      </div>

                      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                        <div>
                          <p className="text-sm text-gray-600">GSTIN</p>
                          <p className="font-medium">{result.gstin}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Vendor Name</p>
                          <p className="font-medium">{result.vendor_name || "N/A"}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Risk Level</p>
                          <p className="font-medium">{result.risk_level}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Data Source</p>
                          <p className="font-medium">{result.data_source}</p>
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
                    {[
                      {
                        name: "ABC Enterprises",
                        gstin: "33AAJCG9959L1ZT",
                        status: "Approved",
                        time: "2 min ago",
                      },
                      {
                        name: "XYZ Corp",
                        gstin: "29AABCU9603R1ZX",
                        status: "Review Required",
                        time: "15 min ago",
                      },
                      {
                        name: "Test Vendor Ltd",
                        gstin: "01AABCU9603R1ZX",
                        status: "Blocked",
                        time: "1 hour ago",
                      },
                    ].map((check, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{check.name}</p>
                          <p className="text-sm text-gray-600">{check.gstin}</p>
                        </div>
                        <div className="flex items-center gap-4">
                          {check.status === "Approved" && (
                            <Badge variant="success">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              {check.status}
                            </Badge>
                          )}
                          {check.status === "Review Required" && (
                            <Badge variant="warning">
                              <Clock className="w-3 h-3 mr-1" />
                              {check.status}
                            </Badge>
                          )}
                          {check.status === "Blocked" && (
                            <Badge variant="danger">
                              <XCircle className="w-3 h-3 mr-1" />
                              {check.status}
                            </Badge>
                          )}
                          <span className="text-sm text-gray-500">{check.time}</span>
                        </div>
                      </div>
                    ))}
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
                  <BatchStatus jobId={batchJobId} onComplete={handleBatchComplete} />
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
