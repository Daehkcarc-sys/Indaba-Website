import * as React from 'react'
import { Tabs as Primitive } from '@base-ui/react/tabs'
import { cn } from '@/lib/utils'

function Tabs(props: React.ComponentProps<typeof Primitive.Root>) {
  return <Primitive.Root data-slot="tabs" {...props} />
}
function TabsList({className,...props}: React.ComponentProps<typeof Primitive.List>) {
  return <Primitive.List data-slot="tabs-list" className={cn(className)} {...props} />
}
function TabsTrigger({className,...props}: React.ComponentProps<typeof Primitive.Tab>) {
  return <Primitive.Tab data-slot="tabs-trigger" className={cn(className)} {...props} />
}
function TabsContent({className,...props}: React.ComponentProps<typeof Primitive.Panel>) {
  return <Primitive.Panel data-slot="tabs-content" className={cn(className)} {...props} />
}
export {Tabs,TabsList,TabsTrigger,TabsContent}
