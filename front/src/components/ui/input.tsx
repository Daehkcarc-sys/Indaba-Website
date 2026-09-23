import * as React from 'react'
import { cn } from '@/lib/utils'

function Input({className,...props}:React.ComponentProps<'input'>){return <input data-slot="input" className={cn('h-9 min-w-0 rounded-md border border-input bg-transparent px-3 text-sm text-foreground shadow-xs outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50',className)} {...props}/>}
export {Input}
