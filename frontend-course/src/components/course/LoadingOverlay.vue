<script setup lang="ts">
defineProps<{
  visible: boolean
  title?: string
  description?: string
  canCancel?: boolean
}>()

const emit = defineEmits<{
  cancel: []
}>()
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="visible"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 px-4 backdrop-blur-sm"
      >
        <div class="w-full max-w-sm rounded-2xl border border-indigo-100/60 bg-white p-6 shadow-2xl">
          <div class="mb-5 flex items-center gap-3">
            <div class="dot-flashing" />
            <p class="m-0 text-sm font-semibold text-foreground">{{ title || "任务执行中" }}</p>
          </div>
          <p class="m-0 text-xs leading-5 text-muted-foreground">
            {{ description || "正在处理请求，请保持页面打开。" }}
          </p>
          <button v-if="canCancel" class="btn-secondary mt-5 w-full" @click="emit('cancel')">关闭提示</button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
