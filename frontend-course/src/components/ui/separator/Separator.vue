<script setup lang="ts">
import { computed } from "vue"

import { cn } from "@/lib/utils"

const props = withDefaults(
  defineProps<{
    orientation?: "horizontal" | "vertical"
  }>(),
  {
    orientation: "horizontal",
  },
)

const className = computed(() =>
  props.orientation === "horizontal" ? "h-px w-full bg-border" : "h-full w-px bg-border",
)
</script>

<template>
  <div :class="cn('shrink-0', className)" aria-hidden="true" />
</template>
