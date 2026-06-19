<script setup lang="ts">
import Label from "@/components/ui/label/Label.vue"
import Input from "@/components/ui/input/Input.vue"
import MarkdownEditor from "./MarkdownEditor.vue"

const props = defineProps<{ item: any; sectionKey: string }>()
const emit = defineEmits<{ change: [] }>()

const fieldLabels: Record<string, string> = {
  school: "学校", major: "专业", degree: "学历", start_date: "开始时间", end_date: "结束时间",
  name: "名称", keywords: "关键词", company: "公司", position: "职位", role: "角色",
  tech_stack: "技术栈", date: "时间",
}

const sectionHints: Record<string, { description: string; highlights: string }> = {
  education: { description: "例如：主修课程、GPA、竞赛经历等", highlights: "每行一条学习成果" },
  skills: { description: "例如：熟悉 Spring Boot、MySQL、Redis，有接口设计和性能优化经验", highlights: "每行一条技能亮点" },
  work: { description: "例如：负责的业务、技术栈、协作方式和结果", highlights: "每行一条工作成果" },
  projects: { description: "例如：项目背景、职责范围、核心技术和上线结果", highlights: "每行一条项目亮点" },
  awards: { description: "例如：奖项级别、获奖背景或作品说明", highlights: "每行一条说明" },
}

function splitInputTags(value: unknown) {
  if (Array.isArray(value)) return value.map((item) => String(item).trim()).filter(Boolean)
  return String(value ?? "").split(/[,，、;；\n\r]+/).map((item) => item.trim()).filter(Boolean)
}

function getFieldValue(item: any, key: string) {
  if (key === "keywords" && Array.isArray(item[key])) return item[key].join(", ")
  return item[key]
}

function setFieldValue(item: any, key: string, value: unknown) {
  item[key] = key === "keywords" ? splitInputTags(value) : value
  emit("change")
}
</script>
<template>
  <div class="px-5 py-5 sm:px-6 sm:py-6">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div v-for="key in Object.keys(item).filter(k => !['id','description','highlights'].includes(k))" :key="key">
        <Label class="text-[13px] text-zinc-600 mb-1.5 block font-medium">{{ fieldLabels[key] || key }}</Label>
        <Input 
          :model-value="getFieldValue(item, key)" 
          :placeholder="fieldLabels[key] || ''" 
          @update:model-value="setFieldValue(item, key, $event)"
          class="bg-zinc-50 border-zinc-200/80 shadow-sm focus-visible:bg-white focus-visible:ring-emerald-500/30 focus-visible:border-emerald-500/50 transition-all rounded-[10px]" 
        />
      </div>
    </div>
    <div class="mt-4">
      <Label class="text-[13px] text-zinc-600 mb-1.5 block font-medium">详细说明</Label>
      <MarkdownEditor v-model="item.description" :placeholder="sectionHints[sectionKey]?.description || '填写详细说明'" @update:model-value="$emit('change')" />
    </div>
    <div v-if="'highlights' in item" class="mt-4">
      <Label class="text-[13px] text-zinc-600 mb-1.5 block font-medium">亮点，每行一条</Label>
      <MarkdownEditor :model-value="(item.highlights || []).join('\n')" :placeholder="sectionHints[sectionKey]?.highlights || '每行一条亮点'" @update:model-value="item.highlights = $event.split('\n').filter(Boolean); $emit('change')" />
    </div>
  </div>
</template>
