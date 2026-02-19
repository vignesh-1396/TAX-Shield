"use client";
import { useState, useEffect } from "react";
import Card, { CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { CreditCard, Check, Download, Calendar } from "lucide-react";
import toast from "react-hot-toast";

const PRICING_PLANS = [
    {
        name: "Free Trial",
        price: 0,
        period: "7 days",
        checks: "Unlimited",
        features: [
            "Unlimited compliance checks",
            "Basic reports",
            "Email support",
            "Certificate downloads",
            "Batch upload (up to 100)",
        ],
        cta: "Start Free Trial",
        popular: false,
    },
    {
        name: "Pro",
        price: 2999,
        period: "month",
        checks: "1,000",
        features: [
            "1,000 compliance checks/month",
            "Advanced reports + CSV export",
            "Priority email support",
            "Certificate downloads",
            "Batch upload (up to 500)",
            "Audit trail export",
        ],
        cta: "Upgrade to Pro",
        popular: true,
    },
    {
        name: "Enterprise",
        price: 9999,
        period: "month",
        checks: "Unlimited",
        features: [
            "Unlimited compliance checks",
            "Custom reports + API access",
            "Dedicated account manager",
            "Certificate downloads",
            "Batch upload (unlimited)",
            "Audit trail export",
            "White-label option",
            "Custom integrations",
        ],
        cta: "Upgrade to Enterprise",
        popular: false,
    },
];

const MOCK_INVOICES = [
    { id: "INV-001", date: "2026-01-15", amount: 2999, status: "Paid", plan: "Pro" },
    { id: "INV-002", date: "2025-12-15", amount: 2999, status: "Paid", plan: "Pro" },
    { id: "INV-003", date: "2025-11-15", amount: 2999, status: "Paid", plan: "Pro" },
];

export default function Billing() {
    const [currentPlan, setCurrentPlan] = useState("trial");
    const [trialEndsAt, setTrialEndsAt] = useState(null);
    const [checksUsed, setChecksUsed] = useState(0);
    const [billingCycle, setBillingCycle] = useState("monthly"); // "monthly" | "annual"

    useEffect(() => {
        // Load billing info from localStorage
        const billingInfo = localStorage.getItem("itc_shield_billing");
        if (billingInfo) {
            const data = JSON.parse(billingInfo);
            setCurrentPlan(data.plan || "trial");
            setTrialEndsAt(data.trialEndsAt || null);
        } else {
            // Set trial end date to 7 days from now
            const trialEnd = new Date();
            trialEnd.setDate(trialEnd.getDate() + 7);
            setTrialEndsAt(trialEnd.toISOString());

            localStorage.setItem("itc_shield_billing", JSON.stringify({
                plan: "trial",
                trialEndsAt: trialEnd.toISOString(),
            }));
        }

        // Mock usage data (in production, fetch from API)
        setChecksUsed(245);
    }, []);

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0,
        }).format(amount);
    };

    const getPrice = (monthlyPrice) => {
        if (billingCycle === "annual") {
            // 2 months free per year
            return monthlyPrice * 10;
        }
        return monthlyPrice;
    };

    const getDaysRemaining = () => {
        if (!trialEndsAt) return 0;
        const now = new Date();
        const end = new Date(trialEndsAt);
        const diff = end - now;
        return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
    };

    const getUsagePercentage = () => {
        if (currentPlan === "trial" || currentPlan === "enterprise") return 0;
        if (currentPlan === "pro") return (checksUsed / 1000) * 100;
        return 0;
    };

    const handleUpgrade = (planName) => {
        // Map plan names to internal IDs
        const planMap = {
            "Free Trial": "trial",
            "Pro": "pro",
            "Enterprise": "enterprise"
        };

        const newPlan = planMap[planName] || "trial";
        setCurrentPlan(newPlan);

        // Save to localStorage
        const billingInfo = localStorage.getItem("itc_shield_billing");
        const data = billingInfo ? JSON.parse(billingInfo) : {};
        localStorage.setItem("itc_shield_billing", JSON.stringify({
            ...data,
            plan: newPlan,
        }));

        toast.success(`✓ Selected ${planName} - Payment integration coming soon!`);
    };

    const handleDownloadInvoice = (invoiceId) => {
        toast.success(`Downloading invoice ${invoiceId}...`);
    };

    // Helper to get plan ID from name
    const getPlanId = (planName) => {
        const planMap = {
            "Free Trial": "trial",
            "Pro": "pro",
            "Enterprise": "enterprise"
        };
        return planMap[planName];
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Billing</h1>
                <p className="text-gray-600 mt-1">
                    Manage your subscription and billing information
                </p>
            </div>

            {/* Current Plan */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <CreditCard className="w-5 h-5 text-gray-600" />
                        <CardTitle>Current Plan</CardTitle>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
                        <div className="flex-1">
                            <div className="flex items-baseline gap-3">
                                <h3 className="text-2xl font-bold text-gray-900">
                                    {currentPlan === "trial" ? "Free Trial" : currentPlan === "pro" ? "Pro Plan" : "Enterprise Plan"}
                                </h3>
                                {currentPlan !== "trial" && (
                                    <span className="text-lg text-gray-600">
                                        {currentPlan === "pro" ? formatCurrency(2999) : formatCurrency(9999)}/month
                                    </span>
                                )}
                            </div>

                            {currentPlan === "trial" && (
                                <div className="mt-4">
                                    <div className="flex items-center gap-2 text-orange-600 mb-2">
                                        <Calendar className="w-4 h-4" />
                                        <span className="font-medium">
                                            {getDaysRemaining()} days remaining in trial
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600">
                                        Trial ends on {new Date(trialEndsAt).toLocaleDateString("en-IN", {
                                            day: "numeric",
                                            month: "long",
                                            year: "numeric",
                                        })}
                                    </p>
                                </div>
                            )}

                            {currentPlan === "pro" && (
                                <div className="mt-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm text-gray-600">Usage this month</span>
                                        <span className="text-sm font-medium text-gray-900">
                                            {checksUsed} / 1,000 checks
                                        </span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-blue-600 h-2 rounded-full transition-all"
                                            style={{ width: `${getUsagePercentage()}%` }}
                                        ></div>
                                    </div>
                                    <p className="text-xs text-gray-500 mt-1">
                                        Next billing: {new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toLocaleDateString("en-IN")}
                                    </p>
                                </div>
                            )}
                        </div>

                        <div className="flex gap-3">
                            {currentPlan === "trial" && (
                                <Button onClick={() => handleUpgrade("Pro")}>
                                    Upgrade Now
                                </Button>
                            )}
                            {currentPlan === "pro" && (
                                <Button variant="outline" onClick={() => handleUpgrade("Enterprise")}>
                                    Upgrade to Enterprise
                                </Button>
                            )}
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Pricing Plans */}
            <div>
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-6">
                    <h2 className="text-xl font-bold text-gray-900">Available Plans</h2>

                    {/* Billing Cycle Toggle */}
                    <div className="flex items-center bg-gray-100 p-1 rounded-lg mt-4 md:mt-0 self-start md:self-auto">
                        <button
                            onClick={() => setBillingCycle("monthly")}
                            className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${billingCycle === "monthly"
                                ? "bg-white text-gray-900 shadow-sm"
                                : "text-gray-500 hover:text-gray-900"
                                }`}
                        >
                            Monthly
                        </button>
                        <button
                            onClick={() => setBillingCycle("annual")}
                            className={`px-4 py-2 text-sm font-medium rounded-md transition-all flex items-center gap-2 ${billingCycle === "annual"
                                ? "bg-white text-gray-900 shadow-sm"
                                : "text-gray-500 hover:text-gray-900"
                                }`}
                        >
                            Annual
                            <span className="bg-green-100 text-green-700 text-xs px-1.5 py-0.5 rounded-full">
                                Save 17%
                            </span>
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {PRICING_PLANS.map((plan) => {
                        const isCurrentPlan = currentPlan === getPlanId(plan.name);

                        return (
                            <Card
                                key={plan.name}
                                className={`relative transition-all ${isCurrentPlan
                                    ? "border-2 border-green-600 shadow-lg"
                                    : plan.popular
                                        ? "border-2 border-blue-600"
                                        : "border border-gray-200"
                                    }`}
                            >
                                {isCurrentPlan && (
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                                        <span className="bg-green-600 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1">
                                            <Check className="w-3 h-3" /> Current Plan
                                        </span>
                                    </div>
                                )}
                                {!isCurrentPlan && plan.popular && (
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                                        <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-medium">
                                            Most Popular
                                        </span>
                                    </div>
                                )}
                                <CardContent className="pt-6">
                                    <div className="text-center mb-6">
                                        <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                                        <div className="flex items-baseline justify-center gap-1">
                                            <span className="text-3xl font-bold text-gray-900">
                                                {plan.price === 0
                                                    ? "Free"
                                                    : formatCurrency(getPrice(plan.price))
                                                }
                                            </span>
                                            {plan.price > 0 && (
                                                <span className="text-gray-600">
                                                    /{billingCycle === "annual" ? "year" : "month"}
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-sm text-gray-600 mt-1">{plan.checks} checks</p>

                                        {/* Annual Savings Text */}
                                        {billingCycle === "annual" && plan.price > 0 && (
                                            <p className="text-xs text-green-600 font-medium mt-2">
                                                Save {formatCurrency(plan.price * 2)}/year (2 months free!)
                                            </p>
                                        )}
                                    </div>

                                    <ul className="space-y-3 mb-6">
                                        {plan.features.map((feature, idx) => (
                                            <li key={idx} className="flex items-start gap-2">
                                                <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                                                <span className="text-sm text-gray-700">{feature}</span>
                                            </li>
                                        ))}
                                    </ul>

                                    <Button
                                        onClick={() => handleUpgrade(plan.name)}
                                        variant={
                                            isCurrentPlan
                                                ? "outline"
                                                : (plan.name === "Free Trial" || plan.name === "Enterprise" || plan.popular)
                                                    ? "primary"
                                                    : "outline"
                                        }
                                        className="w-full"
                                    >
                                        {isCurrentPlan ? "✓ Current Plan" : plan.cta}
                                    </Button>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            </div>

            {/* Payment History */}
            <Card>
                <CardHeader>
                    <CardTitle>Payment History</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200">
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                        Invoice
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                        Date
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                        Plan
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                        Amount
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                        Status
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                                        Action
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {MOCK_INVOICES.map((invoice) => (
                                    <tr key={invoice.id} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="py-3 px-4 text-sm font-mono">{invoice.id}</td>
                                        <td className="py-3 px-4 text-sm">
                                            {new Date(invoice.date).toLocaleDateString("en-IN")}
                                        </td>
                                        <td className="py-3 px-4 text-sm">{invoice.plan}</td>
                                        <td className="py-3 px-4 text-sm font-medium">
                                            {formatCurrency(invoice.amount)}
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                {invoice.status}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4">
                                            <button
                                                onClick={() => handleDownloadInvoice(invoice.id)}
                                                className="text-blue-600 hover:text-blue-700 text-sm flex items-center gap-1"
                                            >
                                                <Download className="w-4 h-4" />
                                                Download
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
