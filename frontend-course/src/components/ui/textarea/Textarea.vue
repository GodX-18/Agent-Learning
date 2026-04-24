<script setup lang="ts">
import { cn } from "@/lib/utils"

const model = defineModel<string>({ default: "" })
</script>

<template>
  <textarea
    v-model="model"
    :class="
      cn(
        'flex min-h-[80px] w-full rounded-md border border-border bg-white px-3 py-2 text-sm shadow-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
      )
    "
    v-bind="$attrs"
  />
</template>
