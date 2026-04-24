<script setup lang="ts">
import { ref, computed } from "vue"
import { marked } from "marked"

const props = defineProps<{
  path: string
  content: string
}>()

marked.setOptions({
  breaks: true,
  gfm: true,
})

const rendered = computed(() => marked.parse(props.content ?? ""))

type Tab = "preview" | "source"
const activeTab = ref<Tab>("preview")
</script>

<template>
  <section class="panel flex h-full flex-col overflow-hidden">
    <div class="mb-2 flex items-center justify-between shrink-0">
      <h3 class="m-0 text-sm font-semibold">{{ path || "未选择文件" }}</h3>
      <div class="flex rounded-md border p-0.5">
        <button
          class="rounded px-3 py-1 text-xs transition-colors"
          :class="activeTab === 'preview' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'"
          @click="activeTab = 'preview'"
        >
          预览
        </button>
        <button
          class="rounded px-3 py-1 text-xs transition-colors"
          :class="activeTab === 'source' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'"
          @click="activeTab = 'source'"
        >
          原文
        </button>
      </div>
    </div>

    <div class="min-h-0 flex-1 overflow-hidden">
      <div v-show="activeTab === 'preview'" class="h-full overflow-auto rounded border p-3">
        <article class="prose prose-sm max-w-none" v-html="rendered" />
      </div>
      <pre
        v-show="activeTab === 'source'"
        class="h-full overflow-auto whitespace-pre-wrap rounded border p-2 text-xs"
      >{{ content }}</pre>
    </div>
  </section>
</template>
