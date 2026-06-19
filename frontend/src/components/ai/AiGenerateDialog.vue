<script setup lang="ts">
import { ref } from "vue"
import Button from "@/components/ui/button/Button.vue"
import AiLoading from "./AiLoading.vue"
defineProps<{ loading?: boolean; streamText?: string }>()
const emit = defineEmits<{ generate: [payload: any] }>()
const form = ref({
  target_position: "Java 后端开发工程师",
  personal_info: "姓名：\n当前状态：应届生\n学历：\n技能：Java、Spring Boot、MySQL、Redis\n项目：\n工作/实习：\n荣誉奖项：",
  style: "技术型",
})
function submit() {
  emit("generate", {
    target_position: form.value.target_position,
    basics: { title: form.value.target_position },
    education: form.value.personal_info,
    skills: [],
    projects: form.value.personal_info,
    work: form.value.personal_info,
    awards: form.value.personal_info,
    style: form.value.style,
    personal_info: form.value.personal_info,
  })
}
</script>
<template>
  <div class="flex flex-col h-full">
    <div v-if="loading" class="flex flex-col h-full justify-center">
      <AiLoading title="正在建立个人档案" description="AI 正在提取你的个人信息，并按岗位生成结构化简历。" :stream-text="streamText" />
    </div>
    <div v-else class="flex flex-col gap-6 h-full">
      <div class="flex flex-col gap-2">
        <label class="text-[11px] font-semibold uppercase tracking-[0.2em] text-zinc-400 shrink-0 px-2">Target Position</label>
        <input v-model="form.target_position" class="h-12 w-full rounded-[16px] bg-zinc-50/80 px-4 text-[15px] font-medium text-zinc-800 placeholder:text-zinc-400 border-0 ring-1 ring-zinc-200/50 transition-all focus:bg-white focus:ring-blue-500/30 focus:shadow-[0_8px_30px_rgba(16,185,129,0.06)] outline-none" />
      </div>
      <div class="flex flex-col gap-2 flex-1 min-h-0">
        <label class="text-[11px] font-semibold uppercase tracking-[0.2em] text-zinc-400 shrink-0 px-2">Personal Info</label>
        <div class="flex-1 min-h-[300px] relative rounded-[20px] bg-zinc-50/80 ring-1 ring-zinc-200/50 transition-all focus-within:bg-white focus-within:ring-blue-500/30 focus-within:shadow-[0_8px_30px_rgba(16,185,129,0.06)] overflow-hidden">
          <textarea v-model="form.personal_info" placeholder="把姓名、学历、技能、项目、经历、奖项等信息写在这里" class="absolute inset-0 h-full w-full resize-none border-0 bg-transparent p-5 text-[15px] leading-relaxed text-zinc-800 placeholder:text-zinc-400 outline-none thin-scrollbar" style="box-shadow: none;" />
        </div>
      </div>
      <div class="pt-2">
        <Button class="h-14 w-full rounded-full bg-zinc-900 text-[16px] font-medium text-white shadow-md transition-all active:scale-[0.98] hover:bg-zinc-800 hover:shadow-lg" @click="submit">
          生成并创建简历
        </Button>
      </div>
    </div>
  </div>
</template>
