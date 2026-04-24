<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue"

import Button from "@/components/ui/button/Button.vue"
import Card from "@/components/ui/card/Card.vue"
import ConfigPanel from "@/components/course/ConfigPanel.vue"
import LoadingOverlay from "@/components/course/LoadingOverlay.vue"
import OutlineEditor from "@/components/course/OutlineEditor.vue"
import PreviewPanel from "@/components/course/PreviewPanel.vue"
import StepIndicator from "@/components/course/StepIndicator.vue"
import { useCourseStore } from "@/stores/courseStore"
import type { CourseTemplate } from "@/types/course"

const store = useCourseStore()

const form = reactive({
  topic: "",
  template: "standard" as CourseTemplate,
  use_rag: false,
  kb_ids: "",
  custom_instruction: "",
})

const currentStep = ref<1 | 2 | 3>(1)
const loadingOutline = ref(false)
const creatingCourse = ref(false)

const canGenerateCourse = computed(() => Boolean(form.topic.trim() && store.outline))
const selectedMarkdown = computed(() => {
  if (!store.result || !store.selectedFile) return ""
  return store.result.markdown_files[store.selectedFile] ?? ""
})
const showOverlay = computed(() => creatingCourse.value || store.status === "running")
const overlayDescription = computed(() => {
  if (store.progressText) return store.progressText
  return "课程生成中，系统会持续同步进度。"
})

watch(
  () => store.outline,
  (nextOutline) => {
    if (nextOutline && currentStep.value < 2) {
      currentStep.value = 2
    }
  },
)

watch(
  () => store.result,
  (nextResult) => {
    if (nextResult) {
      currentStep.value = 3
    }
  },
)

async function onGenerateOutline() {
  loadingOutline.value = true
  try {
    await store.generateOutline({
      topic: form.topic,
      template: form.template,
      use_rag: form.use_rag,
      kb_ids: form.kb_ids.split(",").map((x) => x.trim()).filter(Boolean),
      custom_instruction: form.custom_instruction,
    })
    currentStep.value = 2
  } finally {
    loadingOutline.value = false
  }
}

async function onGenerateCourse() {
  creatingCourse.value = true
  try {
    await store.startGenerate({
      topic: form.topic,
      template: form.template,
      use_rag: form.use_rag,
      kb_ids: form.kb_ids.split(",").map((x) => x.trim()).filter(Boolean),
      custom_instruction: form.custom_instruction,
      outline: store.outline ?? undefined,
    })
    currentStep.value = 3
  } finally {
    creatingCourse.value = false
  }
}
</script>

<template>
  <div class="grid h-full grid-rows-[auto_1fr] gap-4 p-4">
    <StepIndicator :current-step="currentStep" />

    <section class="overflow-hidden">
      <div v-if="currentStep === 1" class="mx-auto max-w-4xl">
        <ConfigPanel
          :form="form"
          :templates="store.templates"
          :loading-outline="loadingOutline"
          :creating-course="creatingCourse"
          :error-message="store.errorMessage"
          :can-generate-course="canGenerateCourse"
          @generate-outline="onGenerateOutline"
          @generate-course="onGenerateCourse"
        />
      </div>

      <div v-else-if="currentStep === 2" class="grid h-full gap-3 overflow-auto">
        <Card class="flex flex-wrap items-center justify-between gap-2 shrink-0">
          <div>
            <h3 class="m-0 text-sm font-semibold">步骤 2：大纲优化</h3>
            <p class="m-0 mt-1 text-xs text-muted-foreground">编辑章节结构后即可生成完整课程。</p>
          </div>
          <div class="flex gap-2">
            <Button variant="secondary" @click="currentStep = 1">返回配置</Button>
            <Button :disabled="creatingCourse || !canGenerateCourse" @click="onGenerateCourse">
              <span v-if="creatingCourse" class="loading-spinner" />
              {{ creatingCourse ? "任务提交中..." : "生成课程内容" }}
            </Button>
          </div>
        </Card>
        <OutlineEditor v-model="store.outline" />
      </div>

      <div v-else class="h-full">
        <PreviewPanel
          :tree="store.result?.tree ?? []"
          :selected-path="store.selectedFile"
          :selected-markdown="selectedMarkdown"
          :task-id="store.currentTaskId"
          :status="store.status"
          @select-file="(path) => (store.selectedFile = path)"
        />
      </div>
    </section>
  </div>

  <LoadingOverlay
    :visible="showOverlay"
    title="课程生成中"
    :description="overlayDescription"
    :can-cancel="false"
  />
</template>
