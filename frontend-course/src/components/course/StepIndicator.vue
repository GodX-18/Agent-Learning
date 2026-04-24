<script setup lang="ts">
import { computed } from "vue"

import Badge from "@/components/ui/badge/Badge.vue"
import Card from "@/components/ui/card/Card.vue"
import Separator from "@/components/ui/separator/Separator.vue"

const props = defineProps<{
  currentStep: 1 | 2 | 3
}>()

const steps = [
  { id: 1, title: "课程配置", description: "填写主题与生成参数" },
  { id: 2, title: "大纲优化", description: "检查并调整章节结构" },
  { id: 3, title: "课程预览", description: "浏览文件并导出内容" },
] as const

function getStepState(stepId: number) {
  if (stepId < props.currentStep) return "complete"
  if (stepId === props.currentStep) return "active"
  return "pending"
}

const completion = computed(() => `${Math.round((props.currentStep / 3) * 100)}%`)

function getStepBadgeVariant(stepId: number) {
  const state = getStepState(stepId)
  if (state === "complete") return "success"
  if (state === "active") return "default"
  return "secondary"
}
</script>

<template>
  <Card>
    <div class="mb-4 flex items-center justify-between">
      <h3 class="m-0 text-sm font-semibold">生成流程</h3>
      <Badge variant="outline">完成度 {{ completion }}</Badge>
    </div>
    <div class="grid gap-3 md:grid-cols-3">
      <div v-for="(step, index) in steps" :key="step.id" class="flex items-start gap-3">
        <Badge
          class="mt-0.5 h-6 w-6 justify-center rounded-full p-0 text-[10px]"
          :variant="getStepBadgeVariant(step.id)"
        >
          <span v-if="getStepState(step.id) === 'complete'">✓</span>
          <span v-else>{{ step.id }}</span>
        </Badge>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <p class="m-0 text-sm font-semibold">{{ step.title }}</p>
            <Badge v-if="getStepState(step.id) === 'active'" variant="default">进行中</Badge>
            <Badge v-else-if="getStepState(step.id) === 'complete'" variant="success">已完成</Badge>
            <Badge v-else variant="secondary">待开始</Badge>
          </div>
          <p class="m-0 mt-1 text-xs text-muted-foreground">{{ step.description }}</p>
        </div>
        <Separator v-if="index < steps.length - 1" orientation="vertical" class="hidden md:block" />
      </div>
    </div>
  </Card>
</template>
