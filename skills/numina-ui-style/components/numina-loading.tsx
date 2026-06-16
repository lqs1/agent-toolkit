import { cn } from "@/lib/utils";

interface NuminaLoadingProps
  extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "aurora" | "soft";
  label?: string;
}

export function NuminaLoading({
  className,
  variant = "aurora",
  label = "加载中...",
  children,
  ...props
}: NuminaLoadingProps) {
  return (
    <div
      className={cn(
        "flex min-h-[120px] flex-col items-center justify-center rounded-xl text-center",
        variant === "aurora" && "numina-loading-aurora text-white/80",
        variant === "soft" && "numina-loading-aurora-soft text-foreground",
        className
      )}
      {...props}
    >
      <div className="relative z-10 flex flex-col items-center gap-3">
        <div
          className="h-8 w-8 animate-spin rounded-full border-2 border-current border-t-transparent"
          aria-hidden="true"
        />
        {label && <span className="text-sm font-medium">{label}</span>}
      </div>
      {children}
    </div>
  );
}

interface NuminaSkeletonProps
  extends React.HTMLAttributes<HTMLDivElement> {
  height?: string;
  width?: string;
}

export function NuminaSkeleton({
  className,
  height = "1rem",
  width = "100%",
  style,
  ...props
}: NuminaSkeletonProps) {
  return (
    <div
      className={cn("numina-skeleton", className)}
      style={{ height, width, ...style }}
      {...props}
    />
  );
}

interface NuminaLoadingBarProps
  extends React.HTMLAttributes<HTMLDivElement> {}

export function NuminaLoadingBar({
  className,
  ...props
}: NuminaLoadingBarProps) {
  return (
    <div
      className={cn("numina-loading-bar", className)}
      role="progressbar"
      aria-busy="true"
      aria-label="Loading"
      {...props}
    />
  );
}
