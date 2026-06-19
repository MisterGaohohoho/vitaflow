<script setup lang="ts">
import { computed } from "vue"
import { Check, Minus, Plus, X } from "lucide-vue-next"
import Button from "@/components/ui/button/Button.vue"
import type { DiffKind, SectionDiff } from "@/utils/aiDiff"

const props = defineProps<{
  open: boolean
  title: string
  subtitle?: string
  sections: SectionDiff[]
  suggestions?: string[]
  applyLabel?: string
  emptyText?: string
}>()

defineEmits<{ close: []; apply: [] }>()

const diffLabels: Record<DiffKind, string> = {
  added: "新增",
  modified: "修改",
  removed: "删除",
}

const diffClass: Record<DiffKind, string> = {
  added: "border-blue-200 bg-blue-50 text-blue-700",
  modified: "border-blue-200 bg-blue-50 text-blue-700",
  removed: "border-red-200 bg-red-50 text-red-700",
}

const diffIconClass: Record<DiffKind, string> = {
  added: "bg-blue-600 text-white",
  modified: "bg-blue-600 text-white",
  removed: "bg-red-600 text-white",
}

const totals = computed(() => {
  const result = { added: 0, modified: 0, removed: 0 }
  props.sections.forEach((section) => {
    section.changes.forEach((change) => {
      result[change.kind] += 1
    })
  })
  return result
})

const totalChanges = computed(() => totals.value.added + totals.value.modified + totals.value.removed)
const visibleSuggestions = computed(() => (props.suggestions || []).filter(Boolean))
</script>

<template>
  <Teleport to="body">
    <Transition name="review-modal">
      <div v-if="open" class="fixed inset-0 z-[90] flex items-center justify-center bg-zinc-950/45 p-4 backdrop-blur-sm">
        <div class="flex max-h-[calc(100dvh-32px)] w-full max-w-6xl flex-col overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-2xl">
          <header class="shrink-0 border-b border-zinc-100 bg-white px-4 py-3 sm:px-6 sm:py-5">
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-lg sm:text-xl font-semibold tracking-tight text-zinc-950">{{ title }}</h2>
                <p v-if="subtitle" class="mt-0.5 sm:mt-1 text-xs sm:text-sm leading-5 sm:leading-6 text-zinc-500">{{ subtitle }}</p>
              </div>
              <Button size="icon" variant="ghost" class="h-8 w-8 sm:h-9 sm:w-9 rounded-full text-zinc-400 hover:bg-zinc-100 hover:text-zinc-900" @click="$emit('close')">
                <X class="h-4 w-4" />
              </Button>
            </div>

            <div class="mt-3 flex gap-2 sm:mt-5 sm:grid sm:grid-cols-4 sm:gap-3">
              <div class="flex-1 rounded-lg border border-zinc-100 bg-zinc-50 px-2 py-1.5 sm:rounded-xl sm:px-4 sm:py-3">
                <div class="text-[10px] text-center sm:text-left sm:text-xs text-zinc-500">变更</div>
                <div class="mt-0.5 text-center sm:text-left text-base sm:mt-1 sm:text-2xl font-semibold text-zinc-950">{{ totalChanges }}</div>
              </div>
              <div class="flex-1 rounded-lg border border-blue-100 bg-blue-50 px-2 py-1.5 sm:rounded-xl sm:px-4 sm:py-3">
                <div class="text-[10px] text-center sm:text-left sm:text-xs text-blue-600">新增</div>
                <div class="mt-0.5 text-center sm:text-left text-base sm:mt-1 sm:text-2xl font-semibold text-blue-700">{{ totals.added }}</div>
              </div>
              <div class="flex-1 rounded-lg border border-blue-100 bg-blue-50 px-2 py-1.5 sm:rounded-xl sm:px-4 sm:py-3">
                <div class="text-[10px] text-center sm:text-left sm:text-xs text-blue-600">修改</div>
                <div class="mt-0.5 text-center sm:text-left text-base sm:mt-1 sm:text-2xl font-semibold text-blue-700">{{ totals.modified }}</div>
              </div>
              <div class="flex-1 rounded-lg border border-red-100 bg-red-50 px-2 py-1.5 sm:rounded-xl sm:px-4 sm:py-3">
                <div class="text-[10px] text-center sm:text-left sm:text-xs text-red-600">删除</div>
                <div class="mt-0.5 text-center sm:text-left text-base sm:mt-1 sm:text-2xl font-semibold text-red-700">{{ totals.removed }}</div>
              </div>
            </div>
          </header>

          <main class="min-h-0 flex-1 overflow-y-auto bg-zinc-50/70 px-4 py-4 sm:px-6 sm:py-5 thin-scrollbar">
            <section v-if="visibleSuggestions.length" class="mb-4 sm:mb-5 rounded-xl sm:rounded-2xl border border-zinc-200 bg-white p-4 sm:p-5">
              <h3 class="text-sm font-semibold text-zinc-950">优化说明</h3>
              <ul class="mt-2 sm:mt-3 list-disc space-y-1.5 sm:space-y-2 pl-5 text-sm leading-6 text-zinc-600">
                <li v-for="item in visibleSuggestions" :key="item">{{ item }}</li>
              </ul>
            </section>

            <div v-if="sections.length" class="space-y-4 sm:space-y-5">
              <section v-for="section in sections" :key="section.key" class="rounded-xl sm:rounded-2xl border border-zinc-200 bg-white p-3 sm:p-5">
                <div class="flex items-center justify-between gap-3 border-b border-zinc-100 pb-3 sm:pb-4">
                  <h3 class="text-sm sm:text-base font-semibold text-zinc-950">{{ section.title }}</h3>
                  <span class="rounded-full bg-zinc-100 px-2 py-0.5 sm:px-2.5 sm:py-1 text-[10px] sm:text-xs font-medium text-zinc-500">{{ section.changes.length }} 项变化</span>
                </div>

                <div class="mt-3 sm:mt-4 space-y-5 sm:space-y-4">
                  <article v-for="(change, index) in section.changes" :key="`${change.kind}-${change.title}-${index}`" class="sm:rounded-xl sm:border border-zinc-100 sm:bg-zinc-50/70 sm:p-4">
                    <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
                      <span class="inline-flex h-6 w-6 items-center justify-center rounded-full" :class="diffIconClass[change.kind]">
                        <Plus v-if="change.kind === 'added'" class="h-3.5 w-3.5" />
                        <Minus v-else-if="change.kind === 'removed'" class="h-3.5 w-3.5" />
                        <Check v-else class="h-3.5 w-3.5" />
                      </span>
                      <span class="rounded-full border px-2 py-0.5 text-xs font-medium" :class="diffClass[change.kind]">{{ diffLabels[change.kind] }}</span>
                      <h4 class="text-sm font-semibold text-zinc-950">{{ change.title }}</h4>
                    </div>

                    <div v-if="change.kind === 'modified'" class="mt-3 sm:mt-4 grid gap-2 sm:gap-4 lg:grid-cols-2 min-w-0">
                      <div class="min-w-0 rounded-md sm:rounded-lg border border-red-100 bg-white p-2.5 sm:p-4">
                        <div class="mb-1.5 sm:mb-2 text-[10px] sm:text-xs font-semibold text-red-600">原内容</div>
                        <p class="whitespace-pre-wrap break-all sm:break-words text-[13px] sm:text-sm leading-6 sm:leading-7 text-zinc-600">{{ change.before }}</p>
                      </div>
                      <div class="min-w-0 rounded-md sm:rounded-lg border border-blue-100 bg-white p-2.5 sm:p-4">
                        <div class="mb-1.5 sm:mb-2 text-[10px] sm:text-xs font-semibold text-blue-600">优化后</div>
                        <p class="whitespace-pre-wrap break-all sm:break-words text-[13px] sm:text-sm leading-6 sm:leading-7 text-zinc-800">{{ change.after }}</p>
                      </div>
                    </div>

                    <div v-else class="min-w-0 mt-3 sm:mt-4 rounded-md sm:rounded-lg border border-zinc-100 bg-white p-2.5 sm:p-4">
                      <p class="whitespace-pre-wrap break-all sm:break-words text-[13px] sm:text-sm leading-6 sm:leading-7 text-zinc-700">{{ change.after || change.before }}</p>
                    </div>
                  </article>
                </div>
              </section>
            </div>

            <div v-else class="rounded-2xl border border-dashed border-zinc-200 bg-white p-8 text-center text-sm text-zinc-500">
              {{ emptyText || "没有检测到可对比的内容变化。" }}
            </div>
          </main>

          <footer class="flex shrink-0 items-center justify-end gap-3 border-t border-zinc-100 bg-white px-6 py-4">
            <Button variant="outline" @click="$emit('close')">返回检查</Button>
            <Button :disabled="!totalChanges" @click="$emit('apply')">{{ applyLabel || "采纳优化结果" }}</Button>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.review-modal-enter-active,
.review-modal-leave-active {
  transition: opacity 0.2s ease;
}
.review-modal-enter-active > div,
.review-modal-leave-active > div {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.review-modal-enter-from,
.review-modal-leave-to {
  opacity: 0;
}
.review-modal-enter-from > div,
.review-modal-leave-to > div {
  opacity: 0;
  transform: translateY(10px) scale(0.98);
}
</style>
