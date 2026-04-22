<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import DocumentPanel from './components/DocumentPanel.vue'
import { streamChat, clearSession, healthCheck } from './api'
import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from '@/components/ai-elements/conversation'
import {
  Message,
  MessageContent,
  MessageResponse,
} from '@/components/ai-elements/message'
import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  PromptInputSubmit,
  PromptInputTextarea,
} from '@/components/ai-elements/prompt-input'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
}

const messages = ref<ChatMessage[]>([])
const isLoading = ref(false)
const sessionId = ref(uuidv4())
const sidebarOpen = ref(true)
const serverOnline = ref(true)
const notification = ref('')
const notifTimer = ref<ReturnType<typeof setTimeout>>()

const chatStatus = computed(() => isLoading.value ? 'streaming' : 'ready')

function showNotif(msg: string) {
  notification.value = msg
  clearTimeout(notifTimer.value)
  notifTimer.value = setTimeout(() => (notification.value = ''), 3000)
}

async function sendMessage(text: string) {
  const trimmed = text.trim()
  if (!trimmed || isLoading.value) return

  isLoading.value = true

  messages.value.push({
    id: uuidv4(),
    role: 'user',
    content: trimmed,
  })

  messages.value.push({
    id: uuidv4(),
    role: 'assistant',
    content: '',
    isStreaming: true,
  })

  try {
    for await (const event of streamChat(trimmed, sessionId.value)) {
      const last = messages.value[messages.value.length - 1]
      if (event.error) {
        last.content = `❌ 错误：${event.error}`
        break
      }
      if (event.chunk) {
        last.content += event.chunk
      }
      if (event.done) break
    }
  } catch (e: unknown) {
    const last = messages.value[messages.value.length - 1]
    last.content = `❌ 请求失败：${e instanceof Error ? e.message : String(e)}`
  } finally {
    const last = messages.value[messages.value.length - 1]
    if (last) last.isStreaming = false
    isLoading.value = false
  }
}

function handlePromptSubmit(payload: { text: string }) {
  sendMessage(payload.text)
}

async function newChat() {
  await clearSession(sessionId.value)
  sessionId.value = uuidv4()
  messages.value = []
  showNotif('已开始新对话')
}

function onDocumentUploaded(doc: { filename: string; chunks: number }) {
  showNotif(`✅ "${doc.filename}" 已上传（${doc.chunks} 个片段）`)
}

const quickPrompts = [
  '总结一下上传文档的主要内容',
  '文档中有哪些关键信息？',
  '现在是什么时间？',
  '帮我计算 1024 * 768',
]

onMounted(async () => {
  serverOnline.value = await healthCheck()
})
</script>

<template>
  <div class="flex h-screen overflow-hidden dark bg-background text-foreground">
    <!-- 侧边栏 -->
    <Transition name="sidebar">
      <aside
        v-show="sidebarOpen"
        class="w-72 flex-shrink-0 bg-card border-r border-border flex flex-col"
      >
        <!-- 侧边栏顶部 -->
        <div class="px-4 py-4 border-b border-border">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">
              L
            </div>
            <div>
              <h1 class="text-sm font-bold text-foreground">LangChain Agent</h1>
              <p class="text-xs text-muted-foreground">RAG 智能问答助手</p>
            </div>
          </div>

          <!-- 服务状态 -->
          <div class="mt-3 flex items-center gap-2 text-xs">
            <span
              class="w-2 h-2 rounded-full"
              :class="serverOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'"
            />
            <span :class="serverOnline ? 'text-emerald-400' : 'text-red-400'">
              {{ serverOnline ? '服务正常' : '服务离线' }}
            </span>
          </div>
        </div>

        <!-- 新对话按钮 -->
        <div class="px-3 py-3 border-b border-border">
          <button
            class="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors"
            @click="newChat"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            新建对话
          </button>
        </div>

        <!-- 文档管理面板 -->
        <div class="flex-1 overflow-hidden">
          <DocumentPanel @upload="onDocumentUploaded" />
        </div>

        <!-- 底部信息 -->
        <div class="px-4 py-3 border-t border-border text-xs text-muted-foreground">
          LangChain + ChromaDB + OpenAI
        </div>
      </aside>
    </Transition>

    <!-- 主内容区 -->
    <main class="flex-1 flex flex-col min-w-0 bg-background">
      <!-- 顶部工具栏 -->
      <header class="flex-shrink-0 flex items-center gap-3 px-4 py-3 border-b border-border bg-card/50 backdrop-blur-sm">
        <button
          class="p-1.5 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
          @click="sidebarOpen = !sidebarOpen"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h2 class="text-sm font-semibold text-foreground">智能对话</h2>
        <div class="ml-auto flex items-center gap-2">
          <span class="text-xs text-muted-foreground font-mono">{{ sessionId.slice(0, 8) }}...</span>
          <button
            class="p-1.5 rounded-lg hover:bg-accent text-muted-foreground hover:text-destructive transition-colors"
            title="清除对话"
            @click="newChat"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </header>

      <!-- 消息区域 + 输入框 -->
      <div class="flex-1 flex flex-col min-h-0">
        <!-- Conversation 组件自动处理滚动 -->
        <Conversation class="flex-1">
          <ConversationContent class="px-4 py-4">
            <!-- 欢迎界面 -->
            <div
              v-if="messages.length === 0"
              class="flex flex-col items-center justify-center min-h-full gap-6 py-16 px-8"
            >
              <div class="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center text-3xl shadow-xl">
                🤖
              </div>
              <div class="text-center">
                <h3 class="text-xl font-bold text-foreground mb-2">你好，我是 LangChain 智能助手</h3>
                <p class="text-sm text-muted-foreground max-w-md">
                  我可以帮你分析上传的文档，回答问题，以及执行各种任务。
                  先在左侧上传文档，或者直接开始提问！
                </p>
              </div>

              <!-- 快速提示 -->
              <div class="grid grid-cols-2 gap-2 w-full max-w-lg">
                <button
                  v-for="prompt in quickPrompts"
                  :key="prompt"
                  class="text-left px-4 py-3 rounded-xl border border-border hover:border-indigo-500/60 hover:bg-accent text-sm text-muted-foreground hover:text-foreground transition-all"
                  @click="sendMessage(prompt)"
                >
                  {{ prompt }}
                </button>
              </div>
            </div>

            <!-- 消息气泡列表 -->
            <template v-for="msg in messages" :key="msg.id">
              <Message :from="msg.role" class="msg-enter">
                <MessageContent>
                  <MessageResponse :content="msg.content" />
                </MessageContent>
              </Message>
            </template>
          </ConversationContent>
          <ConversationScrollButton />
        </Conversation>

        <!-- 输入区域 -->
        <div class="flex-shrink-0 border-t border-border bg-card/50 backdrop-blur-sm px-4 py-4">
          <div class="max-w-4xl mx-auto">
            <PromptInput @submit="handlePromptSubmit">
              <PromptInputBody>
                <PromptInputTextarea
                  placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
                  :disabled="isLoading"
                />
              </PromptInputBody>
              <PromptInputFooter>
                <p class="text-xs text-muted-foreground">
                  AI 可能产生错误信息，重要决策请自行核实
                </p>
                <PromptInputSubmit
                  :status="chatStatus"
                  :disabled="isLoading"
                />
              </PromptInputFooter>
            </PromptInput>
          </div>
        </div>
      </div>
    </main>

    <!-- 通知提示 -->
    <Transition name="notif">
      <div
        v-if="notification"
        class="fixed bottom-6 right-6 bg-card border border-border text-foreground text-sm px-4 py-3 rounded-xl shadow-xl z-50"
      >
        {{ notification }}
      </div>
    </Transition>
  </div>
</template>

<style>
.sidebar-enter-active,
.sidebar-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}
.sidebar-enter-from,
.sidebar-leave-to {
  width: 0 !important;
  opacity: 0;
}

.notif-enter-active,
.notif-leave-active {
  transition: all 0.3s ease;
}
.notif-enter-from,
.notif-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
