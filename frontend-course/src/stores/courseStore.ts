import { defineStore } from "pinia"
import { ref } from "vue"

import {
  createOutline,
  fetchTemplates,
  generateCourse,
  getCourseResult,
  getStatusSseUrl,
  updateOutline,
} from "@/lib/api"
import type {
  CourseHistoryItem,
  CourseOutline,
  CourseResult,
  CourseTemplate,
  CourseTemplateOption,
} from "@/types/course"

const HISTORY_KEY = "course-history-v1"

export const useCourseStore = defineStore("course", () => {
  const templates = ref<CourseTemplateOption[]>([])
  const outline = ref<CourseOutline | null>(null)
  const result = ref<CourseResult | null>(null)
  const currentTaskId = ref("")
  const status = ref<"idle" | "running" | "completed" | "failed">("idle")
  const progressText = ref("")
  const errorMessage = ref("")
  const history = ref<CourseHistoryItem[]>([])
  const selectedFile = ref<string>("README.md")

  let eventSource: EventSource | null = null

  function loadHistory() {
    try {
      const raw = localStorage.getItem(HISTORY_KEY)
      history.value = raw ? (JSON.parse(raw) as CourseHistoryItem[]) : []
    } catch {
      history.value = []
    }
  }

  function saveHistory(item: CourseHistoryItem) {
    history.value = [item, ...history.value.filter((x) => x.taskId !== item.taskId)].slice(0, 30)
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history.value))
  }

  async function loadTemplates() {
    const data = await fetchTemplates()
    templates.value = data.templates
  }

  async function generateOutline(params: {
    topic: string
    template: CourseTemplate
    use_rag: boolean
    kb_ids: string[]
    custom_instruction: string
  }) {
    errorMessage.value = ""
    try {
      const data = await createOutline(params)
      outline.value = data.outline
      await updateOutline({ outline: data.outline })
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err)
      if (msg.includes("503") || msg.includes("繁忙") || msg.includes("overloaded")) {
        errorMessage.value = "模型服务当前繁忙，请稍后重试。"
      } else {
        errorMessage.value = `大纲生成失败：${msg.slice(0, 200)}`
      }
      throw err
    }
  }

  function closeStatusStream() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
  }

  function watchTask(taskId: string) {
    closeStatusStream()
    currentTaskId.value = taskId
    status.value = "running"
    progressText.value = "任务已启动"

    eventSource = new EventSource(getStatusSseUrl(taskId))
    eventSource.addEventListener("progress", (event) => {
      const data = JSON.parse((event as MessageEvent).data) as Record<string, string>
      progressText.value = data.message ?? `${data.current ?? ""}/${data.total ?? ""} ${data.chapter ?? ""}`
    })
    eventSource.addEventListener("done", async () => {
      status.value = "completed"
      progressText.value = "生成完成"
      closeStatusStream()
      await loadResult(taskId)
    })
    eventSource.addEventListener("error", (event) => {
      status.value = "failed"
      try {
        const parsed = JSON.parse((event as MessageEvent).data ?? "{}")
        errorMessage.value = parsed.error ?? "任务失败"
      } catch {
        errorMessage.value = (event as MessageEvent).data || "任务失败"
      }
      progressText.value = ""
      closeStatusStream()
    })
  }

  async function startGenerate(params: {
    topic: string
    template: CourseTemplate
    use_rag: boolean
    kb_ids: string[]
    custom_instruction: string
    outline?: CourseOutline
  }) {
    errorMessage.value = ""
    const data = await generateCourse(params)
    watchTask(data.task_id)
  }

  async function loadResult(taskId: string) {
    const data = await getCourseResult(taskId)
    result.value = data
    outline.value = data.outline
    if (data.markdown_files["README.md"]) {
      selectedFile.value = "README.md"
    } else {
      selectedFile.value = Object.keys(data.markdown_files)[0] ?? ""
    }
    saveHistory({
      taskId,
      title: data.outline.title,
      topic: String(data.meta.topic ?? ""),
      createdAt: new Date().toISOString(),
    })
  }

  return {
    templates,
    outline,
    result,
    currentTaskId,
    status,
    progressText,
    errorMessage,
    history,
    selectedFile,
    loadHistory,
    loadTemplates,
    generateOutline,
    startGenerate,
    loadResult,
    closeStatusStream,
  }
})
