<script setup lang="ts">
import Alert from "@/components/ui/alert/Alert.vue"
import Button from "@/components/ui/button/Button.vue"
import Card from "@/components/ui/card/Card.vue"
import Checkbox from "@/components/ui/checkbox/Checkbox.vue"
import Input from "@/components/ui/input/Input.vue"
import Label from "@/components/ui/label/Label.vue"
import Select from "@/components/ui/select/Select.vue"
import Textarea from "@/components/ui/textarea/Textarea.vue"

import type { CourseTemplate, CourseTemplateOption } from "@/types/course"

interface ConfigFormState {
  topic: string
  template: CourseTemplate
  use_rag: boolean
  kb_ids: string
  custom_instruction: string
}

defineProps<{
  form: ConfigFormState
  templates: CourseTemplateOption[]
  loadingOutline: boolean
  creatingCourse: boolean
  errorMessage: string
  canGenerateCourse: boolean
}>()

const emit = defineEmits<{
  generateOutline: []
  generateCourse: []
}>()
</script>

<template>
  <Card class="space-y-4">
    <div>
      <h3 class="m-0 text-sm font-semibold">步骤 1：课程配置</h3>
      <p class="m-0 mt-1 text-xs text-muted-foreground">先填写课程信息，再生成大纲和课程内容。</p>
    </div>

    <div>
      <Label class="mb-1 block">课程主题</Label>
      <Input v-model="form.topic" placeholder="例如：Python 编程入门" />
    </div>

    <div>
      <Label class="mb-1 block">课程模板</Label>
      <Select v-model="form.template">
        <option v-for="item in templates" :key="item.id" :value="item.id">
          {{ item.name }}（{{ item.id }}）
        </option>
      </Select>
    </div>

    <div class="rounded-md border border-border bg-muted/40 p-3">
      <Label class="flex items-center gap-2 !text-xs !font-medium text-foreground">
        <Checkbox v-model="form.use_rag" />
        启用 RAG 增强（可选）
      </Label>
      <div class="mt-2">
        <Label class="mb-1 block">知识库文档 ID（逗号分隔）</Label>
        <Input v-model="form.kb_ids" placeholder="doc_id_1,doc_id_2" />
      </div>
    </div>

    <div>
      <Label class="mb-1 block">附加要求</Label>
      <Textarea
        v-model="form.custom_instruction"
        class="min-h-[90px] resize-y"
        placeholder="例如：案例驱动，章节结尾加入练习题"
      />
    </div>

    <div class="flex flex-wrap gap-2">
      <Button variant="secondary" :disabled="loadingOutline" @click="emit('generateOutline')">
        <span v-if="loadingOutline" class="loading-spinner !border-gray-300 !border-t-gray-600" />
        {{ loadingOutline ? "AI 思考中..." : "1. 生成大纲" }}
      </Button>
      <Button :disabled="creatingCourse || !canGenerateCourse" @click="emit('generateCourse')">
        <span v-if="creatingCourse" class="loading-spinner" />
        {{ creatingCourse ? "任务提交中..." : "2. 生成课程" }}
      </Button>
    </div>

    <Alert v-if="errorMessage" variant="destructive">
      {{ errorMessage }}
    </Alert>
  </Card>
</template>
