<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { computed, inject } from 'vue'

interface Props {
  class?: HTMLAttributes['class']
}

const props = defineProps<Props>()
const from = inject<string>('messageFrom', 'assistant')
const isUser = computed(() => from === 'user')
</script>

<template>
  <div
    :class="
      cn(
        'flex w-fit flex-col gap-2 overflow-hidden text-sm text-foreground',
        isUser
          ? 'ml-auto rounded-xl bg-indigo-600 px-4 py-3 text-white'
          : 'w-full rounded-xl bg-secondary/50 px-4 py-3 border border-border/50',
        props.class,
      )
    "
    v-bind="$attrs"
  >
    <slot />
  </div>
</template>
