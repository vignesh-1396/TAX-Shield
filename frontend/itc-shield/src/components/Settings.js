"use client";
import { useState, useEffect } from "react";
import Card, { CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { Save, User, Bell, Settings as SettingsIcon, Building, Phone, MapPin } from "lucide-react";
import toast from "react-hot-toast";
import { useAuth } from "@/app/context/AuthContext";
import { supabase } from "@/lib/supabase";
import ConnectGST from "@/components/ConnectGST";

const DEFAULT_SETTINGS = {
    profile: {
        companyName: "",
        email: "",
        userName: "",
        phone: "",
        address: "",
    },
    notifications: {
        emailAlerts: true,
        dailySummary: true,
        thresholdAmount: 100000,
    },
    preferences: {
        defaultAmount: 50000,
        dateFormat: "DD/MM/YYYY",
        currencyFormat: "indian",
        autoDownload: true,
    },
};

export default function Settings() {
    const { user } = useAuth();
    const [settings, setSettings] = useState(DEFAULT_SETTINGS);
    const [hasChanges, setHasChanges] = useState(false);
    const [loading, setLoading] = useState(false);

    // Load settings from Supabase metadata
    useEffect(() => {
        if (user) {
            const metadata = user.user_metadata || {};

            setSettings({
                profile: {
                    companyName: metadata.company_name || "",
                    email: user.email || "",
                    userName: metadata.full_name || "",
                    phone: metadata.phone || "",
                    address: metadata.address || "",
                },
                notifications: metadata.notifications || DEFAULT_SETTINGS.notifications,
                preferences: metadata.preferences || DEFAULT_SETTINGS.preferences,
            });
        }
    }, [user]);

    const handleSave = async () => {
        setLoading(true);
        try {
            const { error } = await supabase.auth.updateUser({
                data: {
                    full_name: settings.profile.userName,
                    company_name: settings.profile.companyName,
                    phone: settings.profile.phone,
                    address: settings.profile.address,
                    notifications: settings.notifications,
                    preferences: settings.preferences,
                }
            });

            if (error) throw error;

            setHasChanges(false);
            toast.success("Settings saved successfully");
        } catch (error) {
            console.error("Failed to save settings:", error);
            toast.error("Failed to save settings");
        } finally {
            setLoading(false);
        }
    };

    const handleProfileChange = (field, value) => {
        setSettings((prev) => ({
            ...prev,
            profile: { ...prev.profile, [field]: value },
        }));
        setHasChanges(true);
    };

    const handleNotificationChange = (field, value) => {
        setSettings((prev) => ({
            ...prev,
            notifications: { ...prev.notifications, [field]: value },
        }));
        setHasChanges(true);
    };

    const handlePreferenceChange = (field, value) => {
        setSettings((prev) => ({
            ...prev,
            preferences: { ...prev.preferences, [field]: value },
        }));
        setHasChanges(true);
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
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
                    <p className="text-gray-600 mt-1">
                        Manage your profile and preferences
                    </p>
                </div>
                <Button onClick={handleSave} disabled={!hasChanges || loading} isLoading={loading}>
                    <Save className="w-4 h-4 mr-2" />
                    Save Changes
                </Button>
            </div>

            {/* Profile Settings */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <User className="w-5 h-5 text-gray-600" />
                        <CardTitle>Profile Settings</CardTitle>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Company Name
                            </label>
                            <Input
                                value={settings.profile.companyName}
                                onChange={(e) =>
                                    handleProfileChange("companyName", e.target.value)
                                }
                                placeholder="Enter company name"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Contact Email
                            </label>
                            <Input
                                type="email"
                                value={settings.profile.email}
                                disabled
                                className="bg-gray-50"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                User Name
                            </label>
                            <Input
                                value={settings.profile.userName}
                                onChange={(e) => handleProfileChange("userName", e.target.value)}
                                placeholder="Enter your name"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Phone Number
                            </label>
                            <Input
                                type="tel"
                                value={settings.profile.phone}
                                onChange={(e) => handleProfileChange("phone", e.target.value)}
                                placeholder="+91 98765 43210"
                                required
                            />
                        </div>

                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Address
                            </label>
                            <Input
                                value={settings.profile.address}
                                onChange={(e) => handleProfileChange("address", e.target.value)}
                                placeholder="123 Business St, City, State, Zip"
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Notification Preferences */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <Bell className="w-5 h-5 text-gray-600" />
                        <CardTitle>Notification Preferences</CardTitle>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {/* Email Alerts Toggle */}
                        <div className="flex items-center justify-between py-3 border-b border-gray-200">
                            <div>
                                <div className="font-medium text-gray-900">
                                    Email alerts for high-risk vendors
                                </div>
                                <div className="text-sm text-gray-600">
                                    Get notified when a vendor is marked as HOLD or STOP
                                </div>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={settings.notifications.emailAlerts}
                                    onChange={(e) =>
                                        handleNotificationChange("emailAlerts", e.target.checked)
                                    }
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                            </label>
                        </div>

                        {/* Daily Summary Toggle */}
                        <div className="flex items-center justify-between py-3 border-b border-gray-200">
                            <div>
                                <div className="font-medium text-gray-900">
                                    Daily compliance summary
                                </div>
                                <div className="text-sm text-gray-600">
                                    Receive a daily report at 8:00 AM with compliance stats
                                </div>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={settings.notifications.dailySummary}
                                    onChange={(e) =>
                                        handleNotificationChange("dailySummary", e.target.checked)
                                    }
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                            </label>
                        </div>

                        {/* Threshold Amount */}
                        <div className="py-3">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Alert when daily blocked amount exceeds
                            </label>
                            <div className="flex items-center gap-4">
                                <Input
                                    type="number"
                                    value={settings.notifications.thresholdAmount}
                                    onChange={(e) =>
                                        handleNotificationChange(
                                            "thresholdAmount",
                                            parseInt(e.target.value) || 0
                                        )
                                    }
                                    className="max-w-xs"
                                />
                                <span className="text-sm text-gray-600">
                                    {formatCurrency(settings.notifications.thresholdAmount)}
                                </span>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* System Preferences */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <SettingsIcon className="w-5 h-5 text-gray-600" />
                        <CardTitle>System Preferences</CardTitle>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Default Amount */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Default check amount
                            </label>
                            <Input
                                type="number"
                                value={settings.preferences.defaultAmount}
                                onChange={(e) =>
                                    handlePreferenceChange(
                                        "defaultAmount",
                                        parseInt(e.target.value) || 0
                                    )
                                }
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                Pre-filled in single vendor checks
                            </p>
                        </div>

                        {/* Date Format */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Date format
                            </label>
                            <select
                                value={settings.preferences.dateFormat}
                                onChange={(e) =>
                                    handlePreferenceChange("dateFormat", e.target.value)
                                }
                                className="w-full h-10 px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm cursor-pointer"
                            >
                                <option value="DD/MM/YYYY">DD/MM/YYYY (11/02/2026)</option>
                                <option value="MM/DD/YYYY">MM/DD/YYYY (02/11/2026)</option>
                                <option value="YYYY-MM-DD">YYYY-MM-DD (2026-02-11)</option>
                            </select>
                        </div>

                        {/* Currency Format */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Currency format
                            </label>
                            <select
                                value={settings.preferences.currencyFormat}
                                onChange={(e) =>
                                    handlePreferenceChange("currencyFormat", e.target.value)
                                }
                                className="w-full h-10 px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm cursor-pointer"
                            >
                                <option value="indian">Indian (₹1,00,000)</option>
                                <option value="international">International (₹100,000)</option>
                            </select>
                        </div>

                        {/* Auto Download */}
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-sm font-medium text-gray-700">
                                    Auto-download certificates
                                </div>
                                <div className="text-xs text-gray-500">
                                    Automatically download PDF after check
                                </div>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={settings.preferences.autoDownload}
                                    onChange={(e) =>
                                        handlePreferenceChange("autoDownload", e.target.checked)
                                    }
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                            </label>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* GSTR-2B Integration */}
            <ConnectGST />
        </div>
    );
}
