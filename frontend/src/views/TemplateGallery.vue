<script setup lang="ts">
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import AppLayout from "@/components/layout/AppLayout.vue"
import Button from "@/components/ui/button/Button.vue"
import TemplatePreview from "@/components/templates/TemplatePreview.vue"
import { listTemplatesApi, type TemplateItem } from "@/api/template"
import { useResumeStore } from "@/stores/resume"

const router = useRouter()
const store = useResumeStore()
const templates = ref<TemplateItem[]>([])

onMounted(async () => {
  templates.value = await listTemplatesApi()
})

async function useTemplate(templateId: string) {
  const token = localStorage.getItem("vitaflow_token")
  if (!token) {
    router.push('/login')
    return
  }
  const item = await store.createResume(templateId)
  router.push(`/resumes/${item.id}/edit`)
}
</script>

<template>
  <AppLayout>
    <main class="mx-auto max-w-7xl px-4 sm:px-6 py-8 md:py-16">
      <!-- Header Area -->
      <div class="max-w-2xl">
        <h1 class="text-3xl font-semibold text-zinc-900 tracking-tight">模板中心</h1>
        <p class="mt-3 text-sm text-zinc-500 leading-relaxed">
          挑选一个符合你行业风格的极简模板，开启专业简历之旅。<br />
          所有模板均经过专业优化，排版精良，开箱即用。
        </p>
      </div>
      
      <!-- Templates Grid -->
      <div class="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <article v-for="item in templates" :key="item.template_id" 
                 class="group relative flex flex-col rounded-[2rem] bg-white p-2.5 shadow-sm ring-1 ring-zinc-100 transition-all duration-500 hover:shadow-2xl hover:shadow-zinc-200/50 hover:ring-zinc-200 hover:-translate-y-2">
          
          <!-- Preview Image Area -->
          <div class="relative w-full aspect-[1/1.1] overflow-hidden rounded-[1.5rem] bg-zinc-50 pointer-events-none border border-zinc-100/80">
            <div class="absolute inset-x-0 top-0 w-full transform transition-transform duration-700 ease-out group-hover:scale-[1.05]">
              <TemplatePreview :html="item.preview_html" />
            </div>
            <!-- Soft fade at bottom -->
            <div class="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-zinc-50 via-zinc-50/80 to-transparent pointer-events-none"></div>
          </div>
          
          <!-- Content Info -->
          <div class="mt-5 mb-1 flex flex-col flex-1 px-3">
            <div class="flex items-center justify-between mb-4">
              <h2 class="font-medium tracking-tight text-zinc-900">{{ item.name }}</h2>
              <span class="inline-flex items-center rounded-full bg-zinc-100 px-2.5 py-1 text-[10px] font-semibold text-zinc-600 transition-colors uppercase tracking-wider">
                {{ item.category }}
              </span>
            </div>
            <div class="mt-auto">
              <Button class="w-full bg-zinc-900 text-white hover:bg-zinc-800 transition-all duration-300 shadow-md rounded-xl font-medium active:scale-[0.98] border-none" @click="useTemplate(item.template_id)">
                开始使用
              </Button>
            </div>
          </div>
        </article>
      </div>
    </main>
  </AppLayout>
</template>
