<script setup lang="ts">
import { computed, ref, watch } from "vue"
import { CheckCircle2, RefreshCw, ScanLine, Sparkles, LoaderCircle } from "lucide-vue-next"

const props = defineProps<{ score: any; loading?: boolean; error?: string; streamText?: string; isWide?: boolean }>()
defineEmits<{ refresh: [] }>()

const stages = [
  { label: "读取简历结构", patterns: ["resume_data", "basics", "summary"] },
  { label: "评估内容表达", patterns: ["details", "dimension", "score", "岗位匹配"] },
  { label: "核对岗位竞争力", patterns: ["strengths", "weaknesses", "missing_keywords"] },
  { label: "整理改进建议", patterns: ["suggestions", "comment", "summary"] },
]

const activeIndex = computed(() => {
  const text = props.streamText || ""
  if (!text) return 0
  let index = 0
  stages.forEach((stage, stageIndex) => {
    if (stage.patterns.some((pattern) => text.includes(pattern))) index = Math.max(index, stageIndex)
  })
  return index
})

const progress = computed(() => {
  if (!props.streamText) return 15
  return Math.min(96, Math.max(20, Math.round(((activeIndex.value + 1) / stages.length) * 100)))
})

const fieldLabels: Record<string, string> = {
  basics: "基本信息",
  highest_degree: "最高学历",
  location: "所在城市",
  status: "当前状态",
  expected_salary: "期望薪资",
  phone: "电话",
  email: "邮箱",
  github: "代码仓库",
  website: "个人网站",
  education: "教育经历",
  skills: "专业技能",
  work: "实习/工作经历",
  projects: "项目经历",
  awards: "荣誉奖项",
}

function localText(value: any) {
  let result = String(value ?? "")
  Object.entries(fieldLabels)
    .sort((a, b) => b[0].length - a[0].length)
    .forEach(([key, label]) => {
      result = result.replace(new RegExp(`(?<![A-Za-z0-9_])${key}(?![A-Za-z0-9_])`, "g"), label)
    })
  return result
}

const scorePercent = computed(() => Math.max(0, Math.min(100, Number(props.score?.score || 0))))
const ringStyle = computed(() => ({ background: `conic-gradient(#3b82f6 ${scorePercent.value * 3.6}deg, #f4f4f5 0deg)` }))
const suggestions = computed(() => (props.score?.suggestions || []).filter(Boolean))

function detailPercent(item: any) {
  const max = Number(item?.max_score || 100)
  return Math.max(0, Math.min(100, Math.round((Number(item?.score || 0) / max) * 100)))
}

function staggerDelay(index: string | number, step = 65, base = 0) {
  return `${base + Number(index) * step}ms`
}
</script>

<template>
  <div class="h-full min-h-0 overflow-y-auto thin-scrollbar relative px-6 py-6">
    <div class="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full bg-blue-500/10 blur-[80px]"></div>
    <div v-if="loading" class="diagnosis-loading flex flex-col min-h-full justify-center">
      <div class="relative w-full max-w-md mx-auto">
        <div class="relative z-10 flex flex-col">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <span class="flex h-12 w-12 shrink-0 items-center justify-center rounded-[16px] bg-white text-zinc-700 shadow-[0_8px_24px_rgba(0,0,0,0.06)] ring-1 ring-zinc-200/60" style="view-transition-name: ai-hero-icon;">
                <ScanLine class="h-6 w-6" stroke-width="1.5" />
              </span>
              <div>
                <div class="text-[11px] font-semibold uppercase tracking-[0.24em] text-blue-600/80">Resume Analysis</div>
                <h3 class="mt-1 text-[20px] font-semibold tracking-tight text-zinc-900">正在进行 简历诊断</h3>
              </div>
            </div>
            <div class="flex h-12 w-12 items-center justify-center rounded-full bg-zinc-50 border border-zinc-100 shadow-sm text-sm font-semibold text-zinc-700">
              {{ progress }}%
            </div>
          </div>

          <div class="mt-10 flex-1 space-y-3.5">
            <div v-for="(item, index) in stages" :key="item.label" class="analysis-step flex items-center gap-4 rounded-[20px] px-5 py-4 transition-colors duration-500" :class="index <= activeIndex ? 'bg-zinc-50 ring-1 ring-zinc-100 shadow-sm' : 'bg-transparent'">
              <span class="flex h-7 w-7 items-center justify-center rounded-full text-[11px] font-semibold transition-all duration-500" :class="index < activeIndex ? 'bg-blue-500 text-white shadow-md shadow-blue-500/20' : index === activeIndex ? 'bg-zinc-900 text-white shadow-md shadow-zinc-900/20' : 'bg-white text-zinc-400 ring-1 ring-zinc-200'">
                <CheckCircle2 v-if="index < activeIndex" class="h-4 w-4" />
                <span v-else>{{ index + 1 }}</span>
              </span>
              <span class="text-[15px] font-medium transition-colors duration-500" :class="index <= activeIndex ? 'text-zinc-900' : 'text-zinc-400'">{{ item.label }}</span>
              <span v-if="index === activeIndex" class="ml-auto flex gap-1.5">
                <i v-for="dot in 3" :key="dot" class="analysis-dot h-1.5 w-1.5 rounded-full bg-zinc-900" :style="{ animationDelay: `${dot * 150}ms` }"></i>
              </span>
              <span v-else-if="index < activeIndex" class="ml-auto text-blue-500">
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

    <div v-else-if="error" class="flex min-h-full items-center justify-center p-4 md:p-8 text-center">
      <div>
        <div class="text-[15px] font-medium text-red-800">诊断未能完成</div>
        <p class="mt-3 text-[14px] text-red-600/80">{{ error }}</p>
        <button class="mt-6 rounded-full bg-red-100 px-6 py-2.5 text-[14px] font-medium text-red-700 transition active:scale-95 hover:bg-red-200" @click="$emit('refresh')">重新诊断</button>
      </div>
    </div>

    <div v-else-if="score" class="flex min-h-full gap-5" :class="isWide ? 'flex-row items-start' : 'flex-col'">
      <!-- Apple style Light Mode Widget for Score -->
      <aside class="score-hero relative overflow-hidden rounded-[28px] bg-white p-7 shadow-[0_8px_30px_rgb(0,0,0,0.04)] ring-1 ring-zinc-200/50 md:p-8 shrink-0 transition-all duration-300" :class="isWide ? 'w-1/3 sticky top-0' : 'w-full'">
        <div class="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-blue-500/5 blur-[80px]"></div>
        <div class="relative z-10 flex items-center justify-between">
          <span class="text-[11px] font-semibold uppercase tracking-[0.24em] text-blue-600/80">Resume Health</span>
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-[14px] bg-white text-zinc-700 shadow-[0_4px_12px_rgba(0,0,0,0.04)] ring-1 ring-zinc-200/60" style="view-transition-name: ai-hero-icon;">
            <ScanLine class="h-5 w-5" stroke-width="1.5" />
          </div>
        </div>
        <div class="relative z-10 mx-auto mt-10 flex h-[220px] w-[220px] items-center justify-center rounded-full p-[12px]" :style="ringStyle">
          <div class="flex h-full w-full flex-col items-center justify-center rounded-full bg-white shadow-[0_4px_20px_rgba(0,0,0,0.06)] ring-1 ring-zinc-100">
            <div class="score-number text-[72px] font-semibold tracking-[-0.04em] leading-none text-zinc-900">{{ score.score }}</div>
            <div class="mt-2 rounded-full bg-zinc-100 px-4 py-1.5 text-[13px] font-medium tracking-wide text-zinc-600">{{ score.level }}</div>
          </div>
        </div>
        <p class="relative z-10 mt-8 text-[15px] leading-relaxed text-zinc-500 text-center">{{ localText(score.summary) }}</p>
        <button class="relative z-10 mt-8 flex w-full items-center justify-center gap-2.5 rounded-full bg-zinc-900 px-5 py-3.5 text-[15px] font-medium text-white transition-all active:scale-[0.98] hover:bg-zinc-800 shadow-sm" @click="$emit('refresh')">
          <RefreshCw class="h-4 w-4" stroke-width="2" />重新扫描
        </button>
      </aside>

      <section class="min-w-0 space-y-5 transition-all duration-300" :class="isWide ? 'w-2/3 flex-1' : 'w-full'">
        <div class="grid gap-4 sm:grid-cols-2">
          <!-- Glassmorphism refined cards -->
          <article v-for="(item, index) in score.details" :key="item.dimension" class="diagnosis-card rounded-[24px] bg-white p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] ring-1 ring-zinc-200/50 transition-all hover:shadow-[0_8px_40px_rgb(0,0,0,0.08)] hover:-translate-y-0.5" :style="{ animationDelay: staggerDelay(index) }">
            <div class="flex items-center justify-between gap-3">
              <h3 class="text-[16px] font-semibold tracking-tight text-zinc-900">{{ item.dimension }}</h3>
              <span class="text-[15px] font-semibold tabular-nums text-blue-600">{{ item.score }}<span class="text-zinc-300">/</span><span class="text-zinc-400">{{ item.max_score }}</span></span>
            </div>
            <div class="mt-4 h-1.5 overflow-hidden rounded-full bg-zinc-100">
              <div class="dimension-progress h-full rounded-full bg-gradient-to-r from-blue-400 to-teal-500" :style="{ width: `${detailPercent(item)}%`, animationDelay: staggerDelay(index, 65, 160) }"></div>
            </div>
            <p class="mt-4 text-[13px] leading-relaxed text-zinc-500">{{ localText(item.comment) }}</p>
          </article>
        </div>

        <div v-if="suggestions.length" class="rounded-[24px] bg-white p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] ring-1 ring-zinc-200/50 md:p-8">
          <div class="flex items-center gap-3">
            <span class="flex h-10 w-10 items-center justify-center rounded-[14px] bg-blue-50 text-blue-600 ring-1 ring-blue-100/50">
              <Sparkles class="h-5 w-5" stroke-width="1.5" />
            </span>
            <div>
              <h3 class="text-[17px] font-semibold tracking-tight text-zinc-900">优先改进建议</h3>
              <p class="mt-1 text-[13px] text-zinc-400">按照对竞争力的影响程度排序</p>
            </div>
          </div>
          <div class="mt-6 grid gap-3 sm:grid-cols-2">
            <div v-for="(item, index) in suggestions" :key="item" class="suggestion-row flex gap-3.5 rounded-[20px] bg-zinc-50 p-4 transition-colors hover:bg-zinc-100/80" :style="{ animationDelay: staggerDelay(index, 55, 220) }">
              <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white text-[12px] font-semibold text-blue-600 shadow-sm ring-1 ring-zinc-200/50">{{ Number(index) + 1 }}</span>
              <p class="pt-0.5 text-[14px] leading-relaxed text-zinc-600">{{ localText(item) }}</p>
            </div>
          </div>
        </div>

        <div v-if="score.strengths?.length" class="rounded-[24px] bg-blue-50/50 p-6 ring-1 ring-blue-100/50">
          <div class="flex items-center gap-2.5 text-[15px] font-semibold tracking-tight text-blue-800">
            <CheckCircle2 class="h-5 w-5" stroke-width="2" />
            值得保留的优势
          </div>
          <div class="mt-4 flex flex-wrap gap-2.5">
            <span v-for="item in score.strengths" :key="item" class="rounded-full bg-white px-4 py-2 text-[13px] font-medium text-blue-700 shadow-sm ring-1 ring-blue-100/50">
              {{ localText(item) }}
            </span>
          </div>
        </div>
      </section>
    </div>

    <div v-else class="flex min-h-full items-center justify-center p-4 md:p-8 text-center">
      <div class="max-w-md">
        <div class="mx-auto flex h-14 w-14 shrink-0 items-center justify-center rounded-[18px] bg-white text-zinc-700 shadow-[0_8px_24px_rgba(0,0,0,0.06)] ring-1 ring-zinc-200/60" style="view-transition-name: ai-hero-icon;">
          <ScanLine class="relative z-10 h-7 w-7" stroke-width="1.5" />
        </div>
        <h3 class="mt-6 text-[22px] font-semibold tracking-tight text-zinc-900">简历诊断</h3>
        <p class="mt-3 text-[15px] leading-relaxed text-zinc-500">从内容完整度、表达质量、岗位匹配和 ATS 友好度等维度，发现简历中的可优化问题。</p>
        <button class="mt-8 rounded-full bg-zinc-900 px-8 py-3.5 text-[15px] font-medium text-white shadow-md transition-all active:scale-[0.98] hover:bg-zinc-800 hover:shadow-lg" @click="$emit('refresh')">开始诊断</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analysis-step { animation: analysis-step 0.6s cubic-bezier(0.25, 0.1, 0.25, 1) both; }
.analysis-dot { animation: analysis-dot 1.2s ease-in-out infinite; }
.score-number { animation: score-resolve 1s cubic-bezier(0.25, 0.1, 0.25, 1) both; }
.diagnosis-card,
.suggestion-row { animation: card-rise 0.6s cubic-bezier(0.25, 0.1, 0.25, 1) both; }
.dimension-progress { transform-origin: left; animation: progress-grow 1s cubic-bezier(0.25, 0.1, 0.25, 1) both; }

@keyframes analysis-step { 
  from { opacity: 0; transform: translateY(10px) scale(0.98); } 
  to { opacity: 1; transform: translateY(0) scale(1); } 
}
@keyframes analysis-dot { 
  0%, 70%, 100% { opacity: 0.2; transform: scale(0.8); } 
  35% { opacity: 1; transform: scale(1.2); } 
}
@keyframes score-resolve { 
  from { opacity: 0; filter: blur(15px); transform: scale(0.8); } 
  to { opacity: 1; filter: blur(0); transform: scale(1); } 
}
@keyframes card-rise { 
  from { opacity: 0; transform: translateY(16px); } 
  to { opacity: 1; transform: translateY(0); } 
}
@keyframes progress-grow { 
  from { transform: scaleX(0); } 
  to { transform: scaleX(1); } 
}
@media (prefers-reduced-motion: reduce) { 
  .analysis-step, .analysis-dot, .score-number, .diagnosis-card, .suggestion-row, .dimension-progress { 
    animation: none !important; 
  } 
}
.icon-morph-anim {
  animation: icon-morph 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both;
  animation-delay: 0.1s;
}
@keyframes icon-morph {
  0% { transform: scale(0.5) rotate(-15deg); opacity: 0; filter: blur(4px); }
  100% { transform: scale(1) rotate(0deg); opacity: 1; filter: blur(0); }
}
</style>
