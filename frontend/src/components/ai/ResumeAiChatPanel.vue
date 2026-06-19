<script setup lang="ts">
import { nextTick, ref, watch, computed } from "vue"
import { CheckCircle2, LoaderCircle, SendHorizontal, Bot, Search, Target, Wand2, Scissors, Trash2, X } from "lucide-vue-next"
import Button from "@/components/ui/button/Button.vue"
import { renderMarkdown } from "@/lib/markdown"

type ChatMessage = {
  id: number | string
  role: "user" | "assistant"
  content: string
  suggestions?: string[]
  optimized_resume_data?: any
  action_status?: "none" | "pending" | "applying" | "applied" | "rejected"
  streaming?: boolean
  phase?: string
  phaseText?: string
}

const props = defineProps<{
  messages: ChatMessage[]
  loading?: boolean
  error?: string
  decisionLoadingId?: number | string | null
}>()

const emit = defineEmits<{
  send: [content: string]
  clear: []
  confirm: [message: ChatMessage]
  reject: [message: ChatMessage]
}>()

const input = ref("")
const inputRef = ref<HTMLTextAreaElement | null>(null)
const composing = ref(false)
const listRef = ref<HTMLElement | null>(null)

const quickPrompts = [
  { text: "这份简历还缺什么？", icon: Search, title: "深度体检", desc: "发现缺失加分项", bg: "bg-blue-50", color: "text-blue-500", ring: "hover:ring-blue-200" },
  { text: "帮我把个人简介写得更适合当前岗位", icon: Target, title: "重构简介", desc: "更贴合岗位需求", bg: "bg-indigo-50", color: "text-indigo-500", ring: "hover:ring-indigo-200" },
  { text: "项目经历怎么突出亮点？", icon: Wand2, title: "提炼亮点", desc: "让项目脱颖而出", bg: "bg-violet-50", color: "text-violet-500", ring: "hover:ring-violet-200" },
  { text: "帮我检查有没有可以删减的内容", icon: Scissors, title: "精简冗余", desc: "去除非核心内容", bg: "bg-rose-50", color: "text-rose-500", ring: "hover:ring-rose-200" }
]

function adjustHeight() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

watch(
  () => [props.messages.length, props.loading, props.messages[props.messages.length - 1]?.content],
  async (newVals, oldVals) => {
    await nextTick()
    if (listRef.value) {
      // Only smooth scroll if the number of messages actually increased
      const isNewMessage = oldVals && newVals[0] > oldVals[0];
      listRef.value.scrollTo({
        top: listRef.value.scrollHeight,
        behavior: isNewMessage ? 'smooth' : 'auto'
      })
    }
  },
  { immediate: true },
)

function submit(event?: Event) {
  const keyEvent = event instanceof KeyboardEvent ? event : null
  if (composing.value || keyEvent?.isComposing || keyEvent?.keyCode === 229) return
  const text = input.value.trim()
  if (!text || props.loading) return
  input.value = ""
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
  }
  emit("send", text)
}

function sendQuick(text: string) {
  if (props.loading) return
  input.value = ""
  emit("send", text)
}

function actionStatus(message: ChatMessage) {
  if (!message.optimized_resume_data) return "none"
  return message.action_status || "pending"
}

const lastAssistantIndex = computed(() => {
  for (let i = props.messages.length - 1; i >= 0; i--) {
    if (props.messages[i].role === 'assistant') return i
  }
  return -1
})
</script>

<template>
  <div class="flex h-full min-h-0 flex-col gap-4 relative">
    <div class="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full bg-blue-500/10 blur-[80px]"></div>
    
    <div v-if="messages.length > 0" class="absolute right-4 top-4 z-20">
      <button @click="emit('clear')" class="flex items-center gap-1.5 rounded-full bg-white/80 px-3 py-1.5 text-[12px] font-medium text-zinc-500 shadow-sm ring-1 ring-zinc-200/60 backdrop-blur-md transition-all hover:bg-rose-50 hover:text-rose-600 hover:ring-rose-200" title="清空对话记录">
        <Trash2 class="h-3.5 w-3.5" />
        清空
      </button>
    </div>
    <section class="chat-stage relative flex min-h-0 flex-1 flex-col bg-transparent z-10">
      <div ref="listRef" class="relative min-h-0 flex-1 flex flex-col overflow-y-auto px-5 py-6 md:px-6 md:py-8 thin-scrollbar">
        <section v-if="!messages.length && !loading" class="mx-auto flex w-full min-h-full max-w-xl flex-col items-center justify-center py-6 text-center">
          <div class="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-[18px] bg-white text-zinc-700 shadow-[0_8px_24px_rgba(0,0,0,0.06)] ring-1 ring-zinc-200/60" style="view-transition-name: ai-hero-icon;">
            <Bot class="relative z-10 h-7 w-7" stroke-width="1.5" />
          </div>
          <h3 class="mt-2.5 text-[20px] font-medium tracking-tight text-zinc-900">简历打磨，现在开始。</h3>
          
          <div class="mt-8 grid w-full grid-cols-2 gap-3 px-1">
            <button v-for="prompt in quickPrompts" :key="prompt.text" class="group relative flex flex-col items-start overflow-hidden rounded-[20px] bg-white ring-1 ring-zinc-200/60 p-3.5 text-left transition-all duration-300 active:scale-[0.97] hover:shadow-[0_8px_20px_rgba(0,0,0,0.04)] hover:-translate-y-0.5" :class="prompt.ring" @click="sendQuick(prompt.text)">
              <div class="absolute -right-6 -top-6 h-20 w-20 rounded-full blur-2xl transition-opacity duration-500 opacity-0 group-hover:opacity-100" :class="prompt.bg"></div>
              <div class="relative z-10 flex h-8 w-8 items-center justify-center rounded-[12px] ring-1 ring-white/50 mb-2.5 transition-transform duration-300 group-hover:scale-110" :class="[prompt.bg, prompt.color]">
                <component :is="prompt.icon" class="h-4 w-4" stroke-width="2" />
              </div>
              <div class="relative z-10 text-[13px] font-semibold text-zinc-900">{{ prompt.title }}</div>
              <div class="relative z-10 mt-0.5 text-[11px] text-zinc-500 line-clamp-1">{{ prompt.desc }}</div>
            </button>
          </div>
        </section>

        <TransitionGroup name="message-list" tag="div" class="space-y-7">
          <article v-for="(message, index) in messages" :key="message.id" class="flex gap-4" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
            <div v-if="message.role === 'assistant'" class="self-end mb-2 flex h-9 w-9 shrink-0 items-center justify-center rounded-[14px] bg-white text-zinc-700 shadow-[0_4px_12px_rgba(0,0,0,0.04)] ring-1 ring-zinc-200/60" :style="index === lastAssistantIndex ? 'view-transition-name: ai-hero-icon;' : ''">
              <Bot class="h-5 w-5" stroke-width="1.5" />
            </div>
            
            <div :class="message.role === 'assistant' ? 'assistant-message-shell' : 'max-w-[75%]'">
              <div class="message-bubble relative text-[15px] leading-relaxed transition-all" :class="message.role === 'user' ? 'rounded-[24px] rounded-tr-[8px] bg-zinc-100 px-5 py-3.5 text-zinc-900' : 'rounded-[24px] rounded-tl-[8px] bg-white px-6 py-5 text-zinc-800 ring-1 ring-zinc-200/50 shadow-sm'">
                <p v-if="message.role === 'user'" class="whitespace-pre-wrap break-words">{{ message.content }}</p>
                <div v-else-if="message.content" class="chat-markdown break-words" v-html="renderMarkdown(message.content)" />
                <div v-else-if="message.streaming" class="flex h-6 items-center gap-1.5" aria-label="AI 正在思考">
                  <span v-for="i in 3" :key="i" class="typing-dot h-1.5 w-1.5 rounded-full bg-blue-400" :style="{ animationDelay: `${(i - 1) * 160}ms` }" />
                </div>

                <div v-if="message.role === 'assistant' && !message.streaming && ['pending', 'applying'].includes(actionStatus(message))" class="mt-4 flex flex-wrap items-center gap-2 border-t border-zinc-100 pt-4">
                  <span class="mr-auto min-w-[180px] text-[13px] font-medium text-zinc-600">是否确认将这些修改写入简历？</span>
                  <button type="button" class="h-8 rounded-full px-3 text-[13px] font-medium text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-900 disabled:opacity-50" :disabled="decisionLoadingId === message.id" @click="emit('reject', message)">取消</button>
                  <Button type="button" size="sm" class="h-8 rounded-full bg-zinc-900 px-4 text-[13px] font-medium text-white hover:bg-zinc-800" :disabled="decisionLoadingId === message.id" @click="emit('confirm', message)">
                    <LoaderCircle v-if="decisionLoadingId === message.id" class="mr-1.5 h-3.5 w-3.5 animate-spin" />
                    确认修改
                  </Button>
                </div>
                <div v-else-if="message.role === 'assistant' && actionStatus(message) === 'applied'" class="mt-4 flex items-center gap-2 border-t border-zinc-100 pt-3 text-[13px] font-medium text-emerald-600">
                  <CheckCircle2 class="h-4 w-4" /> 修改已生效
                </div>
                <div v-else-if="message.role === 'assistant' && actionStatus(message) === 'rejected'" class="mt-4 flex items-center gap-2 border-t border-zinc-100 pt-3 text-[13px] font-medium text-zinc-400">
                  <X class="h-4 w-4" /> 修改已取消
                </div>
              </div>
            </div>
          </article>
        </TransitionGroup>

        <div v-if="error" class="mt-7 rounded-[20px] bg-red-50 p-4 text-[14px] text-red-600 ring-1 ring-red-100">{{ error }}</div>
      </div>

      <form class="composer relative mx-4 mb-4 mt-2 shrink-0 rounded-[24px] bg-zinc-50/80 p-2.5 ring-1 ring-zinc-200/50 transition-all focus-within:bg-white focus-within:ring-blue-200 focus-within:shadow-[0_8px_40px_rgba(16,185,129,0.08)]" @submit.prevent="submit">
        <div class="relative flex items-end gap-2">
          <textarea ref="inputRef" v-model="input" placeholder="输入你想调整的内容..." rows="1" class="min-h-[44px] max-h-[160px] flex-1 resize-none bg-transparent px-3 py-2.5 text-[15px] leading-relaxed text-zinc-800 placeholder:text-zinc-400 border-0 shadow-none focus-visible:ring-0 outline-none" style="scrollbar-width: none;" @input="adjustHeight" @compositionstart="composing = true" @compositionend="composing = false" @keydown.enter.exact.prevent="submit($event)"></textarea>
          
          <div class="flex items-center gap-1.5 shrink-0 pb-0.5">
            <button v-if="messages.length > 0 && !loading" type="button" class="flex h-10 w-10 items-center justify-center rounded-[18px] text-zinc-400 transition-all hover:bg-red-50 hover:text-red-500 active:scale-95" @click="$emit('clear')" title="清空对话">
              <Trash2 class="h-4.5 w-4.5" stroke-width="1.5" />
            </button>
            <Button class="h-10 w-10 shrink-0 rounded-[18px] bg-zinc-900 p-0 text-white shadow-md transition-all active:scale-95 disabled:opacity-50 disabled:active:scale-100 hover:bg-blue-600" :disabled="loading || !input.trim()">
              <SendHorizontal class="h-4.5 w-4.5" stroke-width="1.5" />
            </Button>
          </div>
        </div>
      </form>
    </section>
  </div>
</template>

<style scoped>
.chat-markdown :deep(p) { margin: 0 0 0.6rem; }
.chat-markdown :deep(p:last-child),
.chat-markdown :deep(ul:last-child),
.chat-markdown :deep(ol:last-child) { margin-bottom: 0; }
.chat-markdown :deep(h1),
.chat-markdown :deep(h2),
.chat-markdown :deep(h3) {
  margin: 1rem 0 0.4rem;
  color: #18181b;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: -0.02em;
}
.chat-markdown :deep(h1:first-child),
.chat-markdown :deep(h2:first-child),
.chat-markdown :deep(h3:first-child) { margin-top: 0; }
.chat-markdown :deep(h1) { font-size: 1.1rem; }
.chat-markdown :deep(h2),
.chat-markdown :deep(h3) { font-size: 1rem; }
.chat-markdown :deep(ul),
.chat-markdown :deep(ol) { margin: 0.4rem 0 0.8rem; padding-left: 1.25rem; }
.chat-markdown :deep(ul) { list-style: disc; }
.chat-markdown :deep(ol) { list-style: decimal; }
.chat-markdown :deep(li) { margin: 0.25rem 0; }
.chat-markdown :deep(strong) { color: #18181b; font-weight: 600; }
.chat-markdown :deep(code) {
  border-radius: 0.4rem;
  background: #f4f4f5;
  padding: 0.15rem 0.4rem;
  color: #27272a;
  font-size: 0.85em;
}
.chat-markdown :deep(pre) {
  margin: 0.75rem 0;
  overflow-x: auto;
  border-radius: 0.75rem;
  background: #18181b;
  padding: 1rem;
  color: #fafafa;
}
.chat-markdown :deep(pre code) { background: transparent; padding: 0; color: inherit; }
.chat-markdown :deep(a) { color: #3b82f6; text-decoration: none; font-weight: 500; transition: color 0.2s; }
.chat-markdown :deep(a:hover) { color: #059669; }

.typing-dot { animation: typing-bounce 1.4s ease-in-out infinite; }
.assistant-message-shell {
  width: min(720px, calc(100% - 54px));
  min-width: 0;
}

.assistant-orb::before {
  position: absolute;
  inset: -12px;
  content: "";
  border-radius: 40px;
  background: radial-gradient(circle, rgba(16,185,129,0.06) 0%, transparent 70%);
  animation: orb-breathe 4s ease-in-out infinite alternate;
}

.message-list-enter-active {
  transition: all 0.5s cubic-bezier(0.25, 0.1, 0.25, 1);
}
.message-list-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.98);
}

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}
@keyframes orb-breathe {
  from { transform: scale(0.9); opacity: 0.8; }
  to { transform: scale(1.1); opacity: 1; }
}
@media (prefers-reduced-motion: reduce) { 
  .analysis-step, .analysis-dot, .chat-markdown > *, .assistant-orb::before, .message-row { 
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
