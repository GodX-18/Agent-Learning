<script setup lang="ts">
import ChapterEditor from "@/components/course/ChapterEditor.vue"
import ChapterList from "@/components/course/ChapterList.vue"
import { getDownloadUrl } from "@/lib/api"
import type { CourseTreeNode } from "@/types/course"

defineProps<{
  tree: CourseTreeNode[]
  selectedPath: string
  selectedMarkdown: string
  taskId: string
  status: "idle" | "running" | "completed" | "failed"
}>()

const emit = defineEmits<{
  selectFile: [path: string]
}>()
</script>

<template>
  <section class="grid h-full grid-rows-[auto_1fr] gap-3">
    <div class="panel flex flex-wrap items-center justify-between gap-2">
      <div>
        <h3 class="m-0 text-sm font-semibold">步骤 3：课程预览</h3>
        <p class="m-0 mt-1 text-xs text-muted-foreground">浏览生成文件并校验 Markdown 内容。</p>
      </div>
      <a
        v-if="taskId && status === 'completed'"
        class="btn-secondary no-underline"
        :href="getDownloadUrl(taskId)"
        target="_blank"
      >
        下载课程 ZIP
      </a>
    </div>

    <div v-if="tree.length === 0" class="panel flex items-center justify-center">
      <p class="m-0 text-sm text-muted-foreground">暂无可预览内容，请先完成课程生成。</p>
    </div>
    <div v-else class="grid h-full grid-cols-[260px_1fr] gap-3">
      <ChapterList :tree="tree" :selected-path="selectedPath" @select="(path) => emit('selectFile', path)" />
      <ChapterEditor :path="selectedPath" :content="selectedMarkdown" />
    </div>
  </section>
</template>
