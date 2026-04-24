<script setup lang="ts">
import { onMounted } from "vue"

import CourseGenerator from "@/components/course/CourseGenerator.vue"
import AppHeader from "@/components/layout/AppHeader.vue"
import AppSidebar from "@/components/layout/AppSidebar.vue"
import { useCourseStore } from "@/stores/courseStore"

const store = useCourseStore()

onMounted(async () => {
  store.loadHistory()
  await store.loadTemplates()
})
</script>

<template>
  <div class="grid h-full grid-rows-[auto_1fr] bg-slate-50">
    <AppHeader />
    <div class="grid h-full grid-cols-[260px_1fr] overflow-hidden">
      <AppSidebar :items="store.history" @select="store.loadResult" />
      <main class="h-full overflow-hidden">
        <CourseGenerator />
      </main>
    </div>
  </div>
</template>
