<script setup lang="ts">
import { cva, type VariantProps } from "class-variance-authority"
import { computed } from "vue"

import { cn } from "@/lib/utils"

const alertVariants = cva("rounded-md border px-3 py-2 text-xs", {
  variants: {
    variant: {
      default: "border-border bg-muted/40 text-foreground",
      destructive: "border-red-200 bg-red-50 text-red-600",
    },
  },
  defaultVariants: {
    variant: "default",
  },
})

type AlertVariants = VariantProps<typeof alertVariants>

const props = withDefaults(
  defineProps<{
    variant?: AlertVariants["variant"]
  }>(),
  {
    variant: "default",
  },
)

const className = computed(() => alertVariants({ variant: props.variant }))
</script>

<template>
  <div :class="cn(className)">
    <slot />
  </div>
</template>
