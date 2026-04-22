<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { uploadDocument, fetchDocuments, deleteDocument, type Document } from '../api'

const documents = ref<Document[]>([])
const uploading = ref(false)
const error = ref('')
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement>()

const emit = defineEmits<{
  upload: [doc: Document & { chunks: number }]
}>()

async function loadDocuments() {
  try {
    documents.value = await fetchDocuments()
  } catch (e: any) {
    error.value = e.message
  }
}

async function handleFiles(files: FileList | null) {
  if (!files || files.length === 0) return
  error.value = ''
  uploading.value = true

  try {
    for (const file of Array.from(files)) {
      const result = await uploadDocument(file)
      emit('upload', result)
      await loadDocuments()
    }
  } catch (e: any) {
    error.value = e.message
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function handleDelete(docId: string) {
  try {
    await deleteDocument(docId)
    documents.value = documents.value.filter(d => d.doc_id !== docId)
  } catch (e: any) {
    error.value = e.message
  }
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  handleFiles(e.dataTransfer?.files ?? null)
}

const fileIcons: Record<string, string> = {
  pdf: '📄',
  txt: '📝',
  md: '📝',
  docx: '📃',
  doc: '📃',
}

function getIcon(filename: string) {
  const ext = filename.split('.').pop()?.toLowerCase() ?? ''
  return fileIcons[ext] ?? '📄'
}

onMounted(loadDocuments)
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="px-4 py-3 border-b border-slate-700/50">
      <h2 class="text-sm font-semibold text-slate-200 flex items-center gap-2">
        <span>📚</span> 知识库文档
        <span class="ml-auto text-xs text-slate-500">{{ documents.length }} 个文件</span>
      </h2>
    </div>

    <!-- 拖拽上传区 -->
    <div class="px-3 py-3">
      <div
        class="relative border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all duration-200"
        :class="[
          dragOver
            ? 'border-indigo-400 bg-indigo-900/20'
            : 'border-slate-600 hover:border-indigo-500/60 hover:bg-slate-800/50',
        ]"
        @dragover.prevent="dragOver = true"
        @dragleave="dragOver = false"
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <input
          ref="fileInput"
          type="file"
          class="hidden"
          accept=".pdf,.txt,.md,.docx,.doc"
          multiple
          @change="handleFiles(($event.target as HTMLInputElement).files)"
        />

        <div v-if="uploading" class="flex flex-col items-center gap-2 text-indigo-400">
          <svg class="animate-spin w-6 h-6" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span class="text-xs">正在处理文档...</span>
        </div>
        <div v-else class="flex flex-col items-center gap-1.5">
          <span class="text-2xl">☁️</span>
          <p class="text-xs text-slate-400">拖拽文件到此处，或<span class="text-indigo-400 font-medium">点击上传</span></p>
          <p class="text-xs text-slate-600">支持 PDF、TXT、MD、DOCX</p>
        </div>
      </div>

      <p v-if="error" class="mt-2 text-xs text-red-400 bg-red-900/20 border border-red-800/40 rounded-lg px-3 py-2">
        {{ error }}
      </p>
    </div>

    <!-- 文档列表 -->
    <div class="flex-1 overflow-y-auto scrollbar-thin px-3 pb-3">
      <div v-if="documents.length === 0" class="text-center py-8 text-slate-500 text-xs">
        暂无文档，上传文件开始构建知识库
      </div>

      <TransitionGroup name="doc-list" tag="div" class="space-y-2">
        <div
          v-for="doc in documents"
          :key="doc.doc_id"
          class="group flex items-center gap-2.5 bg-slate-800/60 border border-slate-700/40 rounded-lg px-3 py-2.5 hover:border-slate-600/60 transition-all"
        >
          <span class="text-base flex-shrink-0">{{ getIcon(doc.filename) }}</span>
          <span class="flex-1 text-xs text-slate-300 truncate" :title="doc.filename">{{ doc.filename }}</span>
          <button
            class="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-900/40 text-slate-500 hover:text-red-400"
            @click="handleDelete(doc.doc_id)"
            title="删除"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<style scoped>
.doc-list-enter-active,
.doc-list-leave-active {
  transition: all 0.2s ease;
}
.doc-list-enter-from {
  opacity: 0;
  transform: translateX(-8px);
}
.doc-list-leave-to {
  opacity: 0;
  transform: translateX(8px);
}
</style>
