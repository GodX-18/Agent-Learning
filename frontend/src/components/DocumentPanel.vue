<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchDocumentPreview, fetchDocuments, deleteDocument, getDocumentFileUrl, uploadDocument, type Document, type DocumentPreview } from '../api'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog'
import MessageResponse from './ai-elements/message/MessageResponse.vue'

const documents = ref<Document[]>([])
const uploading = ref(false)
const error = ref('')
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement>()
const previewOpen = ref(false)
const previewLoading = ref(false)
const previewError = ref('')
const previewDocument = ref<DocumentPreview | null>(null)

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
    if (previewDocument.value?.doc_id === docId) {
      previewOpen.value = false
      previewDocument.value = null
    }
  } catch (e: any) {
    error.value = e.message
  }
}

async function handlePreview(doc: Document) {
  previewOpen.value = true
  previewLoading.value = true
  previewError.value = ''
  previewDocument.value = null

  try {
    previewDocument.value = await fetchDocumentPreview(doc.doc_id)
  } catch (e: any) {
    previewError.value = e.message
  } finally {
    previewLoading.value = false
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

const previewContent = computed(() => {
  const content = previewDocument.value?.content?.trim()
  return content || '文档内容为空，暂时没有可展示的文本。'
})

const isPdfPreview = computed(() => previewDocument.value?.file_type === 'pdf')
const previewFileUrl = computed(() => {
  if (!previewDocument.value) return ''
  return getDocumentFileUrl(previewDocument.value.doc_id)
})

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
          class="group flex items-center gap-2.5 bg-slate-800/60 border border-slate-700/40 rounded-lg px-3 py-2.5 hover:border-indigo-500/40 hover:bg-slate-800 transition-all cursor-pointer"
          @click="handlePreview(doc)"
        >
          <span class="text-base flex-shrink-0">{{ getIcon(doc.filename) }}</span>
          <span class="flex-1 text-xs text-slate-300 truncate" :title="doc.filename">{{ doc.filename }}</span>
          <button
            class="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-900/40 text-slate-500 hover:text-red-400"
            @click.stop="handleDelete(doc.doc_id)"
            title="删除"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>

    <Dialog v-model:open="previewOpen">
      <DialogContent class="w-[min(92vw,1100px)] max-w-[1100px] border-slate-800 bg-slate-950 text-slate-100 p-6">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2 text-base">
            <span>{{ previewDocument ? getIcon(previewDocument.filename) : '📄' }}</span>
            <span class="truncate">{{ previewDocument?.filename || '文档预览' }}</span>
          </DialogTitle>
        </DialogHeader>

        <div class="mt-4 max-h-[75vh] overflow-y-auto rounded-2xl border border-slate-800 bg-slate-900/70">
          <div v-if="previewLoading" class="px-4 py-10 text-center text-sm text-slate-400">
            正在加载文档预览...
          </div>
          <div v-else-if="previewError" class="px-4 py-10 text-center text-sm text-red-400">
            {{ previewError }}
          </div>
          <div v-else-if="isPdfPreview" class="flex h-[75vh] flex-col overflow-hidden">
            <div class="flex items-center justify-between border-b border-slate-800 px-5 py-3 text-xs text-slate-400">
              <span>PDF 已切换为原文件预览，版式会比文本抽取更准确。</span>
              <a
                :href="previewFileUrl"
                target="_blank"
                rel="noreferrer"
                class="text-indigo-400 transition hover:text-indigo-300"
              >
                新窗口打开
              </a>
            </div>
            <iframe
              :src="previewFileUrl"
              class="h-full w-full bg-white"
              title="PDF 预览"
            />
          </div>
          <div v-else class="preview-markdown px-6 py-5">
            <MessageResponse :content="previewContent" class="text-slate-200" />
          </div>
        </div>
      </DialogContent>
    </Dialog>
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

:deep(.preview-markdown .prose) {
  max-width: none;
}

:deep(.preview-markdown h1),
:deep(.preview-markdown h2),
:deep(.preview-markdown h3),
:deep(.preview-markdown h4) {
  color: #f8fafc;
  font-weight: 700;
  line-height: 1.25;
  margin: 1.25rem 0 0.75rem;
}

:deep(.preview-markdown h1) {
  font-size: 1.75rem;
}

:deep(.preview-markdown h2) {
  font-size: 1.35rem;
}

:deep(.preview-markdown h3) {
  font-size: 1.1rem;
}

:deep(.preview-markdown p),
:deep(.preview-markdown li),
:deep(.preview-markdown blockquote) {
  color: #cbd5e1;
  line-height: 1.8;
}

:deep(.preview-markdown p),
:deep(.preview-markdown ul),
:deep(.preview-markdown ol),
:deep(.preview-markdown pre),
:deep(.preview-markdown table),
:deep(.preview-markdown blockquote) {
  margin: 0.9rem 0;
}

:deep(.preview-markdown ul),
:deep(.preview-markdown ol) {
  padding-left: 1.4rem;
}

:deep(.preview-markdown a) {
  color: #818cf8;
}

:deep(.preview-markdown strong) {
  color: #f8fafc;
}

:deep(.preview-markdown code) {
  color: #e2e8f0;
}

:deep(.preview-markdown pre) {
  overflow-x: auto;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 0.9rem;
  background: rgba(15, 23, 42, 0.92);
  padding: 1rem;
}

:deep(.preview-markdown pre code) {
  display: block;
  white-space: pre;
  font-size: 0.9rem;
  line-height: 1.7;
}

:deep(.preview-markdown blockquote) {
  border-left: 3px solid rgba(99, 102, 241, 0.65);
  padding-left: 1rem;
}

:deep(.preview-markdown table) {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
  border-radius: 0.8rem;
}

:deep(.preview-markdown th),
:deep(.preview-markdown td) {
  border: 1px solid rgba(148, 163, 184, 0.16);
  padding: 0.7rem 0.85rem;
  text-align: left;
}

:deep(.preview-markdown th) {
  background: rgba(30, 41, 59, 0.9);
  color: #f8fafc;
}
</style>
