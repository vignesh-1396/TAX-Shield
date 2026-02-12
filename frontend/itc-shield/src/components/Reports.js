"use client";
import { useState } from "react";
import Card, { CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { Calendar, Download, FileText, AlertTriangle, Shield } from "lucide-react";
import toast from "react-hot-toast";
import { useAuth } from "@/app/context/AuthContext";

import api, { getAuthConfig } from "@/lib/api";

export default function Reports() {
    const { session } = useAuth();
    const [reportType, setReportType] = useState("summary"); // summary, high-risk, audit-trail
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [loading, setLoading] = useState(false);
    const [reportData, setReportData] = useState(null);

    const handleGenerateReport = async () => {
        setLoading(true);
        try {
            const token = session?.access_token;
            if (!token) throw new Error("Not authenticated");

            const { data } = await api.get(`/api/v1/reports/${reportType}`, {
                ...getAuthConfig(token),
                params: {
                    start_date: startDate || undefined,
                    end_date: endDate || undefined
                }
            });

            setReportData(data);
            toast.success("Report generated successfully");
        } catch (error) {
            console.error("Report error:", error);
            toast.error("Failed to generate report");
        } finally {
            setLoading(false);
        }
    };

    const handleExportCSV = () => {
        if (!reportData) return;

        let csvContent = "";
        let filename = "";

        if (reportType === "summary") {
            filename = `compliance_summary_${startDate || "all"}_${endDate || "all"}.csv`;
            csvContent = "Metric,Value\n";
            csvContent += `Total Checks,${reportData.total_checks}\n`;
            csvContent += `RELEASE,${reportData.decisions.RELEASE}\n`;
            csvContent += `HOLD,${reportData.decisions.HOLD}\n`;
            csvContent += `STOP,${reportData.decisions.STOP}\n`;
            csvContent += `Total Amount,${reportData.amounts.total}\n`;
            csvContent += `Released Amount,${reportData.amounts.released}\n`;
            csvContent += `Blocked Amount,${reportData.amounts.blocked}\n`;
        } else if (reportType === "high-risk") {
            filename = `high_risk_vendors_${startDate || "all"}_${endDate || "all"}.csv`;
            csvContent = "GSTIN,Vendor Name,Amount,Decision,Risk Level,Reason,Date\n";
            reportData.checks.forEach((check) => {
                csvContent += `${check.gstin},"${check.vendor_name}",${check.amount},${check.decision},${check.risk_level},"${check.reason}",${check.created_at}\n`;
            });
        } else if (reportType === "audit-trail") {
            filename = `audit_trail_${startDate || "all"}_${endDate || "all"}.csv`;
            csvContent = "ID,GSTIN,Vendor Name,Amount,Decision,Risk Level,Reason,Date\n";
            reportData.checks.forEach((check) => {
                csvContent += `${check.id},${check.gstin},"${check.vendor_name}",${check.amount},${check.decision},${check.risk_level},"${check.reason}",${check.created_at}\n`;
            });
        }

        const blob = new Blob([csvContent], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        toast.success("Report exported successfully");
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0,
        }).format(amount);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
                <p className="text-gray-600 mt-1">
                    Generate compliance analytics and audit documentation
                </p>
            </div>

            {/* Report Configuration */}
            <Card>
                <CardHeader>
                    <CardTitle>Generate Report</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        {/* Report Type */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Report Type
                            </label>
                            <select
                                value={reportType}
                                onChange={(e) => setReportType(e.target.value)}
                                className="w-full h-10 px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm cursor-pointer"
                                style={{ color: '#111827' }}
                            >
                                <option value="summary">Compliance Summary</option>
                                <option value="high-risk">High-Risk Vendors</option>
                                <option value="audit-trail">Audit Trail</option>
                            </select>
                        </div>

                        {/* Start Date */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Start Date
                            </label>
                            <Input
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                placeholder="Start date"
                                className="h-10"
                            />
                        </div>

                        {/* End Date */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                End Date
                            </label>
                            <Input
                                type="date"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                                placeholder="End date"
                                className="h-10"
                            />
                        </div>

                        {/* Generate Button */}
                        <div className="flex items-end">
                            <Button
                                onClick={handleGenerateReport}
                                disabled={loading}
                                className="w-full"
                            >
                                <FileText className="w-4 h-4 mr-2" />
                                {loading ? "Generating..." : "Generate"}
                            </Button>
                        </div>
                    </div>

                    {reportData && (
                        <div className="mt-4 flex justify-end">
                            <Button onClick={handleExportCSV} variant="outline">
                                <Download className="w-4 h-4 mr-2" />
                                Export CSV
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Report Results */}
            {reportData && (
                <>
                    {reportType === "summary" && (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Total Checks */}
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-center">
                                        <Shield className="w-12 h-12 mx-auto text-blue-600 mb-2" />
                                        <div className="text-3xl font-bold text-gray-900">
                                            {reportData.total_checks}
                                        </div>
                                        <div className="text-sm text-gray-600 mt-1">Total Checks</div>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Decisions Breakdown */}
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">RELEASE</span>
                                            <span className="text-lg font-semibold text-green-600">
                                                {reportData.decisions.RELEASE}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">HOLD</span>
                                            <span className="text-lg font-semibold text-yellow-600">
                                                {reportData.decisions.HOLD}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">STOP</span>
                                            <span className="text-lg font-semibold text-red-600">
                                                {reportData.decisions.STOP}
                                            </span>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Amount Statistics */}
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="space-y-3">
                                        <div>
                                            <div className="text-sm text-gray-600">Total Amount</div>
                                            <div className="text-xl font-bold text-gray-900">
                                                {formatCurrency(reportData.amounts.total)}
                                            </div>
                                        </div>
                                        <div>
                                            <div className="text-sm text-gray-600">Blocked Amount</div>
                                            <div className="text-lg font-semibold text-red-600">
                                                {formatCurrency(reportData.amounts.blocked)}
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}

                    {reportType === "high-risk" && (
                        <Card>
                            <CardHeader>
                                <div className="flex justify-between items-center">
                                    <CardTitle>High-Risk Vendors</CardTitle>
                                    <div className="text-sm text-gray-600">
                                        Total Exposure: <span className="font-semibold text-red-600">
                                            {formatCurrency(reportData.total_exposure)}
                                        </span>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="border-b border-gray-200">
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    GSTIN
                                                </th>
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    Vendor Name
                                                </th>
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    Amount
                                                </th>
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    Decision
                                                </th>
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    Risk Level
                                                </th>
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    Reason
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {reportData.checks.map((check) => (
                                                <tr key={check.id} className="border-b border-gray-100 hover:bg-gray-50">
                                                    <td className="py-3 px-4 text-sm font-mono">{check.gstin}</td>
                                                    <td className="py-3 px-4 text-sm">{check.vendor_name}</td>
                                                    <td className="py-3 px-4 text-sm">{formatCurrency(check.amount)}</td>
                                                    <td className="py-3 px-4">
                                                        <span
                                                            className={`px-2 py-1 rounded-full text-xs font-medium ${check.decision === "HOLD"
                                                                ? "bg-yellow-100 text-yellow-800"
                                                                : "bg-red-100 text-red-800"
                                                                }`}
                                                        >
                                                            {check.decision}
                                                        </span>
                                                    </td>
                                                    <td className="py-3 px-4 text-sm">{check.risk_level}</td>
                                                    <td className="py-3 px-4 text-sm text-gray-600">{check.reason}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {reportType === "audit-trail" && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Audit Trail ({reportData.total_count} records)</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="border-b border-gray-200">
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    ID
                                                </th>
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    Date
                                                </th>
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    GSTIN
                                                </th>
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    Vendor Name
                                                </th>
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    Amount
                                                </th>
                                                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                                    Decision
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {reportData.checks.slice(0, 100).map((check) => (
                                                <tr key={check.id} className="border-b border-gray-100 hover:bg-gray-50">
                                                    <td className="py-3 px-4 text-sm">{check.id}</td>
                                                    <td className="py-3 px-4 text-sm">
                                                        {new Date(check.created_at).toLocaleDateString()}
                                                    </td>
                                                    <td className="py-3 px-4 text-sm font-mono">{check.gstin}</td>
                                                    <td className="py-3 px-4 text-sm">{check.vendor_name}</td>
                                                    <td className="py-3 px-4 text-sm">{formatCurrency(check.amount)}</td>
                                                    <td className="py-3 px-4">
                                                        <span
                                                            className={`px-2 py-1 rounded-full text-xs font-medium ${check.decision === "RELEASE"
                                                                ? "bg-green-100 text-green-800"
                                                                : check.decision === "HOLD"
                                                                    ? "bg-yellow-100 text-yellow-800"
                                                                    : "bg-red-100 text-red-800"
                                                                }`}
                                                        >
                                                            {check.decision}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                    {reportData.total_count > 100 && (
                                        <div className="text-center py-4 text-sm text-gray-600">
                                            Showing first 100 of {reportData.total_count} records. Export CSV for complete data.
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </>
            )}
        </div>
    );
}
