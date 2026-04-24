<script setup lang="ts">
import { computed } from "vue"

const model = defineModel<boolean>({ default: false })

const proxyModel = computed({
  get: () => model.value,
  set: (value: boolean | string) => {
    model.value = Boolean(value)
  },
})
</script>

<template>
  <input
    v-model="proxyModel"
    type="checkbox"
    class="h-4 w-4 rounded border-border text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    v-bind="$attrs"
  />
</template>
