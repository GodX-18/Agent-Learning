<script setup lang="ts">
import type { CourseHistoryItem } from "@/types/course"

defineProps<{
  items: CourseHistoryItem[]
}>()

const emit = defineEmits<{
  select: [taskId: string]
}>()

function onSelect(taskId: string) {
  emit("select", taskId)
}
</script>

<template>
  <aside class="h-full border-r border-slate-900/20 p-3 text-[var(--sidebar-text)]" style="background: var(--sidebar-bg);">
    <div class="mb-4 rounded-xl border border-white/10 bg-white/5 p-3">
      <h2 class="m-0 text-sm font-semibold text-[var(--sidebar-text)]">历史课程</h2>
      <p class="m-0 mt-1 text-[11px] text-[var(--sidebar-text-muted)]">点击任意任务可快速载入预览内容</p>
    </div>
    <div v-if="items.length === 0" class="rounded-xl border border-white/10 bg-white/5 p-3 text-xs text-[var(--sidebar-text-muted)]">
      暂无历史记录，先生成一门课程吧。
    </div>
    <div v-else class="space-y-2">
      <button
        v-for="item in items"
        :key="item.taskId"
        class="w-full rounded-lg border border-white/10 px-3 py-2 text-left text-xs transition hover:translate-x-0.5 hover:brightness-110"
        style="background: var(--sidebar-surface); color: var(--sidebar-text);"
        @click="onSelect(item.taskId)"
      >
        <p class="m-0 font-medium">{{ item.title }}</p>
        <p class="m-0 mt-1 text-[11px] text-[var(--sidebar-text-muted)]">{{ item.topic || "无主题" }}</p>
      </button>
    </div>
  </aside>
</template>
