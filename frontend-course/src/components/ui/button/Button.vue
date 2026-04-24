<script setup lang="ts">
import { cva, type VariantProps } from "class-variance-authority"
import { computed } from "vue"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-md text-xs font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-60",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:opacity-90",
        secondary: "border border-border bg-white text-foreground hover:bg-muted",
        outline: "border border-border bg-transparent text-foreground hover:bg-muted",
        destructive: "bg-red-600 text-white hover:bg-red-700",
      },
      size: {
        sm: "h-8 px-3",
        default: "h-9 px-4",
        lg: "h-10 px-6",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
)

type ButtonVariants = VariantProps<typeof buttonVariants>

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariants["variant"]
    size?: ButtonVariants["size"]
    type?: "button" | "submit" | "reset"
  }>(),
  {
    variant: "default",
    size: "default",
    type: "button",
  },
)

const className = computed(() => buttonVariants({ variant: props.variant, size: props.size }))
</script>

<template>
  <button :type="type" :class="cn(className)" v-bind="$attrs">
    <slot />
  </button>
</template>
