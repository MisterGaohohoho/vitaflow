<script setup lang="ts">
import { ref } from "vue"
import { Award, Banknote, BookOpen, Briefcase, Building2, Calendar, CalendarCheck, Code2, Cpu, Github, Globe, GraduationCap, Heart, IdCard, Info, Languages, Laptop, Link, Mail, Map, MapPin, Phone, Plus, Rocket, School, Sparkles, Star, Tag, Trash2, Upload, UserRound, Wallet, Wrench } from "lucide-vue-next"
import Button from "@/components/ui/button/Button.vue"
import Input from "@/components/ui/input/Input.vue"
import Label from "@/components/ui/label/Label.vue"
import Select from "@/components/ui/select/Select.vue"
import { uploadAvatarApi } from "@/api/file"

const props = defineProps<{ basics: Record<string, any> }>()
const emit = defineEmits<{ change: [] }>()
const activeIconPicker = ref("")
const coreFields = [
  { key: "name", label: "姓名", placeholder: "请输入姓名" },
  { key: "title", label: "求职方向", placeholder: "例如：Java 后端开发工程师" },
]
const builtInFields = [
  { key: "phone", label: "电话", icon: "Phone" },
  { key: "email", label: "邮箱", icon: "Mail" },
  { key: "status", label: "当前状态", icon: "Info" },
  { key: "location", label: "所在城市", icon: "MapPin" },
  { key: "highest_degree", label: "最高学历", icon: "GraduationCap" },
  { key: "website", label: "个人网站", icon: "Globe" },
  { key: "github", label: "代码仓库", icon: "Github" },
  { key: "expected_salary", label: "期望薪资", icon: "Briefcase" },
]
const iconOptions = [
  { value: "Phone", label: "电话", component: Phone },
  { value: "Mail", label: "邮箱", component: Mail },
  { value: "Info", label: "信息", component: Info },
  { value: "MapPin", label: "地点", component: MapPin },
  { value: "GraduationCap", label: "学历", component: GraduationCap },
  { value: "Globe", label: "网站", component: Globe },
  { value: "Github", label: "代码仓库", component: Github },
  { value: "Briefcase", label: "工作", component: Briefcase },
  { value: "Wallet", label: "薪资", component: Wallet },
  { value: "Banknote", label: "收入", component: Banknote },
  { value: "Calendar", label: "时间", component: Calendar },
  { value: "CalendarCheck", label: "日期确认", component: CalendarCheck },
  { value: "UserRound", label: "个人", component: UserRound },
  { value: "IdCard", label: "证件", component: IdCard },
  { value: "Tag", label: "标签", component: Tag },
  { value: "School", label: "学校", component: School },
  { value: "Building2", label: "公司", component: Building2 },
  { value: "Award", label: "奖项", component: Award },
  { value: "BookOpen", label: "课程", component: BookOpen },
  { value: "Code2", label: "代码", component: Code2 },
  { value: "Cpu", label: "技术", component: Cpu },
  { value: "Laptop", label: "电脑", component: Laptop },
  { value: "Wrench", label: "工具", component: Wrench },
  { value: "Languages", label: "语言", component: Languages },
  { value: "Heart", label: "兴趣", component: Heart },
  { value: "Star", label: "亮点", component: Star },
  { value: "Sparkles", label: "亮点效果", component: Sparkles },
  { value: "Rocket", label: "目标", component: Rocket },
  { value: "Map", label: "地图", component: Map },
  { value: "Link", label: "链接", component: Link },
]
const iconMap = Object.fromEntries(iconOptions.map((item) => [item.value, item.component]))
const rowOptions = [1, 2, 3, 4]
function pickerKey(prefix: string, key: string) {
  return `${prefix}:${key}`
}
function setBuiltInIcon(key: string, icon: string) {
  props.basics.field_config[key].icon = icon
  activeIconPicker.value = ""
  emit("change")
}
function setCustomIcon(field: Record<string, any>, icon: string) {
  field.icon = icon
  activeIconPicker.value = ""
  emit("change")
}
function ensureConfig() {
  props.basics.field_config ||= {}
  builtInFields.forEach((field, index) => {
    props.basics.field_config[field.key] ||= { label: field.label, icon: field.icon, row: Math.floor(index / 4) + 1, order: index + 1 }
    props.basics.field_config[field.key].label = field.label
    props.basics.field_config[field.key].order ||= index + 1
    props.basics.field_config[field.key].row ||= Math.floor(index / 4) + 1
  })
  props.basics.custom_fields ||= []
}
ensureConfig()
async function upload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const result = await uploadAvatarApi(file)
  props.basics.avatar = result.url
  emit("change")
}
function addCustom() {
  ensureConfig()
  props.basics.custom_fields ||= []
  props.basics.custom_fields.push({ id: `field_${Date.now()}`, label: "附加信息", value: "", icon: "Info", row: 1, order: props.basics.custom_fields.length + 1 })
  emit("change")
}
</script>
<template>
  <div class="space-y-6 max-w-3xl mx-auto py-2">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
      <div v-for="field in coreFields" :key="field.key">
        <Label class="text-[13px] text-zinc-600 mb-1.5 block font-medium">{{ field.label }}</Label>
        <Input v-model="basics[field.key]" :placeholder="field.placeholder" class="bg-zinc-50 border-zinc-200/80 shadow-sm focus-visible:bg-white focus-visible:ring-emerald-500/30 focus-visible:border-emerald-500/50 transition-all rounded-[10px]" @update:model-value="$emit('change')" />
      </div>
    </div>
    <div>
      <Label class="text-[13px] text-zinc-600 mb-1.5 block font-medium">头像</Label>
      <div class="flex items-center gap-4">
        <img v-if="basics.avatar" :src="basics.avatar" class="h-14 w-14 rounded-lg object-cover" />
        <label class="inline-flex h-10 cursor-pointer items-center gap-2 rounded-lg border border-gray-200 px-3 text-sm"><Upload class="h-4 w-4" />上传<input type="file" class="hidden" @change="upload" /></label>
      </div>
    </div>
    <div class="rounded-xl border border-zinc-200/80 bg-white shadow-sm overflow-hidden">
      <div class="flex items-center justify-between p-3 md:p-4 border-b border-zinc-100/80">
        <h3 class="text-sm font-semibold text-zinc-900">基本信息</h3>
        <Button size="sm" variant="outline" class="h-8 border-zinc-200" @click="addCustom"><Plus class="h-4 w-4 md:mr-1" /><span class="hidden md:inline">添加字段</span></Button>
      </div>
      <div class="p-2 md:p-3 space-y-2">
        <div v-for="field in builtInFields" :key="field.key" class="flex items-center gap-2 md:gap-3 p-2 rounded-xl border border-zinc-100 hover:border-zinc-300 hover:shadow-sm bg-zinc-50/50 hover:bg-white transition-all group">
          <!-- Icon Picker -->
          <div class="relative shrink-0">
            <button class="flex h-9 w-9 items-center justify-center rounded-lg border border-zinc-200 bg-white hover:border-zinc-400 hover:bg-zinc-50 transition-colors shadow-sm" :title="basics.field_config[field.key].icon" @click="activeIconPicker = activeIconPicker === pickerKey('builtin', field.key) ? '' : pickerKey('builtin', field.key)">
              <component :is="iconMap[basics.field_config[field.key].icon] || Info" class="h-4 w-4 text-zinc-600" />
            </button>
            <div v-if="activeIconPicker === pickerKey('builtin', field.key)" class="absolute left-0 top-11 z-30 grid w-56 grid-cols-6 gap-1 rounded-xl border border-zinc-200 bg-white/95 backdrop-blur-md p-2 shadow-xl">
              <button v-for="icon in iconOptions" :key="icon.value" class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-zinc-100 transition-colors" :title="icon.label" @click="setBuiltInIcon(field.key, icon.value)">
                <component :is="icon.component" class="h-4 w-4 text-zinc-700" />
              </button>
            </div>
          </div>
          
          <!-- Label -->
          <div class="hidden md:block w-16 shrink-0 text-[14px] font-medium text-zinc-700 px-1">{{ field.label }}</div>
          
          <!-- Content Input -->
          <Input v-model="basics[field.key]" :placeholder="field.label" class="flex-1 min-w-0 h-9 bg-white shadow-sm border-zinc-200" @update:model-value="$emit('change')" />
          
          <!-- Row Segmented Control -->
          <div class="shrink-0 flex items-center bg-zinc-100/80 p-1 rounded-lg border border-zinc-200/50" title="排版行数">
            <button v-for="r in 4" :key="r" class="w-6 md:w-7 h-6 md:h-7 rounded-md flex items-center justify-center text-[13px] font-medium transition-all" :class="basics.field_config[field.key].row === r ? 'bg-white text-zinc-900 shadow-sm ring-1 ring-zinc-200/50' : 'text-zinc-500 hover:text-zinc-700 hover:bg-zinc-200/50'" @click="basics.field_config[field.key].row = r; $emit('change')">
              {{ r }}
            </button>
          </div>
        </div>

        <div v-for="(field, i) in basics.custom_fields" :key="field.id" class="flex items-center gap-2 md:gap-3 p-2 rounded-xl border border-zinc-100 hover:border-zinc-300 hover:shadow-sm bg-zinc-50/50 hover:bg-white transition-all group">
          <!-- Icon Picker -->
          <div class="relative shrink-0">
            <button class="flex h-9 w-9 items-center justify-center rounded-lg border border-zinc-200 bg-white hover:border-zinc-400 hover:bg-zinc-50 transition-colors shadow-sm" :title="field.icon" @click="activeIconPicker = activeIconPicker === pickerKey('custom', field.id) ? '' : pickerKey('custom', field.id)">
              <component :is="iconMap[field.icon] || Info" class="h-4 w-4 text-zinc-600" />
            </button>
            <div v-if="activeIconPicker === pickerKey('custom', field.id)" class="absolute left-0 top-11 z-30 grid w-56 grid-cols-6 gap-1 rounded-xl border border-zinc-200 bg-white/95 backdrop-blur-md p-2 shadow-xl">
              <button v-for="icon in iconOptions" :key="icon.value" class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-zinc-100 transition-colors" :title="icon.label" @click="setCustomIcon(field, icon.value)">
                <component :is="icon.component" class="h-4 w-4 text-zinc-700" />
              </button>
            </div>
          </div>
          
          <!-- Label -->
          <div class="hidden md:block w-16 shrink-0 text-[14px] font-medium text-zinc-500 px-1">自定义</div>
          
          <!-- Content Input -->
          <Input v-model="field.value" placeholder="附加内容" class="flex-1 min-w-0 h-9 bg-white shadow-sm border-zinc-200" @update:model-value="$emit('change')" />
          
          <!-- Row Segmented Control -->
          <div class="shrink-0 flex items-center bg-zinc-100/80 p-1 rounded-lg border border-zinc-200/50" title="排版行数">
            <button v-for="r in 4" :key="r" class="w-6 md:w-7 h-6 md:h-7 rounded-md flex items-center justify-center text-[13px] font-medium transition-all" :class="field.row === r ? 'bg-white text-zinc-900 shadow-sm ring-1 ring-zinc-200/50' : 'text-zinc-500 hover:text-zinc-700 hover:bg-zinc-200/50'" @click="field.row = r; $emit('change')">
              {{ r }}
            </button>
          </div>

          <!-- Delete -->
          <Button size="icon" variant="ghost" class="shrink-0 h-9 w-9 hover:bg-red-50 hover:text-red-600 rounded-lg text-zinc-400" @click="basics.custom_fields.splice(i, 1); $emit('change')"><Trash2 class="h-4 w-4" /></Button>
        </div>
      </div>
    </div>
  </div>
</template>
