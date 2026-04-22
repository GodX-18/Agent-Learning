<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'

const props = defineProps<{
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
  timestamp?: number
}>()

// ── Marked 配置 ────────────────────────────────────────────────────────────
marked.setOptions({ breaks: true, gfm: true })
const renderer = new marked.Renderer()
renderer.code = ({ text, lang }) => {
  const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext'
  const highlighted = hljs.highlight(text, { language }).value
  return `<pre><code class="hljs language-${language}">${highlighted}</code></pre>`
}
marked.use({ renderer })

// ── 打字机状态 ─────────────────────────────────────────────────────────────
// 当前打字机展示的字符串（从 '' 追赶到 props.content）
const typedText = ref('')
// 是否已切换为 Markdown 渲染
const markdownReady = ref(false)

let rafId: number | null = null
const SPEED = 8 // 每帧追加字符数

function scheduleRaf() {
  if (rafId !== null) return
  rafId = requestAnimationFrame(function advance() {
    const target = props.content
    if (typedText.value.length < target.length) {
      typedText.value = target.slice(0, typedText.value.length + SPEED)
      rafId = requestAnimationFrame(advance)
    } else {
      typedText.value = target
      rafId = null
    }
  })
}

function cancelRaf() {
  if (rafId !== null) {
    cancelAnimationFrame(rafId)
    rafId = null
  }
}

function snapToMarkdown() {
  cancelRaf()
  typedText.value = props.content
  // 短暂延迟让 DOM 更新后再切渲染模式，避免闪烁
  setTimeout(() => {
    markdownReady.value = true
  }, 60)
}

// 内容变化时：流式则启动打字机，非流式则直接展示
watch(
  () => props.content,
  () => {
    if (props.isStreaming) {
      scheduleRaf()
    } else {
      snapToMarkdown()
    }
  },
)

// 流式状态变化：结束时切 Markdown
watch(
  () => props.isStreaming,
  (streaming) => {
    if (!streaming) snapToMarkdown()
  },
)

// 挂载时处理已有内容（历史消息 / 非流式场景）
onMounted(() => {
  if (!props.isStreaming && props.content) {
    typedText.value = props.content
    markdownReady.value = true
  }
})

// 光标闪烁：正在流式 OR 打字机还没追上
const showCursor = computed(
  () => props.isStreaming === true || typedText.value.length < props.content.length,
)

// 展示模式：markdownReady 且光标已消失 → Markdown；否则纯文本
const showMarkdown = computed(() => markdownReady.value && !showCursor.value)

const renderedMarkdown = computed(() => marked.parse(props.content) as string)

const timeStr = computed(() => {
  if (!props.timestamp) return ''
  return new Date(props.timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
})
</script>

<template>
  <div
    class="msg-enter flex gap-3 px-4 py-3"
    :class="role === 'user' ? 'flex-row-reverse' : 'flex-row'"
  >
    <!-- 头像 -->
    <div class="flex-shrink-0">
      <div
        v-if="role === 'assistant'"
        class="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600
               flex items-center justify-center text-white text-sm font-bold shadow-lg"
      >
        AI
      </div>
      <div
        v-else
        class="w-8 h-8 rounded-full bg-gradient-to-br from-slate-500 to-slate-600
               flex items-center justify-center text-white text-sm font-bold"
      >
        U
      </div>
    </div>

    <!-- 消息气泡 -->
    <div
      class="flex flex-col gap-1 max-w-[80%]"
      :class="role === 'user' ? 'items-end' : 'items-start'"
    >
      <div
        class="rounded-2xl px-4 py-3 shadow-sm"
        :class="[
          role === 'user'
            ? 'bg-indigo-600 text-white rounded-tr-sm'
            : 'bg-slate-800 border border-slate-700/50 rounded-tl-sm',
        ]"
      >
        <!-- 用户消息 -->
        <p v-if="role === 'user'" class="text-sm leading-relaxed whitespace-pre-wrap">
          {{ content }}
        </p>

        <!-- AI 消息 -->
        <div v-else class="relative min-w-[1.5rem] min-h-[1.5rem]">

          <!-- ① 打字机阶段：纯文本 + 光标 -->
          <div v-show="!showMarkdown">
            <!-- 空内容时：只显示闪烁光标（等待响应） -->
            <span
              v-if="!typedText"
              class="inline-block w-2 h-[1.1em] bg-indigo-400 rounded-sm cursor-blink align-middle"
            />
            <!-- 有内容：打字机文本 -->
            <p v-else class="text-sm leading-relaxed whitespace-pre-wrap text-slate-200 typewriter-text">
              {{ typedText }}<span
                v-if="showCursor"
                class="typewriter-cursor"
              />
            </p>
          </div>

          <!-- ② Markdown 阶段：流式结束后淡入 -->
          <Transition name="md-fade" appear>
            <div
              v-if="showMarkdown"
              class="prose-custom"
              v-html="renderedMarkdown"
            />
          </Transition>

        </div>
      </div>

      <span v-if="timeStr" class="text-xs text-slate-500 px-1">{{ timeStr }}</span>
    </div>
  </div>
</template>

<style scoped>
/* 打字机光标 */
.typewriter-cursor {
  display: inline-block;
  width: 2px;
  height: 1.1em;
  background: #818cf8;
  border-radius: 1px;
  margin-left: 1px;
  vertical-align: middle;
  animation: blink 0.7s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0; }
}

/* 每个新字符滑入 */
.typewriter-text {
  overflow-wrap: break-word;
}

/* Markdown 淡入 */
.md-fade-enter-active {
  transition: opacity 0.25s ease;
}
.md-fade-enter-from {
  opacity: 0;
}
</style>
