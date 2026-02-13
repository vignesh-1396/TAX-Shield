import { cn } from "@/lib/utils";

export default function Input({ className, error, ...props }) {
    return (
        <input
            className={cn(
                "w-full px-3 py-2 text-sm border rounded-lg transition-colors bg-white text-gray-900 placeholder:text-gray-400",
                "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                "disabled:bg-gray-50 disabled:cursor-not-allowed",
                error ? "border-red-300 focus:ring-red-500" : "border-gray-300",
                className
            )}
            {...props}
        />
    );
}
