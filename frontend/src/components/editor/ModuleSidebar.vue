<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from "vue"
import { useScroll } from "@vueuse/core"
import { ArrowDown, ArrowUp, Eye, EyeOff, GripVertical, Plus, Trash2, LayoutList, ChevronDown, ChevronLeft, ChevronRight, Sparkles, PanelLeftClose, PanelLeftOpen } from "lucide-vue-next"
import Button from "@/components/ui/button/Button.vue"
import Input from "@/components/ui/input/Input.vue"
import type { ResumeData } from "@/types/resume"

const isMobile = ref(false)
const mobileExpanded = ref(false)
let resizeHandler: () => void

const scrollContainer = ref<HTMLElement | null>(null)
const { x, arrivedState } = useScroll(scrollContainer, { behavior: 'smooth' })

function scrollNav(direction: 'left' | 'right') {
  if (!scrollContainer.value) return
  const offset = 250
  scrollContainer.value.scrollBy({ left: direction === 'left' ? -offset : offset, behavior: 'smooth' })
}

onMounted(() => {
  isMobile.value = window.innerWidth < 768
  resizeHandler = () => { isMobile.value = window.innerWidth < 768 }
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
})

const props = defineProps<{ data: ResumeData; current: string; optimizeLoading?: boolean; formExpanded?: boolean }>()
const emit = defineEmits<{ select: [key: string]; change: []; addCustom: []; removeCustom: [key: string]; optimize: []; togglePanel: [] }>()
const builtIn = ["basics", "summary", "education", "skills", "work", "projects", "awards"]
let draggingKey = ""
const orderedSections = computed(() => ["basics", ...(props.data.layout?.section_order || []).filter((item) => item !== "basics")])

function visible(key: string) {
  if (key === "basics") return true
  return !(props.data.layout?.hidden_sections || []).includes(key)
}
function setVisible(key: string, value: boolean) {
  if (key === "basics") return
  props.data.layout ||= { section_order: [], hidden_sections: [], section_titles: {} }
  props.data.layout.hidden_sections ||= []
  const hidden = props.data.layout.hidden_sections
  if (value) props.data.layout.hidden_sections = hidden.filter((item) => item !== key)
  else if (!hidden.includes(key)) hidden.push(key)
  emit("change")
}

function onDragStart(key: string) {
  if (key === "basics") return
  draggingKey = key
}

function onDrop(targetKey: string) {
  if (targetKey === "basics") return
  if (!draggingKey || draggingKey === targetKey) return
  const order = props.data.layout?.section_order || []
  const from = order.indexOf(draggingKey)
  const to = order.indexOf(targetKey)
  if (from < 0 || to < 0) return
  order.splice(from, 1)
  order.splice(to, 0, draggingKey)
  draggingKey = ""
  emit("change")
}

function move(key: string, offset: number) {
  if (key === "basics") return
  const order = props.data.layout?.section_order || []
  const from = order.indexOf(key)
  const to = from + offset
  if (from < 0 || to <= 0 || to >= order.length) return
  order.splice(from, 1)
  order.splice(to, 0, key)
  emit("select", key)
  emit("change")
}
</script>

<template>
  <div class="w-full shrink-0 border-b border-zinc-200/60 bg-white flex flex-col relative z-20">
    <!-- Module List -->
    <div class="relative w-full overflow-hidden flex items-center group/nav">
      <!-- Left Fade & Arrow -->
      <div v-show="!arrivedState.left" class="absolute left-0 top-0 bottom-0 w-16 bg-gradient-to-r from-white via-white/90 to-transparent z-10 flex items-center justify-start px-2 pointer-events-none transition-opacity duration-300">
        <button @click="scrollNav('left')" class="h-7 w-7 rounded-full bg-white shadow-sm border border-zinc-200 hidden md:flex items-center justify-center text-zinc-500 hover:text-zinc-900 hover:border-zinc-300 transition-all pointer-events-auto opacity-0 group-hover/nav:opacity-100">
          <ChevronLeft class="h-4 w-4" />
        </button>
      </div>

      <div ref="scrollContainer" class="flex items-center overflow-x-auto overflow-y-hidden px-4 py-3 gap-2.5 w-full scrollbar-none [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none] scroll-smooth relative">
        <div
          v-for="element in orderedSections"
          :key="element"
          class="group relative flex items-center shrink-0 h-9 rounded-full px-4 text-[14px] font-medium transition-all duration-300 cursor-pointer border select-none"
          :class="[
            current === element 
              ? 'bg-zinc-900 text-white border-zinc-900 shadow-md' 
              : 'bg-white text-zinc-600 border-zinc-200/80 hover:border-zinc-300 hover:bg-zinc-50 shadow-sm', 
            !visible(element) && 'opacity-50'
          ]"
          :draggable="element !== 'basics' && !isMobile"
          @dragover.prevent
          @drop.prevent="onDrop(element)"
          @dragstart.stop="onDragStart(element)"
          @click="$emit('select', element)"
        >
          <!-- Title Text -->
          <span class="whitespace-nowrap flex items-center">
            <GripVertical v-if="element !== 'basics' && !isMobile" class="h-3.5 w-3.5 mr-1.5 opacity-0 group-hover:opacity-40 transition-opacity" :class="current === element ? 'text-zinc-300' : 'text-zinc-400'" />
            {{ data.layout?.section_titles?.[element] || element }}
          </span>

          <!-- Action Buttons -->
          <div class="flex items-center justify-end gap-1 transition-opacity duration-200"
               :class="[
                 element !== 'basics' ? 'ml-1 -mr-1' : '',
                 !builtIn.includes(element) ? 'w-[44px]' : 'w-[24px]',
                 !isMobile ? 'opacity-0 group-hover:opacity-100' : (current === element ? 'opacity-100' : 'hidden')
               ]"
               v-if="element !== 'basics'">
              <button class="flex items-center justify-center p-1 rounded-full transition-colors" :class="current === element ? 'text-zinc-300 hover:text-white hover:bg-white/20' : 'text-zinc-400 hover:text-zinc-900 hover:bg-zinc-200/50'" title="显示/隐藏" @click.stop="setVisible(element, !visible(element))">
                <Eye v-if="visible(element)" class="h-3.5 w-3.5" />
                <EyeOff v-else class="h-3.5 w-3.5" />
              </button>
              <button v-if="!builtIn.includes(element)" class="flex items-center justify-center p-1 rounded-full transition-colors" :class="current === element ? 'text-red-300 hover:text-red-100 hover:bg-red-500/50' : 'text-zinc-400 hover:text-red-600 hover:bg-red-50'" title="删除" @click.stop="$emit('removeCustom', element)">
                <Trash2 class="h-3.5 w-3.5" />
              </button>
          </div>
        </div>

        <!-- Add Custom Module Button -->
        <button
          class="group flex items-center justify-center shrink-0 h-9 rounded-full px-4 text-[14px] font-medium transition-all duration-200 border border-dashed border-zinc-300 bg-zinc-50/50 text-zinc-500 hover:border-zinc-400 hover:text-zinc-700 hover:bg-zinc-100"
          @click="$emit('addCustom')"
        >
          <Plus class="h-4 w-4 mr-1" />
          添加模块
        </button>
      </div>

      <!-- Right Fade & Arrow -->
      <div v-show="!arrivedState.right" class="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-white via-white/90 to-transparent z-10 flex items-center justify-end px-2 pointer-events-none transition-opacity duration-300">
        <button @click="scrollNav('right')" class="h-7 w-7 rounded-full bg-white shadow-sm border border-zinc-200 hidden md:flex items-center justify-center text-zinc-500 hover:text-zinc-900 hover:border-zinc-300 transition-all pointer-events-auto opacity-0 group-hover/nav:opacity-100">
          <ChevronRight class="h-4 w-4" />
        </button>
      </div>
    </div>
  </div>
</template>
