import { cn } from "@/lib/utils";

interface NuminaButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "destructive";
}

export function NuminaButton({
  className,
  variant = "primary",
  children,
  ...props
}: NuminaButtonProps) {
  const base =
    "relative overflow-hidden rounded-xl px-5 py-2.5 font-medium text-white transition-all duration-200 active:scale-[0.97]";

  const variantStyles = {
    primary: "bg-[#4f46e5] hover:brightness-110",
    destructive: "bg-[#ef4444] hover:brightness-110",
  };

  const shadowStyle = {
    boxShadow:
      "6px 6px 12px var(--neu-shadow-dark), -6px -6px 12px var(--neu-shadow-light)",
  };

  return (
    <button
      className={cn(base, variantStyles[variant], "tech-btn-shimmer", className)}
      style={shadowStyle}
      {...props}
    >
      {children}
    </button>
  );
}
