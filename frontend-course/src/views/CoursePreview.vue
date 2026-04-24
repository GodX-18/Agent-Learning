<script setup lang="ts">
import { computed } from "vue"
import { marked } from "marked"
import { useCourseStore } from "@/stores/courseStore"

const store = useCourseStore()
const html = computed(() => {
  if (!store.result || !store.selectedFile) return "<p>暂无预览内容</p>"
  const content = store.result.markdown_files[store.selectedFile] ?? ""
  return marked.parse(content)
})
</script>

<template>
  <main class="mx-auto max-w-5xl p-6">
    <h1 class="text-xl">{{ store.outline?.title || "课程预览" }}</h1>
    <article class="prose max-w-none" v-html="html" />
  </main>
</template>
