"use client";
import { useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import Card, { CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Badge from "@/components/ui/Badge";
import {
    FileUp,
    CheckCircle,
    AlertTriangle,
    XCircle,
    HelpCircle,
    Download,
    RefreshCw
} from "lucide-react";
import toast from "react-hot-toast";
import api, { getAuthConfig } from "@/lib/api";
import { useAuth } from "@/app/context/AuthContext";

export default function ReconciliationPage() {
    const { session } = useAuth();
    const [file, setFile] = useState(null);
    const [returnPeriod, setReturnPeriod] = useState(new Date().toISOString().slice(5, 7) + new Date().getFullYear()); // Default current month
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [activeTab, setActiveTab] = useState("mismatch"); // Default to mismatch as it needs action

    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleRunReconciliation = async () => {
        if (!file) {
            toast.error("Please upload a Purchase Register file");
            return;
        }

        // Validate MMYYYY format
        if (!/^\d{6}$/.test(returnPeriod)) {
            toast.error("Invalid Return Period. Use MMYYYY format (e.g., 112024)");
            return;
        }

        setLoading(true);
        setResults(null);

        try {
            const token = session?.access_token;
            if (!token) {
                toast.error("Authentication required");
                return;
            }

            const formData = new FormData();
            formData.append("file", file);
            formData.append("return_period", returnPeriod);

            const { data } = await api.post('/reconcile/run', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    ...getAuthConfig(token).headers
                }
            });

            setResults(data);
            toast.success("Reconciliation Completed Successfully!");

        } catch (error) {
            console.error("Reconciliation error:", error);
            toast.error(error.response?.data?.detail || "Failed to run reconciliation");
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    };

    const tabs = [
        { id: "matched", label: "Matched", icon: CheckCircle, count: results?.summary?.matched || 0, color: "text-green-600" },
        { id: "mismatch", label: "Mismatch", icon: AlertTriangle, count: results?.summary?.mismatch || 0, color: "text-yellow-600" },
        { id: "missing_in_2b", label: "Missing in 2B", icon: XCircle, count: results?.summary?.missing_in_2b || 0, color: "text-red-600" },
        { id: "missing_in_pr", label: "Missing in PR", icon: HelpCircle, count: results?.summary?.missing_in_pr || 0, color: "text-blue-600" },
    ];

    return (
        <AppLayout>
            <div className="space-y-6">
                {/* Header */}
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">GSTR-2B Reconciliation</h1>
                    <p className="text-gray-600">Match your Purchase Register with Government Data (GSTR-2B)</p>
                </div>

                {/* Input Section */}
                <Card>
                    <CardHeader>
                        <CardTitle>Run New Reconciliation</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Return Period (MMYYYY)</label>
                                <Input
                                    value={returnPeriod}
                                    onChange={(e) => setReturnPeriod(e.target.value)}
                                    placeholder="e.g. 112023"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Upload Purchase Register</label>
                                <div className="relative">
                                    <input
                                        type="file"
                                        id="pr-upload"
                                        className="hidden"
                                        onChange={handleFileChange}
                                        accept=".csv, .xlsx, .xls"
                                    />
                                    <label
                                        htmlFor="pr-upload"
                                        className="flex items-center justify-center w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer"
                                    >
                                        <FileUp className="w-4 h-4 mr-2" />
                                        {file ? file.name : "Choose Excel/CSV File"}
                                    </label>
                                </div>
                            </div>

                            <div>
                                <Button
                                    onClick={handleRunReconciliation}
                                    disabled={loading}
                                    className="w-full"
                                >
                                    {loading ? (
                                        <>
                                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                            Processing...
                                        </>
                                    ) : (
                                        <>
                                            <CheckCircle className="w-4 h-4 mr-2" />
                                            Run Matching
                                        </>
                                    )}
                                </Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Results Section */}
                {results && (
                    <div className="space-y-6">
                        {/* Stats Overview */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
                                <p className="text-sm text-gray-500">Total Invoices (PR)</p>
                                <p className="text-2xl font-bold text-gray-900">{results.summary.total_pr}</p>
                            </div>
                            <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
                                <p className="text-sm text-gray-500">Total Invoices (2B)</p>
                                <p className="text-2xl font-bold text-blue-600">{results.summary.total_2b}</p>
                            </div>
                            <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
                                <p className="text-sm text-gray-500">Matched Amount</p>
                                <p className="text-2xl font-bold text-green-600">
                                    {formatCurrency(results.results.matched.reduce((acc, item) => acc + item.pr_amount, 0))}
                                </p>
                            </div>
                            <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
                                <p className="text-sm text-gray-500">Disputed Amount</p>
                                <p className="text-2xl font-bold text-red-600">
                                    {formatCurrency(
                                        results.results.missing_in_2b.reduce((acc, item) => acc + item.pr_amount, 0) +
                                        results.results.mismatch.reduce((acc, item) => acc + Math.abs(item.difference), 0)
                                    )}
                                </p>
                            </div>
                        </div>

                        {/* Detailed Tabs */}
                        <div className="bg-white shadow rounded-lg overflow-hidden">
                            <div className="border-b border-gray-200">
                                <nav className="flex -mb-px">
                                    {tabs.map((tab) => {
                                        const isSelected = activeTab === tab.id;
                                        const Icon = tab.icon;
                                        return (
                                            <button
                                                key={tab.id}
                                                onClick={() => setActiveTab(tab.id)}
                                                className={`
                           flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm flex items-center justify-center gap-2
                           ${isSelected
                                                        ? `border-blue-500 text-blue-600`
                                                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                                                    }
                         `}
                                            >
                                                <Icon className={`w-4 h-4 ${isSelected ? tab.color : ""}`} />
                                                {tab.label}
                                                <span className={`ml-2 py-0.5 px-2.5 rounded-full text-xs font-medium ${isSelected ? "bg-blue-100 text-blue-600" : "bg-gray-100 text-gray-900"}`}>
                                                    {tab.count}
                                                </span>
                                            </button>
                                        );
                                    })}
                                </nav>
                            </div>

                            {/* Table Content */}
                            <div className="p-4">
                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">GSTIN</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor Name</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice No</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">PR Amount</th>
                                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">2B Amount</th>
                                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Diff</th>
                                                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {results.results[activeTab].length === 0 ? (
                                                <tr>
                                                    <td colSpan="8" className="px-6 py-12 text-center text-gray-500">
                                                        <p className="text-sm">No records found in this category.</p>
                                                    </td>
                                                </tr>
                                            ) : (
                                                results.results[activeTab].map((item, idx) => (
                                                    <tr key={idx} className="hover:bg-gray-50">
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.gstin}</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.vendor_name || "-"}</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.invoice_number}</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.invoice_date}</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900 font-medium">{formatCurrency(item.pr_amount)}</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">{formatCurrency(item.gstr2b_amount)}</td>
                                                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-bold ${item.difference !== 0 ? 'text-red-600' : 'text-gray-400'}`}>
                                                            {formatCurrency(item.difference)}
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-center">
                                                            <Badge variant={
                                                                item.status === "MATCHED" ? "success" :
                                                                    item.status === "MISMATCH" ? "warning" :
                                                                        "danger"
                                                            }>
                                                                {item.message}
                                                            </Badge>
                                                        </td>
                                                    </tr>
                                                ))
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
