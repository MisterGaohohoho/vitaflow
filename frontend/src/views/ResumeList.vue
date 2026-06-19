<script setup lang="ts">
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { Copy, FileText, Plus, Trash2, X, Sparkles, FileStack, CheckCircle2, AlertTriangle } from "lucide-vue-next"
import AppLayout from "@/components/layout/AppLayout.vue"
import Button from "@/components/ui/button/Button.vue"
import Badge from "@/components/ui/badge/Badge.vue"
import { useResumeStore } from "@/stores/resume"
import AiGenerateDialog from "@/components/ai/AiGenerateDialog.vue"
import { generateResumeStreamApi } from "@/api/ai"
import { listTemplatesApi, type TemplateItem } from "@/api/template"
import TemplatePreview from "@/components/templates/TemplatePreview.vue"

const router = useRouter()
const store = useResumeStore()
const showAiCreate = ref(false)
const showTemplateSelect = ref(false)
const showDeleteConfirm = ref(false)
const resumeToDelete = ref<number | null>(null)

const aiLoading = ref(false)
const aiError = ref("")
const aiStreamText = ref("")
const toastMessage = ref("")

const templates = ref<TemplateItem[]>([])
const templateNames: Record<string, string> = {
  classic: "经典单栏",
  tech: "技术岗位",
  modern: "现代双栏",
  blue_timeline: "极简时间轴",
}
onMounted(async () => {
  await store.fetchResumeList()
  templates.value = await listTemplatesApi()
})
async function openTemplateSelect() {
  showTemplateSelect.value = true
  if (!templates.value.length) templates.value = await listTemplatesApi()
}
async function createResume(templateId: string) {
  const item = await store.createResume(templateId)
  showTemplateSelect.value = false
  router.push(`/resumes/${item.id}/edit`)
}
async function generateResume(payload: any) {
  aiLoading.value = true
  aiError.value = ""
  aiStreamText.value = ""
  try {
    const result = await generateResumeStreamApi(payload, {
      onDelta: (text) => (aiStreamText.value += text),
    })
    const item = await store.createResumeFromAi(result)
    showAiCreate.value = false
    router.push(`/resumes/${item.id}/edit`)
  } catch (error: any) {
    aiError.value = error.message || "AI 生成失败"
  } finally {
    aiLoading.value = false
  }
}
function goToEdit(id: number) {
  router.push(`/resumes/${id}/edit`)
}

function showToast(message: string) {
  toastMessage.value = message
  setTimeout(() => {
    if (toastMessage.value === message) {
      toastMessage.value = ""
    }
  }, 2500)
}

async function handleDuplicate(id: number) {
  try {
    await store.duplicateResume(id)
    showToast("复制成功")
  } catch (error) {
    showToast("复制失败，请重试")
  }
}

function triggerDelete(id: number) {
  resumeToDelete.value = id
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  if (resumeToDelete.value === null) return
  try {
    await store.deleteResume(resumeToDelete.value)
    showDeleteConfirm.value = false
    resumeToDelete.value = null
    showToast("删除成功")
  } catch (error) {
    showToast("删除失败，请重试")
  }
}
</script>

<template>
  <AppLayout>
    <main class="mx-auto max-w-7xl px-4 sm:px-6 py-6 md:py-14 relative">
      <!-- Toast Notification -->
      <Transition name="toast-slide">
        <div v-if="toastMessage" class="fixed bottom-10 left-1/2 -translate-x-1/2 z-[100] flex items-center gap-2 rounded-full bg-zinc-900 px-6 py-3 text-sm font-medium text-white shadow-xl border border-zinc-800">
          <CheckCircle2 v-if="toastMessage.includes('成功')" class="h-4 w-4 text-blue-400" />
          {{ toastMessage }}
        </div>
      </Transition>

      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-6 mb-10">
        <div>
          <h1 class="text-3xl font-semibold text-zinc-900 tracking-tight">工作台</h1>
          <p class="mt-2 text-sm text-zinc-500">管理、编辑并导出你的极简专业简历</p>
        </div>
        <div class="flex flex-wrap gap-3">
          <Button variant="outline" class="h-10 px-4 border-zinc-200 text-zinc-700 transition-colors hover:bg-zinc-50 hover:text-zinc-900" @click="showAiCreate = true">
            <Sparkles class="h-4 w-4 mr-2" /> AI 智能生成
          </Button>
          <Button class="h-10 px-4 bg-zinc-900 text-white hover:bg-zinc-800 transition-all active:scale-95 shadow-sm" @click="openTemplateSelect">
            <Plus class="h-4 w-4 mr-2" /> 新建空白简历
          </Button>
        </div>
      </div>

      <!-- Template Select Modal -->
      <Transition name="fade">
        <div v-if="showTemplateSelect" class="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/40 backdrop-blur-sm p-4 sm:p-6">
          <section class="w-full max-w-5xl max-h-[90vh] flex flex-col rounded-2xl bg-white shadow-2xl overflow-hidden transform transition-all" @click.stop>
            <div class="flex items-center justify-between border-b border-zinc-100 px-6 py-5 bg-zinc-50/50">
              <div>
                <h2 class="text-lg font-semibold text-zinc-900 tracking-tight">选择简历模板</h2>
                <p class="mt-1 text-xs text-zinc-500">挑选一个符合你行业风格的极简模板</p>
              </div>
              <button class="p-2 text-zinc-400 hover:bg-zinc-200/50 hover:text-zinc-600 rounded-full transition-colors" @click="showTemplateSelect = false">
                <X class="h-5 w-5" />
              </button>
            </div>
            <div class="flex-1 overflow-y-auto p-4 sm:p-6 bg-zinc-50/30 thin-scrollbar">
              <div class="grid gap-4 sm:gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <article v-for="item in templates" :key="item.template_id" class="group flex flex-col rounded-xl border border-zinc-200/60 bg-white p-4 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:border-zinc-300 cursor-pointer" @click="createResume(item.template_id)">
                  <div class="relative w-full aspect-[4/3] overflow-hidden rounded-md bg-white border border-zinc-100 transition-transform duration-300 group-hover:scale-[1.02] shadow-sm">
                    <div class="absolute inset-x-0 top-0">
                      <TemplatePreview :html="item.preview_html" />
                    </div>
                    <div class="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-white to-transparent pointer-events-none"></div>
                  </div>
                  <div class="mt-4 flex flex-col gap-2 flex-1">
                    <h3 class="font-medium text-zinc-900 text-sm">{{ item.name }}</h3>
                    <p class="text-xs text-zinc-500">{{ item.category }}适用</p>
                  </div>
                </article>
              </div>
            </div>
          </section>
        </div>
      </Transition>

      <!-- AI Generation Modal -->
      <Transition name="fade">
        <div v-if="showAiCreate" class="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/40 backdrop-blur-sm p-4">
          <div class="flex max-h-[calc(100vh-2rem)] w-full max-w-lg flex-col overflow-hidden rounded-2xl bg-white shadow-2xl transform transition-all" @click.stop>
            <div class="shrink-0 flex items-center justify-between border-b border-zinc-100 px-6 py-5 bg-zinc-50/50">
              <div>
                <h2 class="text-lg font-semibold text-zinc-900 tracking-tight flex items-center gap-2">
                  <Sparkles class="w-4 h-4 text-zinc-700"/> AI 智能生成
                </h2>
                <p class="mt-1 text-xs text-zinc-500">输入基础信息，AI 将为你提炼出彩简历</p>
              </div>
              <button class="p-2 text-zinc-400 hover:bg-zinc-200/50 hover:text-zinc-600 rounded-full transition-colors" @click="showAiCreate = false">
                <X class="h-5 w-5" />
              </button>
            </div>
            <div class="min-h-0 flex-1 overflow-y-auto p-4 sm:p-6 thin-scrollbar">
              <p v-if="aiError" class="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-600">{{ aiError }}</p>
              <AiGenerateDialog :loading="aiLoading" :stream-text="aiStreamText" @generate="generateResume" />
            </div>
          </div>
        </div>
      </Transition>

      <!-- Delete Confirmation Modal -->
      <Transition name="fade">
        <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/40 backdrop-blur-sm p-4">
          <div class="w-full max-w-sm rounded-2xl bg-white shadow-2xl overflow-hidden transform transition-all" @click.stop>
            <div class="p-6 text-center">
              <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100 mb-4">
                <AlertTriangle class="h-6 w-6 text-red-600" />
              </div>
              <h2 class="text-lg font-semibold text-zinc-900 tracking-tight">确认删除简历？</h2>
              <p class="mt-2 text-sm text-zinc-500">删除后将无法恢复，确定要继续吗？</p>
            </div>
            <div class="flex gap-3 px-6 py-4 bg-zinc-50/50">
              <Button variant="outline" class="flex-1 bg-white border-zinc-200 text-zinc-700 hover:bg-zinc-100 transition-colors" @click="showDeleteConfirm = false; resumeToDelete = null">取消</Button>
              <Button class="flex-1 bg-red-600 text-white hover:bg-red-700 transition-all shadow-sm active:scale-95" @click="confirmDelete">确认删除</Button>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Resume List -->
      <div v-if="store.resumeList.length" class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <div v-for="item in store.resumeList" :key="item.id" 
             class="group relative flex flex-col rounded-xl border border-zinc-200/70 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_12px_30px_-10px_rgba(0,0,0,0.08)] hover:border-zinc-300 cursor-pointer overflow-hidden"
             @click="goToEdit(item.id)">
          
          <!-- Hover Actions overlayed on the preview -->
          <div class="absolute right-3 top-3 flex gap-1.5 opacity-0 transition-opacity duration-200 group-hover:opacity-100 z-10">
            <button class="p-2 text-zinc-600 bg-white/95 backdrop-blur shadow-sm hover:text-zinc-900 rounded-lg hover:bg-white transition-colors border border-zinc-200/50" @click.stop="handleDuplicate(item.id)" title="复制">
              <Copy class="h-4 w-4" />
            </button>
            <button class="p-2 text-zinc-600 bg-white/95 backdrop-blur shadow-sm hover:text-red-600 rounded-lg hover:bg-red-50 hover:border-red-100 transition-colors border border-zinc-200/50" @click.stop="triggerDelete(item.id)" title="删除">
              <Trash2 class="h-4 w-4" />
            </button>
          </div>

          <!-- Preview Area -->
          <div class="relative w-full bg-zinc-50/50 border-b border-zinc-100/80 overflow-hidden group-hover:bg-zinc-100/50 transition-colors">
            <div class="p-4 sm:p-5">
              <div class="relative w-full aspect-[4/3] overflow-hidden rounded-md shadow-[0_2px_10px_rgba(0,0,0,0.04)] border border-zinc-200/50 transition-transform duration-500 group-hover:scale-[1.02] bg-white">
                <div class="absolute inset-x-0 top-0">
                  <TemplatePreview :html="templates.find(t => t.template_id === item.template_id)?.preview_html" />
                </div>
                <div class="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-white to-transparent pointer-events-none"></div>
              </div>
            </div>
            <!-- Gradient overlay for actions -->
            <div class="absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-black/5 to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"></div>
          </div>

          <!-- Content -->
          <div class="p-5 flex flex-col flex-1 bg-white relative z-10">
            <h2 class="text-base font-semibold text-zinc-900 tracking-tight line-clamp-1 mb-1">{{ item.title }}</h2>
            <p class="text-xs text-zinc-500 mb-4">最后更新于最近 · 简体中文</p>
            <div class="mt-auto flex items-center justify-between">
              <Badge variant="secondary" class="bg-zinc-50 text-zinc-600 font-normal border border-zinc-200/50">{{ templateNames[item.template_id] || "自定义模板" }}</Badge>
              <span class="text-xs font-medium text-zinc-400 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                点击编辑 &rarr;
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="mt-12 flex flex-col items-center justify-center rounded-2xl border border-dashed border-zinc-200 bg-white py-24 px-6 text-center shadow-sm">
        <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-zinc-50 border border-zinc-100">
          <FileStack class="h-8 w-8 text-zinc-300" />
        </div>
        <h2 class="mt-6 text-lg font-medium text-zinc-900 tracking-tight">空空如也</h2>
        <p class="mt-2 max-w-sm text-sm text-zinc-500">你还没有创建任何简历。选择一个心仪的模板开始，或者让 AI 帮你快速搞定。</p>
        <div class="mt-8 flex gap-4">
          <Button class="bg-zinc-900 text-white hover:bg-zinc-800 transition-all active:scale-95 shadow-sm px-6" @click="openTemplateSelect">新建空白简历</Button>
        </div>
      </div>
    </main>
  </AppLayout>
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
.fade-enter-active > div,
.fade-leave-active > div,
.fade-enter-active section,
.fade-leave-active section {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease;
}
.fade-enter-from > div,
.fade-enter-from section {
  transform: scale(0.96) translateY(10px);
  opacity: 0;
}
.fade-leave-to > div,
.fade-leave-to section {
  transform: scale(0.96) translateY(10px);
  opacity: 0;
}

/* Toast Transition */
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-slide-enter-from,
.toast-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, 20px);
}
</style>
