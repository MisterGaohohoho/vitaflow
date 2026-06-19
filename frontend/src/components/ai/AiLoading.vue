<script setup lang="ts">
import { computed } from "vue"
import { Sparkles, CheckCircle2, Bot, Target, ScanLine } from "lucide-vue-next"

const props = defineProps<{ title?: string; description?: string; streamText?: string }>()

type Stage = {
  label: string
  patterns: string[]
}

const stageCatalog: Record<string, Stage[]> = {
  generate: [
    { label: "解析岗位与个人信息", patterns: ["target_position", "personal_info", "目标岗位"] },
    { label: "整理基本信息", patterns: ["basics", "field_config", "name", "phone", "email"] },
    { label: "撰写个人简介", patterns: ["summary", "个人简介", "content"] },
    { label: "梳理教育与技能", patterns: ["education", "skills", "keywords", "教育", "技能"] },
    { label: "生成经历与项目亮点", patterns: ["work", "projects", "highlights", "项目", "经历"] },
    { label: "检查结构并准备创建", patterns: ["layout", "section_order", "template_config", "explanation"] },
  ],
  score: [
    { label: "读取简历内容", patterns: ["resume_data", "basics", "summary"] },
    { label: "评估核心维度", patterns: ["details", "dimension", "score", "岗位匹配"] },
    { label: "整理优势与不足", patterns: ["strengths", "weaknesses", "missing_keywords"] },
    { label: "生成可执行建议", patterns: ["suggestions", "comment", "summary"] },
  ],
  jd: [
    { label: "解析岗位描述", patterns: ["job_description", "job_keywords", "岗位"] },
    { label: "比对简历匹配度", patterns: ["match_analysis", "score", "缺口", "匹配"] },
    { label: "重写相关模块", patterns: ["optimized_resume_data", "summary", "skills", "projects", "work"] },
    { label: "整理采纳建议", patterns: ["suggestions", "changes", "score"] },
  ],
  section: [
    { label: "读取当前模块", patterns: ["section_type", "section_title", "section_content"] },
    { label: "保留原有条目", patterns: ["id", "optimized_section"] },
    { label: "润色表达与关键词", patterns: ["keywords", "highlights", "description", "content"] },
    { label: "整理可写入内容", patterns: ["changes", "suggestions", "optimized_section"] },
  ],
}

const mode = computed<string>(() => {
  const title = props.title || ""
  if (title.includes("生成简历")) return "generate"
  if (title.includes("评分")) return "score"
  if (title.includes("JD")) return "jd"
  if (title.includes("润色")) return "section"
  if (title.includes("打磨")) return "chat"
  return "generate"
})

const stages = computed(() => stageCatalog[mode.value] || stageCatalog.generate)

const activeIndex = computed(() => {
  const text = props.streamText || ""
  if (!text) return 0
  let index = 0
  stages.value.forEach((stage, stageIndex) => {
    if (stage.patterns.some((pattern) => text.includes(pattern))) index = Math.max(index, stageIndex)
  })
  return index
})

const progress = computed(() => {
  if (!props.streamText) return 12
  return Math.min(96, Math.max(18, Math.round(((activeIndex.value + 1) / stages.value.length) * 100)))
})

const currentActivity = computed(() => {
  const current = stages.value[activeIndex.value]?.label || "处理内容"
  return `正在${current.replace(/^正在/, "")}...`
})

const IconComponent = computed(() => {
  if (mode.value === 'jd') return Target
  if (mode.value === 'score') return ScanLine
  if (mode.value === 'chat') return Bot
  return Sparkles
})
</script>

<template>
  <div class="diagnosis-loading flex flex-col justify-center py-4 w-full">
    <div class="relative w-full mx-auto">
      <div class="relative z-10 flex flex-col">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <span class="flex h-12 w-12 items-center justify-center rounded-[16px] bg-white text-zinc-700 shadow-[0_8px_24px_rgba(0,0,0,0.06)] ring-1 ring-zinc-200/60" style="view-transition-name: ai-hero-icon;">
              <component :is="IconComponent" class="h-6 w-6" stroke-width="1.5" />
            </span>
            <div>
              <div class="text-[11px] font-semibold uppercase tracking-[0.24em] text-blue-600/80">AI AGENT</div>
              <h3 class="mt-1 text-[18px] sm:text-[20px] font-semibold tracking-tight text-zinc-900">{{ title || "正在处理" }}</h3>
            </div>
          </div>
          <div class="flex h-12 w-12 items-center justify-center rounded-full bg-zinc-50 border border-zinc-100 shadow-sm text-sm font-semibold text-zinc-700 shrink-0">
            {{ progress }}%
          </div>
        </div>

        <p v-if="description" class="mt-4 text-[14px] leading-relaxed text-zinc-500">{{ description }}</p>

        <div class="mt-6 flex-1 space-y-3">
          <div v-for="(item, index) in stages" :key="item.label" class="analysis-step flex items-center gap-4 rounded-[16px] px-4 py-3.5 transition-colors duration-500" :class="index <= activeIndex ? 'bg-zinc-50 ring-1 ring-zinc-100 shadow-sm' : 'bg-transparent'">
            <span class="flex h-7 w-7 items-center justify-center rounded-full text-[11px] font-semibold transition-all duration-500 shrink-0" :class="index < activeIndex ? 'bg-blue-500 text-white shadow-md shadow-blue-500/20' : index === activeIndex ? 'bg-zinc-900 text-white shadow-md shadow-zinc-900/20' : 'bg-white text-zinc-400 ring-1 ring-zinc-200'">
              <CheckCircle2 v-if="index < activeIndex" class="h-4 w-4" />
              <span v-else>{{ index + 1 }}</span>
            </span>
            <span class="text-[14px] sm:text-[15px] font-medium transition-colors duration-500" :class="index <= activeIndex ? 'text-zinc-900' : 'text-zinc-400'">{{ item.label }}</span>
            <span v-if="index === activeIndex" class="ml-auto flex gap-1.5 shrink-0">
              <i v-for="dot in 3" :key="dot" class="h-1.5 w-1.5 rounded-full bg-zinc-900 animate-pulse" :style="{ animationDelay: `${dot * 150}ms` }"></i>
            </span>
            <span v-else-if="index < activeIndex" class="ml-auto text-blue-500 shrink-0">
              <CheckCircle2 class="h-5 w-5" />
            </span>
          </div>
        </div>
        
        <div class="mt-8 h-1.5 w-full overflow-hidden rounded-full bg-zinc-200/50">
          <div class="h-full rounded-full bg-blue-500 transition-all duration-700 ease-out" :style="{ width: `${progress}%` }"></div>
        </div>
      </div>
    </div>
  </div>
</template>
