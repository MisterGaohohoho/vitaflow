<script setup lang="ts">
import Input from "@/components/ui/input/Input.vue"
import Label from "@/components/ui/label/Label.vue"
import Switch from "@/components/ui/switch/Switch.vue"
import Select from "@/components/ui/select/Select.vue"
import type { TemplateConfig } from "@/types/resume"
const props = defineProps<{ config: TemplateConfig }>()
defineEmits<{ change: [] }>()
const numberFields = [
  "name_font_size",
  "title_font_size",
  "body_font_size",
  "line_height",
  "page_margin_top",
  "page_margin_bottom",
  "next_page_margin_top",
  "next_page_margin_bottom",
  "page_margin_right",
  "page_margin_left",
  "section_margin_top",
  "section_margin_bottom",
  "section_title_margin_bottom",
]
const fieldLabels: Record<string, string> = {
  name_font_size: "姓名字号",
  title_font_size: "标题字号",
  body_font_size: "正文字号",
  line_height: "正文行高",
  page_margin_top: "首页上边距",
  page_margin_right: "右边距",
  page_margin_bottom: "首页下边距",
  page_margin_left: "左边距",
  next_page_margin_top: "续页上边距",
  next_page_margin_bottom: "续页下边距",
  section_margin_top: "模块上间距",
  section_margin_bottom: "模块下间距",
  section_title_margin_bottom: "模块标题间距",
}
const templates = [
  { value: "classic", label: "经典单栏" },
  { value: "tech", label: "技术蓝线" },
  { value: "modern", label: "现代侧栏" },
  { value: "blue_timeline", label: "蓝色时间轴" },
]
const fonts = [
  { value: "vf-sans", label: "简洁黑体" },
  { value: "vf-serif", label: "正式宋体" },
  { value: "vf-rounded", label: "温和圆体" },
  { value: "vf-kai", label: "文雅楷体" },
]
function getConfigValue(field: string) {
  return (props.config as unknown as Record<string, number>)[field]
}
function setConfigValue(field: string, value: string) {
  ;(props.config as unknown as Record<string, number>)[field] = Number(value)
}
function selectFont(value: string) {
  props.config.font_family = value
}
</script>
<template>
  <div class="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
    <h3 class="text-sm font-semibold">样式设置</h3>
    <div><Label>模板</Label><Select v-model="config.template_id" :options="templates" @change="$emit('change')" class="w-full mt-1.5" /></div>
    <div>
      <Label>字体</Label>
      <Select v-model="config.font_family" :options="fonts" @change="$emit('change')" class="w-full mt-1.5" />
    </div>
    <div class="grid grid-cols-2 gap-3">
      <div><Label>主题色</Label><input v-model="config.theme_color" type="color" class="h-9 w-full rounded-md border border-gray-200" @input="$emit('change')" /></div>
      <div><Label>姓名颜色</Label><input v-model="config.name_font_color" type="color" class="h-9 w-full rounded-md border border-gray-200" @input="$emit('change')" /></div>
      <div><Label>标题颜色</Label><input v-model="config.title_font_color" type="color" class="h-9 w-full rounded-md border border-gray-200" @input="$emit('change')" /></div>
      <div><Label>正文颜色</Label><input v-model="config.body_font_color" type="color" class="h-9 w-full rounded-md border border-gray-200" @input="$emit('change')" /></div>
      <div><Label>白底图标</Label><input v-model="config.icon_color" type="color" class="h-9 w-full rounded-md border border-gray-200" @input="$emit('change')" /></div>
      <div><Label>深色背景图标</Label><input v-model="config.header_icon_color" type="color" class="h-9 w-full rounded-md border border-gray-200" @input="$emit('change')" /></div>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <div v-for="field in numberFields" :key="field"><Label>{{ fieldLabels[field] }}</Label><Input :model-value="getConfigValue(field)" type="number" @update:model-value="setConfigValue(field, $event); $emit('change')" /></div>
    </div>
    <div class="flex items-center justify-between"><Label>显示头像</Label><Switch v-model="config.show_avatar" @update:model-value="$emit('change')" /></div>
  </div>
</template>
