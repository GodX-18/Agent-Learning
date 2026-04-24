<script setup lang="ts">
import { cva, type VariantProps } from "class-variance-authority"
import { computed } from "vue"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground",
        secondary: "border-transparent bg-muted text-muted-foreground",
        success: "border-transparent bg-emerald-500 text-white",
        outline: "border-border text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

type BadgeVariants = VariantProps<typeof badgeVariants>

const props = withDefaults(
  defineProps<{
    variant?: BadgeVariants["variant"]
  }>(),
  {
    variant: "default",
  },
)

const className = computed(() => badgeVariants({ variant: props.variant }))
</script>

<template>
  <span :class="cn(className)">
    <slot />
  </span>
</template>
