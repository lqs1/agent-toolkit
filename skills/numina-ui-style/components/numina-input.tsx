import { cn } from "@/lib/utils";

interface NuminaInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

export function NuminaInput({ className, ...props }: NuminaInputProps) {
  return (
    <input
      className={cn(
        "numina-input rounded-xl border-0 bg-card px-4 py-2.5 text-foreground placeholder:text-muted-foreground",
        "transition-all duration-200",
        className
      )}
      style={{ boxShadow: "var(--neu-pressed-sm)" }}
      {...props}
    />
  );
}
