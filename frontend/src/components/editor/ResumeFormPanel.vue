<script setup lang="ts">
import { PanelLeftClose, Sparkles } from "lucide-vue-next"
import Button from "@/components/ui/button/Button.vue"
import Input from "@/components/ui/input/Input.vue"
import BasicInfoForm from "./BasicInfoForm.vue"
import SectionListForm from "./SectionListForm.vue"
import SummaryForm from "./SummaryForm.vue"
import CustomSectionForm from "./CustomSectionForm.vue"
import StyleConfigPanel from "./StyleConfigPanel.vue"
import SectionOptimizeInline from "./SectionOptimizeInline.vue"
import type { ResumeData, TemplateConfig } from "@/types/resume"

const props = defineProps<{
  data: ResumeData
  config: TemplateConfig
  current: string
  showStyle: boolean
  optimizeResult?: any
  optimizePreview?: any
  optimizeLoading?: boolean
  optimizeError?: string
  optimizeStreamText?: string
  isWide?: boolean
}>()
const emit = defineEmits<{ change: []; optimize: []; applyOptimize: []; clearOptimize: [] }>()
function customSection() {
  return props.data.custom_sections.find((item) => item.id === props.current)
}

function currentSectionValue() {
  if ((props.data as any)[props.current] !== undefined) return (props.data as any)[props.current]
  return customSection()
}
</script>

<template>
  <section class="h-full shrink-0 flex flex-col border-r border-zinc-200/60 bg-white/95 backdrop-blur-sm shadow-[10px_0_15px_-3px_rgba(0,0,0,0.02)]">
    <!-- Sticky Header -->
    <div class="hidden md:flex items-center justify-between border-b border-zinc-100/80 bg-white/80 px-5 py-4 shrink-0 z-10 backdrop-blur-md">
      <div class="flex-1 min-w-0 mr-4">
        <div class="inline-grid items-center max-w-full -ml-2">
          <span class="col-start-1 row-start-1 invisible whitespace-pre pl-2 pr-3 py-1 border border-transparent text-[16px] sm:text-[18px] font-semibold tracking-tight overflow-hidden">{{ data.layout.section_titles[current] || current }}</span>
          <input 
            :value="data.layout.section_titles[current] || current"
            @input="data.layout.section_titles[current] = ($event.target as HTMLInputElement).value; $emit('change')"
            size="1"
            class="col-start-1 row-start-1 w-full min-w-0 border border-transparent bg-transparent px-2 py-1 text-[16px] sm:text-[18px] font-semibold tracking-tight text-zinc-900 shadow-none hover:border-zinc-200 hover:bg-zinc-50 focus:border-emerald-500 focus:bg-white focus:ring-1 focus:ring-emerald-500 transition-all outline-none rounded-md truncate"
          />
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button v-if="current !== 'basics'" size="sm" variant="outline" class="h-8 border-zinc-200 bg-white text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 shadow-sm transition-all" :disabled="optimizeLoading" @click="$emit('optimize')">
          <Sparkles class="h-3.5 w-3.5 mr-1.5 text-zinc-500" /> AI 润色
        </Button>
      </div>
    </div>
    
    <!-- Scrollable Content -->
    <div class="flex-1 overflow-y-auto p-3 md:p-5 pb-20 md:pb-5 thin-scrollbar">
      <SectionOptimizeInline
        v-if="current !== 'basics' && (optimizeLoading || optimizeError || optimizeResult)"
        :section-key="current"
        :section-title="data.layout.section_titles[current] || current"
        :current-value="currentSectionValue()"
        :result="optimizeResult"
        :preview="optimizePreview"
        :loading="optimizeLoading"
        :error="optimizeError"
        :stream-text="optimizeStreamText"
        @apply="$emit('applyOptimize')"
        @retry="$emit('optimize')"
        @clear="$emit('clearOptimize')"
      />
      <StyleConfigPanel v-if="showStyle" :config="config" class="mb-4" @change="$emit('change')" />
      <BasicInfoForm v-if="current === 'basics'" :basics="data.basics" @change="$emit('change')" />
      <SummaryForm v-else-if="current === 'summary'" :summary="data.summary" @change="$emit('change')" />
      <SectionListForm v-else-if="['education','skills','work','projects','awards'].includes(current)" :section-key="current" :items="(data as any)[current]" :is-wide="isWide" @change="$emit('change')" />
      <CustomSectionForm v-else-if="customSection()" :section="customSection()" @change="$emit('change')" />
    </div>
  </section>
</template>
