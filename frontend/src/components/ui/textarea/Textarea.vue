<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from "vue"

const props = defineProps<{ modelValue?: string; placeholder?: string; rows?: number }>()
const emit = defineEmits<{ "update:modelValue": [value: string] }>()

const textareaRef = ref<HTMLTextAreaElement | null>(null)

function adjustHeight() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

watch(() => props.modelValue, () => {
  nextTick(adjustHeight)
})

onMounted(() => {
  nextTick(adjustHeight)
})

function onInput(event: Event) {
  adjustHeight()
  emit('update:modelValue', (event.target as HTMLTextAreaElement).value)
}
</script>
<template>
  <textarea ref="textareaRef" :rows="rows || 5" :value="modelValue" :placeholder="placeholder" class="w-full resize-none rounded-md border border-zinc-200 bg-white px-3 py-2 text-[14px] leading-relaxed text-zinc-800 outline-none transition-all placeholder:text-zinc-400 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 shadow-sm" style="overflow: hidden;" @input="onInput" />
</template>
