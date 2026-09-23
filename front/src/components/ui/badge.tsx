import type * as React from "react"
import { cn } from "@/lib/utils"

function Badge({ className, ...props }: React.ComponentProps<"span">) {
  return <span data-slot="badge" className={cn("inline-flex items-center rounded-sm border px-2 py-1 text-xs font-medium", className)} {...props} />
}

export { Badge }
