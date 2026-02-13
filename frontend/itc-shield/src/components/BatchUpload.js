"use client";
import { useState, useCallback } from "react";
import { Upload, FileText, Download, AlertCircle } from "lucide-react";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import toast from "react-hot-toast";
import { useAuth } from "@/app/context/AuthContext";

import api, { getAuthConfig } from "@/lib/api";

export default function BatchUpload({ onUploadSuccess }) {
    const { session } = useAuth();
    const [isDragging, setIsDragging] = useState(false);
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setIsDragging(false);

        const droppedFile = e.dataTransfer.files[0];
        validateAndSetFile(droppedFile);
    }, []);

    const handleFileSelect = (e) => {
        const selectedFile = e.target.files[0];
        validateAndSetFile(selectedFile);
    };

    const validateAndSetFile = (file) => {
        if (!file) return;

        // Validate file type
        if (!file.name.endsWith(".csv")) {
            toast.error("Please upload a CSV file");
            return;
        }

        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            toast.error("File size must be less than 5MB");
            return;
        }

        setFile(file);
        toast.success(`File selected: ${file.name}`);
    };

    const handleUpload = async () => {
        if (!file) {
            toast.error("Please select a file first");
            return;
        }

        setUploading(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const token = session?.access_token;
            if (!token) throw new Error("Not authenticated");

            const data = await api.post('/batch/upload', formData, {
                headers: {
                    ...getAuthConfig(token).headers,
                    "Content-Type": undefined
                }
            });
            // toast.success(`Batch uploaded successfully! Job ID: ${data.job_id}`); // Handled by parent

            // Reset file
            setFile(null);

            // Notify parent component
            if (onUploadSuccess) {
                onUploadSuccess(data);
            }
        } catch (error) {
            console.error("Upload error:", error);

            // Handle Pydantic validation errors (422)
            let errorMessage = "Failed to upload batch";
            if (error.response?.data?.detail) {
                if (Array.isArray(error.response.data.detail)) {
                    // Pydantic validation errors
                    errorMessage = error.response.data.detail.map(err => err.msg).join(", ");
                } else if (typeof error.response.data.detail === 'string') {
                    errorMessage = error.response.data.detail;
                } else if (error.response.data.detail.message) {
                    errorMessage = error.response.data.detail.message;
                }
            } else if (error.message) {
                errorMessage = error.message;
            }

            toast.error(errorMessage);
        } finally {
            setUploading(false);
        }
    };

    const downloadTemplate = () => {
        // Create sample CSV with proper formatting
        const csvContent = `gstin,party_name,amount
33AAJCG9959L1ZT,ABC Enterprises,100000
29AABCU9603R1ZX,XYZ Corporation,50000
01AABCU9603R1ZX,Test Vendor Ltd,75000`;

        // Add UTF-8 BOM for better Excel compatibility
        const BOM = '\uFEFF';
        const blob = new Blob([BOM + csvContent], { type: "text/csv;charset=utf-8;" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "vendor_batch_template.csv";
        a.style.display = "none";
        document.body.appendChild(a);
        a.click();

        // Cleanup
        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 100);

        toast.success("Template downloaded successfully");
    };

    return (
        <div className="space-y-6">
            {/* Instructions Card */}
            <Card>
                <CardHeader>
                    <CardTitle>Batch Processing Instructions</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3 text-sm text-gray-600">
                        <div className="flex items-start gap-2">
                            <AlertCircle className="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" />
                            <div>
                                <p className="font-medium text-gray-900">CSV Format Required</p>
                                <p>Upload a CSV file with columns: gstin, party_name, amount</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-2">
                            <FileText className="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" />
                            <div>
                                <p className="font-medium text-gray-900">Limits</p>
                                <p>Maximum 500 vendors per batch, file size up to 5MB</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-2">
                            <Download className="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" />
                            <div>
                                <p className="font-medium text-gray-900">Download Template</p>
                                <button
                                    onClick={downloadTemplate}
                                    className="text-blue-600 hover:text-blue-700 underline"
                                >
                                    Click here to download a sample CSV template
                                </button>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Upload Area */}
            <Card>
                <CardContent className="pt-6">
                    <div
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        className={`
              border-2 border-dashed rounded-lg p-12 text-center transition-colors
              ${isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300 bg-gray-50"}
              ${file ? "bg-green-50 border-green-300" : ""}
            `}
                    >
                        <Upload className={`w-12 h-12 mx-auto mb-4 ${file ? "text-green-600" : "text-gray-400"}`} />

                        {file ? (
                            <div className="space-y-2">
                                <p className="text-lg font-medium text-green-700">File Selected</p>
                                <p className="text-sm text-gray-600">{file.name}</p>
                                <p className="text-xs text-gray-500">
                                    {(file.size / 1024).toFixed(2)} KB
                                </p>
                                <div className="pt-4">
                                    <Button
                                        onClick={() => setFile(null)}
                                        variant="ghost"
                                        size="sm"
                                    >
                                        Remove File
                                    </Button>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                <p className="text-lg font-medium text-gray-700">
                                    Drag & drop your CSV file here
                                </p>
                                <p className="text-sm text-gray-500">or</p>
                                <label className="inline-block">
                                    <input
                                        type="file"
                                        accept=".csv"
                                        onChange={handleFileSelect}
                                        className="hidden"
                                    />
                                    <span className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 cursor-pointer transition-colors">
                                        <FileText className="w-4 h-4" />
                                        Choose File
                                    </span>
                                </label>
                            </div>
                        )}
                    </div>

                    {file && (
                        <div className="mt-6 flex justify-center">
                            <Button
                                onClick={handleUpload}
                                disabled={uploading}
                                size="lg"
                            >
                                {uploading ? "Uploading..." : "Upload & Process Batch"}
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
