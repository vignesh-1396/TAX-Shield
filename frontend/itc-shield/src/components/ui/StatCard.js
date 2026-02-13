import Card from "./Card";
import { cn } from "@/lib/utils";

export default function StatCard({ title, value, change, icon: Icon, trend }) {
    return (
        <Card className="p-6">
            <div className="flex items-center justify-between">
                <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600">{title}</p>
                    <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
                    {change && (
                        <p
                            className={cn(
                                "mt-2 text-sm font-medium",
                                trend === "up" ? "text-green-600" : "text-red-600"
                            )}
                        >
                            {change}
                        </p>
                    )}
                </div>
                {Icon && (
                    <div className="flex-shrink-0">
                        <div className="p-3 bg-blue-50 rounded-lg">
                            <Icon className="w-6 h-6 text-blue-600" />
                        </div>
                    </div>
                )}
            </div>
        </Card>
    );
}
