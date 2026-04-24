<script setup lang="ts">
import { computed } from "vue"

import Button from "@/components/ui/button/Button.vue"
import Card from "@/components/ui/card/Card.vue"
import Input from "@/components/ui/input/Input.vue"
import Label from "@/components/ui/label/Label.vue"
import Textarea from "@/components/ui/textarea/Textarea.vue"

import type { CourseOutline } from "@/types/course"

const props = defineProps<{
  modelValue: CourseOutline | null
}>()

const emit = defineEmits<{
  "update:modelValue": [value: CourseOutline | null]
}>()

const outline = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
})

function addChapter() {
  if (!outline.value) return
  const index = outline.value.chapters.length + 1
  outline.value.chapters.push({
    id: `ch${index}`,
    title: `第${index}章`,
    summary: "",
    sections: [],
  })
}

function removeChapter(index: number) {
  if (!outline.value) return
  outline.value.chapters.splice(index, 1)
}

function addSection(chapterIndex: number) {
  if (!outline.value) return
  const chapter = outline.value.chapters[chapterIndex]
  const index = chapter.sections.length + 1
  chapter.sections.push({
    id: `${chapter.id}-s${index}`,
    title: `小节 ${index}`,
    goals: ["学习目标"],
  })
}

function removeSection(chapterIndex: number, sectionIndex: number) {
  if (!outline.value) return
  outline.value.chapters[chapterIndex].sections.splice(sectionIndex, 1)
}
</script>

<template>
  <Card>
    <div class="mb-3 flex items-center justify-between">
      <h3 class="m-0 text-sm font-semibold">大纲编辑器</h3>
      <Button variant="secondary" size="sm" @click="addChapter">新增章节</Button>
    </div>
    <p v-if="!outline" class="m-0 text-sm text-muted-foreground">先生成大纲后再编辑。</p>
    <div v-else class="space-y-3">
      <div class="grid gap-2">
        <Label>课程标题</Label>
        <Input v-model="outline.title" />
      </div>

      <div
        v-for="(chapter, chapterIndex) in outline.chapters"
        :key="chapter.id"
        class="rounded border border-border p-3"
      >
        <div class="mb-2 flex items-center gap-2">
          <Input v-model="chapter.title" class="flex-1" />
          <Button variant="secondary" size="sm" @click="addSection(chapterIndex)">新增小节</Button>
          <Button variant="destructive" size="sm" @click="removeChapter(chapterIndex)">删除章</Button>
        </div>
        <Textarea
          v-model="chapter.summary"
          class="mb-2 text-xs"
          :rows="2"
          placeholder="章节概述"
        />
        <div class="space-y-2">
          <div
            v-for="(section, sectionIndex) in chapter.sections"
            :key="section.id"
            class="rounded border border-dashed px-2 py-2"
          >
            <div class="flex items-center gap-2">
              <Input v-model="section.title" class="h-8 flex-1 text-xs" />
              <Button variant="outline" size="sm" @click="removeSection(chapterIndex, sectionIndex)">删除</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Card>
</template>
