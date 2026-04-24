<script setup lang="ts">
import type { CourseTreeNode } from "@/types/course"

defineProps<{
  tree: CourseTreeNode[]
  selectedPath: string
}>()

const emit = defineEmits<{
  select: [path: string]
}>()

function selectFile(path: string) {
  emit("select", path)
}
</script>

<template>
  <section class="panel h-full overflow-auto">
    <h3 class="m-0 mb-2 text-sm font-semibold">文件树</h3>
    <ul class="m-0 space-y-1 p-0 text-xs">
      <li v-for="root in tree" :key="root.path">
        <details open>
          <summary class="cursor-pointer">{{ root.name }}</summary>
          <ul class="ml-4 mt-1 space-y-1 p-0">
            <template v-for="child in root.children ?? []" :key="child.path">
              <li v-if="child.type === 'directory'">
                <details open>
                  <summary class="cursor-pointer">{{ child.name }}</summary>
                  <ul class="ml-4 mt-1 space-y-1 p-0">
                    <li v-for="file in child.children ?? []" :key="file.path">
                      <button
                        class="rounded px-1 py-0.5"
                        :class="selectedPath === file.path ? 'bg-muted font-semibold' : 'hover:bg-muted/70'"
                        @click="selectFile(file.path)"
                      >
                        {{ file.name }}
                      </button>
                    </li>
                  </ul>
                </details>
              </li>
              <li v-else>
                <button
                  class="rounded px-1 py-0.5"
                  :class="selectedPath === child.path ? 'bg-muted font-semibold' : 'hover:bg-muted/70'"
                  @click="selectFile(child.path)"
                >
                  {{ child.name }}
                </button>
              </li>
            </template>
          </ul>
        </details>
      </li>
    </ul>
  </section>
</template>
