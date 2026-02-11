import { cn } from "@/lib/utils";

export default function Card({ children, className, ...props }) {
    return (
        <div
            className={cn(
                "bg-white rounded-lg border border-gray-200 shadow-sm",
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
}

export function CardHeader({ children, className }) {
    return (
        <div className={cn("px-6 py-4 border-b border-gray-200", className)}>
            {children}
        </div>
    );
}

export function CardContent({ children, className }) {
    return <div className={cn("px-6 py-4", className)}>{children}</div>;
}

export function CardTitle({ children, className }) {
    return (
        <h3 className={cn("text-lg font-semibold text-gray-900", className)}>
            {children}
        </h3>
    );
}
