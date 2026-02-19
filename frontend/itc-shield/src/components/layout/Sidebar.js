"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    Users,
    FileText,
    Settings,
    Shield,
    CreditCard,
    RefreshCcw
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Reconciliation", href: "/reconciliation", icon: RefreshCcw },
    { name: "Reports", href: "/reports", icon: FileText },
    { name: "Billing", href: "/billing", icon: CreditCard },
    { name: "Settings", href: "/settings", icon: Settings },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <div className="flex flex-col w-64 bg-white border-r border-gray-200 h-screen">
            {/* Logo */}
            <div className="flex items-center h-16 px-6 border-b border-gray-200">
                <Shield className="w-8 h-8 text-blue-600" />
                <span className="ml-2 text-xl font-semibold text-gray-900">ITC Shield</span>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
                {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            className={cn(
                                "flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                                isActive
                                    ? "bg-blue-50 text-blue-700"
                                    : "text-gray-700 hover:bg-gray-50"
                            )}
                        >
                            <item.icon className="w-5 h-5 mr-3" />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200">
                <div className="text-xs text-gray-500">
                    © 2026 ITC Shield
                </div>
            </div>
        </div>
    );
}
