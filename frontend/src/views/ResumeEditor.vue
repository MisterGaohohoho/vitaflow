<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, onUnmounted, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useDebounceFn } from "@vueuse/core"
import { ArrowLeft, Bot, CheckCircle2, Download, FileText, LoaderCircle, Save, Settings, Sparkles, Trash2, X, Target, Edit3, Eye, ScanLine } from "lucide-vue-next"
import Button from "@/components/ui/button/Button.vue"
import Input from "@/components/ui/input/Input.vue"
import ModuleSidebar from "@/components/editor/ModuleSidebar.vue"
import ResumeFormPanel from "@/components/editor/ResumeFormPanel.vue"
import StyleConfigPanel from "@/components/editor/StyleConfigPanel.vue"
import A4Preview from "@/components/preview/A4Preview.vue"
import ResumeScorePanel from "@/components/ai/ResumeScorePanel.vue"
import JdOptimizeModal from "@/components/ai/JdOptimizeModal.vue"
import ResumeAiChatPanel from "@/components/ai/ResumeAiChatPanel.vue"
import { normalizeResumeData, useResumeStore } from "@/stores/resume"
import { useEditorStore } from "@/stores/editor"
import { exportPdfApi, exportWordApi } from "@/api/export"
import { clearResumeChatMessagesApi, decideResumeChatChangeApi, getResumeChatMessagesApi, optimizeByJdStreamApi, optimizeSectionStreamApi, scoreResumeStreamApi, sendResumeChatMessageStreamApi } from "@/api/ai"
import { previewHtmlApi } from "@/api/resume"

const route = useRoute()
const router = useRouter()
const resumeStore = useResumeStore()
const editor = useEditorStore()
const showStyle = ref(false)
type SidePanel = "none" | "style" | "chat" | "score" | "jd" | "outline" | "suggestions" | "global"
const sidePanel = ref<SidePanel>("chat")

let activeTransition: any = null

const switchTab = (tab: "chat" | "score" | "jd" | "outline" | "suggestions" | "global") => {
  if (sidePanel.value === tab) return
  if (!document.startViewTransition) {
    sidePanel.value = tab
    return
  }
  
  if (activeTransition) {
    try {
      activeTransition.skipTransition()
    } catch (e) {
      // Ignore if transition is already finished to prevent crashing
    }
  }

  try {
    const transition = document.startViewTransition(async () => {
      sidePanel.value = tab
      await nextTick()
    })
    activeTransition = transition

    transition.finished.finally(() => {
      if (activeTransition === transition) {
        activeTransition = null
      }
    }).catch(() => {})
  } catch (err) {
    // Fallback if startViewTransition fails
    sidePanel.value = tab
  }
}

const mainMode = ref<"edit" | "ai">("edit")
const mobileTab = ref<"edit" | "preview">("edit")
const formPanelExpanded = ref(true)

const score = ref<any>(null)
const scoreLoading = ref(false)
const scoreError = ref("")
const scoreStreamText = ref("")
const optimizeResult = ref<any>(null)
const optimizeLoading = ref(false)
const optimizeError = ref("")
const optimizeStreamText = ref("")
const optimizeSectionKey = ref("")
const jdText = ref("")
const jdResult = ref<any>(null)
const jdLoading = ref(false)
const jdError = ref("")
const jdStreamText = ref("")
const chatMessages = ref<any[]>([])
const chatLoading = ref(false)
const chatLoaded = ref(false)
const chatDecisionLoadingId = ref<number | string | null>(null)

const isMobile = ref(false)
const leftPanelWidth = ref(600)
const isWide = computed(() => !isMobile.value && leftPanelWidth.value >= 800)
let resizeHandler: () => void

onMounted(() => {
  isMobile.value = window.innerWidth < 768
  resizeHandler = () => { isMobile.value = window.innerWidth < 768 }
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
})

watch(sidePanel, (newVal) => {
  if (newVal === "chat" && !chatLoaded.value) {
    loadChatMessages()
  }
})

const isResizing = ref(false)

function startResize(e: MouseEvent) {
  isResizing.value = true
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  
  const startX = e.clientX
  const startWidth = leftPanelWidth.value
  
  function onMouseMove(e: MouseEvent) {
    if (!isResizing.value) return
    const delta = e.clientX - startX
    let newWidth = startWidth + delta
    if (newWidth < 400) newWidth = 400
    if (newWidth > 1200) newWidth = 1200
    leftPanelWidth.value = newWidth
  }
  
  function onMouseUp() {
    isResizing.value = false
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }
  
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

const showAiOptimizeModal = ref(false)
const chatError = ref("")
const previewRefreshing = ref(false)
const exportLoading = ref<"" | "pdf" | "word">("")
const applySuccess = ref(false)
let applyTimer: ReturnType<typeof setTimeout> | undefined
let saveChain: Promise<unknown> = Promise.resolve()
let previewRequestSeq = 0
const resumeId = computed(() => Number(route.params.id))
const activeOptimizeResult = computed(() => (optimizeSectionKey.value === editor.currentSection ? optimizeResult.value : null))
const activeOptimizeLoading = computed(() => optimizeSectionKey.value === editor.currentSection && optimizeLoading.value)
const activeOptimizeError = computed(() => (optimizeSectionKey.value === editor.currentSection ? optimizeError.value : ""))
const activeOptimizeStreamText = computed(() => (optimizeSectionKey.value === editor.currentSection ? optimizeStreamText.value : ""))
const activeOptimizePreview = computed(() => {
  if (!resumeStore.resumeData || !activeOptimizeResult.value) return null
  return normalizeOptimizedSection(editor.currentSection, activeOptimizeResult.value, resumeStore.resumeData)
})
const aiWorkbenchOpen = computed(() => ["chat", "score", "jd"].includes(sidePanel.value))
const aiWorkbenchTitle = computed(() => {
  if (sidePanel.value === "score") return "简历 简历诊断"
  if (sidePanel.value === "jd") return "JD 匹配作战室"
  return "AI 简历助手"
})
const aiWorkbenchDescription = computed(() => {
  if (sidePanel.value === "score") return "扫描表达质量、岗位竞争力与内容完整度"
  if (sidePanel.value === "jd") return "把岗位要求、当前差距和可采纳修改放在同一张桌面上"
  return "围绕当前简历讨论、改写，并在写入前审阅每一处变化"
})

const debouncedSave = useDebounceFn(() => {
  void save().catch(() => undefined)
}, 1500)

onMounted(async () => {
  try {
    await resumeStore.fetchResumeDetail(resumeId.value)
    if (sidePanel.value === "chat" && !chatLoaded.value) {
      loadChatMessages()
    }
    if (window.innerWidth < 768) {
      editor.setPreviewScale(Number(((window.innerWidth - 32) / 794).toFixed(2)))
    }
  } catch (error: any) {
    console.error("Failed to load resume:", error)
    window.alert("简历不存在或无权限访问")
    router.replace("/")
  }
})

onBeforeUnmount(() => {
  if (applyTimer) clearTimeout(applyTimer)
})



async function performSave(options: { refreshPreview?: boolean } = {}) {
  if (!resumeStore.currentResume) return
  const { refreshPreview = true } = options
  editor.setSaving(true)
  try {
    const config = resumeStore.currentResume.template_config
    resumeStore.currentResume.template_id = config.template_id
    await resumeStore.updateResume({
      title: resumeStore.currentResume.title,
      resume_data: resumeStore.currentResume.resume_data,
      template_id: resumeStore.currentResume.template_id,
      template_config: config,
    } as any)
    if (refreshPreview) await refreshPreviewLatest()
    editor.setSaved(true)
  } catch (error) {
    editor.saveError = true
    throw error
  } finally {
    editor.setSaving(false)
  }
}

function save(options: { refreshPreview?: boolean } = {}) {
  saveChain = saveChain.catch(() => undefined).then(() => performSave(options))
  return saveChain
}

async function refreshPreviewLatest() {
  if (!resumeStore.currentResume) return
  const requestSeq = ++previewRequestSeq
  previewRefreshing.value = true
  try {
    const html = await previewHtmlApi(resumeStore.currentResume.id)
    if (requestSeq === previewRequestSeq) {
      resumeStore.previewHtml = html
    }
  } finally {
    if (requestSeq === previewRequestSeq) previewRefreshing.value = false
  }
}

function markChanged() {
  editor.saved = false
  debouncedSave()
}

function addCustomSection() {
  const data = resumeStore.resumeData
  if (!data) return
  const id = `custom_${Date.now()}`
  data.custom_sections.push({ id, title: "自定义模块", items: [{ id: `item_${Date.now()}`, title: "", content: "" }] })
  data.layout.section_order.push(id)
  data.layout.section_titles[id] = "自定义模块"
  editor.setCurrentSection(id)
  markChanged()
}

function removeCustomSection(key: string) {
  const data = resumeStore.resumeData
  if (!data) return
  data.custom_sections = data.custom_sections.filter((item) => item.id !== key)
  data.layout.section_order = data.layout.section_order.filter((item) => item !== key)
  delete data.layout.section_titles[key]
  editor.setCurrentSection("basics")
  markChanged()
}

function selectSection(key: string) {
  editor.setCurrentSection(key)
}

function isObject(value: unknown): value is Record<string, any> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value))
}

function splitTags(value: unknown) {
  if (Array.isArray(value)) return value.map((item) => String(item).trim()).filter(Boolean)
  return String(value ?? "")
    .split(/[,，、;；\n\r]+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function normalizeLines(value: unknown) {
  if (Array.isArray(value)) return value.map((item) => String(item).trim()).filter(Boolean)
  return String(value ?? "")
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function asText(value: unknown): string {
  if (value === undefined || value === null) return ""
  if (Array.isArray(value)) return value.map((item: unknown) => asText(item)).filter(Boolean).join("\n")
  if (isObject(value)) return String(value.content || value.description || value.text || "")
  return String(value)
}

function itemIdentity(item: any) {
  return String(item?.id || item?.name || item?.company || item?.school || item?.title || "").trim()
}

function normalizeSectionItem(key: string, item: any, currentItem: any, index: number) {
  const next = { ...(isObject(currentItem) ? currentItem : {}), ...(isObject(item) ? item : { description: asText(item) }) }
  next.id = next.id || currentItem?.id || `${key}_${Date.now()}_${index}`
  if (key === "skills") {
    next.keywords = splitTags(next.keywords)
    next.description = asText(next.description)
  }
  if (["work", "projects"].includes(key)) {
    next.highlights = normalizeLines(next.highlights)
    next.description = asText(next.description)
  }
  if (key === "education" || key === "awards") next.description = asText(next.description)
  if (key === "projects") next.tech_stack = Array.isArray(next.tech_stack) ? next.tech_stack.join(" / ") : asText(next.tech_stack)
  return next
}

function currentSectionValue(key: string, data: any) {
  if (data?.[key] !== undefined) return data[key]
  return data?.custom_sections?.find((item: any) => item.id === key)
}

function unwrapOptimizedSection(key: string, result: any) {
  let value = result?.optimized_section ?? result
  for (let i = 0; i < 6; i += 1) {
    if (!isObject(value)) break
    if (value.optimized_section !== undefined) {
      value = value.optimized_section
      continue
    }
    if (value.section_content !== undefined) {
      value = value.section_content
      continue
    }
    if (value.resume_data?.[key] !== undefined) {
      value = value.resume_data[key]
      continue
    }
    if (value[key] !== undefined) {
      value = value[key]
      continue
    }
    if (key === "summary" && value.summary !== undefined) {
      value = value.summary
      continue
    }
    break
  }
  return value
}

function normalizeListSection(key: string, value: any, currentValue: any) {
  let items = Array.isArray(value) ? value : []
  if (!items.length && isObject(value) && Array.isArray(value.items)) items = value.items
  if (!items.length && isObject(value) && ["name", "school", "company", "title"].some((field) => value[field])) items = [value]
  const currentItems = Array.isArray(currentValue) ? currentValue : []
  const used = new Set<number>()
  const normalized = items.map((item: any, index: number) => {
    const identity = itemIdentity(item)
    let matchIndex = identity ? currentItems.findIndex((currentItem, currentIndex) => !used.has(currentIndex) && itemIdentity(currentItem) === identity) : -1
    if (matchIndex < 0 && index < currentItems.length && !used.has(index)) matchIndex = index
    if (matchIndex >= 0) used.add(matchIndex)
    return normalizeSectionItem(key, item, matchIndex >= 0 ? currentItems[matchIndex] : {}, index)
  })
  currentItems.forEach((item, index) => {
    if (!used.has(index)) normalized.push(normalizeSectionItem(key, item, item, normalized.length))
  })
  return normalized
}

function normalizeCustomSectionValue(value: any, currentValue: any) {
  const current = isObject(currentValue) ? currentValue : { id: editor.currentSection, title: "自定义模块", items: [] }
  let items: any[] = []
  if (Array.isArray(value)) items = value
  else if (isObject(value) && Array.isArray(value.items)) items = value.items
  else if (isObject(value) && (value.title || value.content || value.description)) items = [value]
  else if (asText(value)) items = [{ title: "", content: asText(value) }]
  return {
    ...current,
    title: (isObject(value) && (value.title || value.section_title)) || current.title || "自定义模块",
    items: items.map((item, index) => {
      const currentItem = Array.isArray(current.items) && isObject(current.items[index]) ? current.items[index] : {}
      return {
        id: item?.id || currentItem.id || `item_${Date.now()}_${index}`,
        title: asText(item?.title || item?.name || currentItem.title),
        content: asText(item?.content || item?.description || item?.text || currentItem.content),
      }
    }),
  }
}

function normalizeOptimizedSection(key: string, result: any, data: any) {
  const value = unwrapOptimizedSection(key, result)
  const currentValue = currentSectionValue(key, data)
  if (key === "summary") return { ...(isObject(currentValue) ? currentValue : {}), content: asText(isObject(value) && value.content !== undefined ? value.content : value) }
  if (["education", "skills", "work", "projects", "awards"].includes(key)) return normalizeListSection(key, value, currentValue)
  if (currentValue) return normalizeCustomSectionValue(value, currentValue)
  return null
}

async function exportPdf() {
  if (exportLoading.value) return
  exportLoading.value = "pdf"
  try {
    if (!editor.saved) await save({ refreshPreview: false })
    await exportPdfApi(resumeId.value, resumeStore.currentResume?.title || "简历")
  } catch (error: any) {
    window.alert(error?.message || "PDF 导出失败")
  } finally {
    exportLoading.value = ""
  }
}

async function exportWord() {
  if (exportLoading.value) return
  exportLoading.value = "word"
  try {
    if (!editor.saved) await save({ refreshPreview: false })
    await exportWordApi(resumeId.value, resumeStore.currentResume?.title || "简历")
  } catch (error: any) {
    window.alert(error?.message || "Word 导出失败")
  } finally {
    exportLoading.value = ""
  }
}

async function refreshScore() {
  if (!resumeStore.resumeData) return
  scoreLoading.value = true
  scoreError.value = ""
  scoreStreamText.value = ""
  try {
    score.value = await scoreResumeStreamApi(
      { resume_data: resumeStore.resumeData, target_position: resumeStore.resumeData.basics.title },
      { onDelta: (text) => (scoreStreamText.value += text) },
    )
  } catch (error: any) {
    scoreError.value = error.message || "AI 评分失败"
  } finally {
    scoreLoading.value = false
  }
}

function showApplySuccess() {
  applySuccess.value = true
  if (applyTimer) clearTimeout(applyTimer)
  applyTimer = setTimeout(() => (applySuccess.value = false), 1800)
}

async function openScorePanel() {
  if (sidePanel.value === "score") {
    sidePanel.value = "none"
    return
  }
  sidePanel.value = "score"
}

async function loadChatMessages() {
  chatError.value = ""
  try {
    chatMessages.value = (await getResumeChatMessagesApi(resumeId.value)) as unknown as any[]
    chatLoaded.value = true
  } catch (error: any) {
    chatError.value = error.message || "对话记录加载失败"
  }
}

async function openChatPanel() {
  if (sidePanel.value === "chat") {
    sidePanel.value = "none"
    return
  }
  sidePanel.value = "chat"
  if (!chatLoaded.value) await loadChatMessages()
}

async function sendChatMessage(content: string) {
  if (!resumeStore.currentResume || chatLoading.value) return
  chatLoading.value = true
  chatError.value = ""
  const stamp = Date.now()
  const pendingUser = { id: `user-${stamp}`, role: "user", content }
  const pendingAssistant = { id: `assistant-${stamp}`, role: "assistant", content: "", streaming: true, phase: "replying", phaseText: "正在组织回复" }
  chatMessages.value.push(pendingUser, pendingAssistant)
  const assistantIndex = chatMessages.value.length - 1
  try {
    if (!editor.saved) await save({ refreshPreview: false })
    const response = (await sendResumeChatMessageStreamApi(
      resumeId.value,
      { content },
      {
        onDelta: (text) => {
          const assistant = chatMessages.value[assistantIndex]
          if (assistant) assistant.content += text
        },
        onPhase: (phase, text) => {
          const assistant = chatMessages.value[assistantIndex]
          if (assistant) Object.assign(assistant, { phase, phaseText: text })
        },
      },
    )) as any
    const savedAssistant = response?.assistant_message
    const assistant = chatMessages.value[assistantIndex]
    if (assistant && savedAssistant) Object.assign(assistant, savedAssistant, { streaming: false })
    else if (assistant) assistant.streaming = false
    if (response?.resolved_message) {
      const resolved = chatMessages.value.find((item) => item.id === response.resolved_message.id)
      if (resolved) Object.assign(resolved, response.resolved_message)
    }
    if (response?.resume_data && resumeStore.currentResume) {
      resumeStore.updateResumeData(response.resume_data)
      editor.setSaved(true)
      await resumeStore.refreshPreviewHtml()
      showApplySuccess()
    }
    chatLoaded.value = true
  } catch (error: any) {
    const assistant = chatMessages.value[assistantIndex]
    if (assistant) assistant.streaming = false
    if (!assistant?.content) chatMessages.value = chatMessages.value.filter((item) => item.id !== pendingAssistant.id)
    chatError.value = error.message || "AI 对话失败"
  } finally {
    chatLoading.value = false
  }
}

async function clearChatMessages() {
  chatError.value = ""
  try {
    await clearResumeChatMessagesApi(resumeId.value)
    chatMessages.value = []
    chatLoaded.value = true
  } catch (error: any) {
    chatError.value = error.message || "清除对话记录失败"
  }
}

async function confirmClearChatMessages() {
  if (chatLoading.value || !chatMessages.value.length) return
  if (window.confirm("确定清除当前简历的 AI 对话记录吗？")) await clearChatMessages()
}

async function optimizeCurrentSection() {
  if (!resumeStore.resumeData) return
  const key = editor.currentSection
  optimizeSectionKey.value = key
  optimizeResult.value = null
  optimizeLoading.value = true
  optimizeError.value = ""
  optimizeStreamText.value = ""
  try {
    optimizeResult.value = await optimizeSectionStreamApi(
      {
        section_type: key,
        section_title: resumeStore.resumeData.layout.section_titles[key],
        section_content: currentSectionValue(key, resumeStore.resumeData),
        full_resume_data: resumeStore.resumeData,
        target_position: resumeStore.resumeData.basics.title,
      },
      { onDelta: (text) => (optimizeStreamText.value += text) },
    )
  } catch (error: any) {
    optimizeResult.value = null
    optimizeError.value = error.message || "模块优化失败"
  } finally {
    optimizeLoading.value = false
  }
}

function clearSectionOptimizeResult() {
  optimizeResult.value = null
  optimizeError.value = ""
  optimizeStreamText.value = ""
  if (!optimizeLoading.value) optimizeSectionKey.value = ""
}

async function optimizeJd(jd: string) {
  if (!resumeStore.resumeData) return
  jdLoading.value = true
  jdError.value = ""
  jdStreamText.value = ""
  sidePanel.value = "jd"
  try {
    jdResult.value = await optimizeByJdStreamApi(
      { resume_data: resumeStore.resumeData, job_description: jd },
      { onDelta: (text) => (jdStreamText.value += text) },
    )
  } catch (error: any) {
    jdError.value = error.message || "JD 优化失败"
  } finally {
    jdLoading.value = false
  }
}

function mergeOptimizedResumeData(currentData: any, optimizedData: any) {
  const rawData = optimizedData?.resume_data && typeof optimizedData.resume_data === "object" ? optimizedData.resume_data : optimizedData
  const mergedData = { ...(rawData || {}) }
  const currentLayout = currentData?.layout || {}
  const optimizedLayout = mergedData.layout || {}
  const currentTitles = currentLayout.section_titles && typeof currentLayout.section_titles === "object" ? currentLayout.section_titles : {}
  const optimizedTitles = optimizedLayout.section_titles && typeof optimizedLayout.section_titles === "object" ? optimizedLayout.section_titles : {}
  const sectionTitles = { ...currentTitles }
  for (const [key, title] of Object.entries(optimizedTitles)) {
    if (typeof title === "string" && title && title !== key) sectionTitles[key] = title
  }
  mergedData.layout = {
    ...optimizedLayout,
    section_order: Array.isArray(optimizedLayout.section_order) && optimizedLayout.section_order.length ? optimizedLayout.section_order : currentLayout.section_order,
    hidden_sections: Array.isArray(optimizedLayout.hidden_sections) ? optimizedLayout.hidden_sections : currentLayout.hidden_sections,
    section_titles: sectionTitles,
  }
  return normalizeResumeData(mergedData)
}

async function applyOptimizeResult(targetResult?: any) {
  if (!resumeStore.currentResume) return
  const result = targetResult || optimizeResult.value
  if (!result) return
  if (result.optimized_resume_data) {
    resumeStore.currentResume.resume_data = mergeOptimizedResumeData(resumeStore.currentResume.resume_data, result.optimized_resume_data)
  }
  if (result.optimized_section) {
    const key = editor.currentSection
    if ((resumeStore.currentResume.resume_data as any)[key] !== undefined) (resumeStore.currentResume.resume_data as any)[key] = result.optimized_section
    else {
      const custom = resumeStore.currentResume.resume_data.custom_sections.find((item) => item.id === key)
      if (custom) Object.assign(custom, result.optimized_section)
    }
    resumeStore.currentResume.resume_data = normalizeResumeData(resumeStore.currentResume.resume_data)
  }
  if (!resumeStore.currentResume.resume_data.layout.section_order.includes(editor.currentSection)) editor.setCurrentSection("basics")
  await save()
  if (aiWorkbenchOpen.value) sidePanel.value = "none"
  showApplySuccess()
}

async function applySectionOptimizeResult() {
  if (!resumeStore.currentResume || !resumeStore.resumeData) return
  const key = optimizeSectionKey.value || editor.currentSection
  const nextSection = normalizeOptimizedSection(key, optimizeResult.value, resumeStore.resumeData)
  if (!nextSection) return
  if ((resumeStore.currentResume.resume_data as any)[key] !== undefined) {
    ;(resumeStore.currentResume.resume_data as any)[key] = nextSection
  } else {
    const custom = resumeStore.currentResume.resume_data.custom_sections.find((item) => item.id === key)
    if (custom && isObject(nextSection)) Object.assign(custom, nextSection)
  }
  resumeStore.currentResume.resume_data = normalizeResumeData(resumeStore.currentResume.resume_data)
  editor.setCurrentSection(key)
  clearSectionOptimizeResult()
  await save()
}

async function resolveChatDecision(message: any, action: "apply" | "reject") {
  if (!resumeStore.currentResume || !message?.id || chatDecisionLoadingId.value !== null) return
  const previousStatus = message.action_status || "pending"
  chatDecisionLoadingId.value = message.id
  message.action_status = "applying"
  chatError.value = ""
  try {
    const response = (await decideResumeChatChangeApi(resumeId.value, Number(message.id), action)) as any
    if (response?.assistant_message) Object.assign(message, response.assistant_message)
    if (action === "apply" && response?.resume_data) {
      resumeStore.updateResumeData(response.resume_data)
      editor.setSaved(true)
      if (!resumeStore.resumeData?.layout.section_order.includes(editor.currentSection)) editor.setCurrentSection("basics")
      await resumeStore.refreshPreviewHtml()
      showApplySuccess()
    }
  } catch (error: any) {
    message.action_status = previousStatus
    chatError.value = error.message || (action === "apply" ? "修改写入失败" : "取消修改失败")
  } finally {
    chatDecisionLoadingId.value = null
  }
}

function openStylePanel() {
  showStyle.value = true
  sidePanel.value = "style"
}

function openJdPanel() {
  if (sidePanel.value === "jd") {
    sidePanel.value = "none"
    return
  }
  sidePanel.value = "jd"
}

function closeSidePanel() {
  sidePanel.value = "none"
}

const sidePanelTitle = computed(() => {
  if (sidePanel.value === "style") return "样式设置"
  if (sidePanel.value === "jd") return "岗位描述(JD)匹配优化"
  if (sidePanel.value === "chat") return "AI 简历助手"
  return "AI 简历诊断"
})
</script>

<template>
  <div v-if="resumeStore.currentResume && resumeStore.resumeData && resumeStore.templateConfig" class="fixed inset-0 flex flex-col overflow-hidden bg-zinc-100/60">
    <!-- Premium Header -->
    <header class="flex h-16 shrink-0 items-center gap-4 border-b border-zinc-200/60 bg-white/80 backdrop-blur-md px-6 relative z-40">
      <Button size="icon" variant="ghost" class="text-zinc-500 hover:text-zinc-900 rounded-lg hover:bg-zinc-100" @click="router.push('/resumes')">
        <ArrowLeft class="h-5 w-5" />
      </Button>
      
      <div class="h-8 w-[1px] bg-zinc-200 hidden sm:block"></div>
      
      <div class="flex items-center gap-3">
        <div class="inline-grid items-center max-w-[150px] sm:max-w-[400px]">
          <span class="col-start-1 row-start-1 invisible whitespace-pre pl-2 pr-3 py-1 border border-transparent text-[16px] sm:text-[18px] font-semibold tracking-tight overflow-hidden">{{ resumeStore.currentResume.title || '无标题简历' }}</span>
          <input 
            v-model="resumeStore.currentResume.title" 
            placeholder="无标题简历"
            size="1"
            class="col-start-1 row-start-1 w-full min-w-0 border border-transparent bg-transparent px-2 py-1 text-[16px] sm:text-[18px] font-semibold tracking-tight text-zinc-900 shadow-none hover:border-zinc-200 hover:bg-zinc-50 focus:border-blue-500 focus:bg-white focus:ring-1 focus:ring-blue-500 transition-all outline-none rounded-md truncate"
            @input="markChanged" 
          />
        </div>
        <div class="flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium transition-colors whitespace-nowrap" :class="editor.saving ? 'bg-amber-50 text-amber-600' : editor.saveError ? 'bg-red-50 text-red-600' : 'bg-zinc-100 text-zinc-500'">
          <Save v-if="editor.saving" class="h-3.5 w-3.5 animate-pulse shrink-0" /> 
          <CheckCircle2 v-else class="h-3.5 w-3.5 shrink-0" :class="{ 'text-blue-500': !editor.saveError }" />
          <span class="hidden sm:inline">{{ editor.saving ? '保存中' : editor.saveError ? '保存失败' : '已自动保存' }}</span>
        </div>
      </div>
      
      <div class="ml-auto flex items-center gap-2.5">

        
        <div class="h-6 w-[1px] bg-zinc-200 hidden md:block mx-0.5 md:mx-1"></div>

        <Button size="icon" variant="outline" class="shrink-0 h-8 w-8 md:h-10 md:w-10 border-zinc-200 text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 rounded-lg shadow-sm" @click="openStylePanel" title="主题设置">
          <Settings class="h-4 w-4 shrink-0" />
        </Button>
        <Button size="sm" variant="outline" class="!hidden md:!inline-flex shrink-0 h-10 px-4 border-zinc-200 text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 rounded-lg shadow-sm font-medium" :disabled="!!exportLoading" @click="exportWord">
          <FileText class="h-4 w-4 shrink-0 mr-1.5" /> Word
        </Button>
        <Button size="sm" class="shrink-0 h-8 px-3 md:h-10 md:px-5 bg-zinc-900 text-white hover:bg-zinc-800 rounded-lg shadow-md active:scale-95 transition-all font-medium text-xs md:text-sm whitespace-nowrap" :disabled="!!exportLoading" @click="exportPdf">
          <Download class="h-3 w-3 md:h-4 md:w-4 shrink-0" /> <span class="hidden md:inline ml-1.5">导出</span> PDF
        </Button>
      </div>
    </header>

    <!-- Main Workspace -->
    <div class="relative flex min-h-0 flex-1 overflow-hidden pb-14 md:pb-0">
      <div class="workspace-surface flex min-w-0 flex-1">
        <!-- Left Unified Sidebar -->
        <div :class="['flex-col h-full shrink-0 bg-white overflow-hidden transition-none relative z-20 shadow-[4px_0_24px_rgba(0,0,0,0.02)]', mobileTab === 'edit' ? 'flex w-full' : 'hidden md:flex']" :style="{ width: isMobile ? '100%' : leftPanelWidth + 'px' }">
          
          <!-- Mode Switcher -->
          <div class="shrink-0 border-b border-zinc-200/50 p-2.5 bg-zinc-50/80 flex justify-center w-full z-10 relative">
             <div class="flex w-full bg-zinc-200/50 p-1 rounded-xl shadow-inner border border-zinc-200/80">
                <button 
                  class="relative flex-1 flex items-center justify-center gap-2 py-1.5 rounded-lg text-[14px] font-medium transition-all duration-300"
                  :class="mainMode === 'edit' ? 'text-zinc-900 shadow-sm' : 'text-zinc-500 hover:text-zinc-700'"
                  @click="mainMode = 'edit'"
                >
                  <div v-if="mainMode === 'edit'" class="absolute inset-0 bg-white rounded-lg shadow-[0_2px_8px_rgba(0,0,0,0.04)]"></div>
                  <Edit3 class="relative z-10 w-4 h-4" />
                  <span class="relative z-10">内容编辑</span>
                </button>
                <button 
                  class="relative flex-1 flex items-center justify-center gap-2 py-1.5 rounded-lg text-[14px] font-medium transition-all duration-300"
                  :class="mainMode === 'ai' ? 'text-zinc-900 shadow-sm' : 'text-zinc-500 hover:text-zinc-700'"
                  @click="mainMode = 'ai'; if(sidePanel === 'none') sidePanel = 'chat'"
                >
                  <div v-if="mainMode === 'ai'" class="absolute inset-0 bg-white rounded-lg shadow-[0_2px_8px_rgba(0,0,0,0.04)] border border-blue-100/50"></div>
                  <Sparkles class="relative z-10 w-4 h-4" :class="mainMode === 'ai' ? 'text-blue-500' : ''" />
                  <span class="relative z-10 font-bold tracking-tight">Flow Agent (Beta)</span>
                </button>
             </div>
          </div>

          <!-- Traditional Edit Mode -->
          <div v-show="mainMode === 'edit'" class="flex flex-col flex-1 min-h-0 overflow-hidden relative bg-zinc-50/30">
            <ModuleSidebar 
              class="w-full shrink-0 relative z-20 shadow-[0_4px_12px_rgba(0,0,0,0.02)]" 
              :data="resumeStore.resumeData" 
              :current="editor.currentSection" 
              @select="selectSection" 
              @change="markChanged" 
              @add-custom="addCustomSection" 
              @remove-custom="removeCustomSection" 
              @optimize="optimizeCurrentSection" 
            />

            <ResumeFormPanel
              class="relative z-10 flex-1 min-h-0 min-w-0"
              :data="resumeStore.resumeData"
              :config="resumeStore.templateConfig"
              :current="editor.currentSection"
              :show-style="false"
              :optimize-result="activeOptimizeResult"
              :optimize-preview="activeOptimizePreview"
              :optimize-loading="activeOptimizeLoading"
              :optimize-error="activeOptimizeError"
              :optimize-stream-text="activeOptimizeStreamText"
              :is-wide="isWide"
              @change="markChanged"
              @optimize="optimizeCurrentSection"
              @apply-optimize="applySectionOptimizeResult"
              @clear-optimize="clearSectionOptimizeResult"
            />
          </div>

          <!-- AI Workbench Mode -->
          <div v-show="mainMode === 'ai'" class="flex flex-col flex-1 min-h-0 overflow-hidden bg-white">
            <header class="relative shrink-0 border-b border-zinc-200/60 bg-white flex flex-col z-10">
              <nav class="flex items-center overflow-x-auto overflow-y-hidden px-4 py-3 gap-2.5 w-full scrollbar-none [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
                <button class="flex-1 flex items-center justify-center gap-1.5 h-9 rounded-full px-4 text-[14px] font-medium transition-all duration-300 border select-none" :class="sidePanel === 'chat' ? 'bg-zinc-900 text-white border-zinc-900 shadow-md' : 'bg-white text-zinc-600 border-zinc-200/80 hover:border-zinc-300 hover:bg-zinc-50 shadow-sm'" @click="switchTab('chat')">
                  <Bot class="h-4 w-4 shrink-0" /> <span class="whitespace-nowrap">AI 助手</span>
                </button>
                <button class="flex-1 flex items-center justify-center gap-1.5 h-9 rounded-full px-4 text-[14px] font-medium transition-all duration-300 border select-none" :class="sidePanel === 'score' ? 'bg-zinc-900 text-white border-zinc-900 shadow-md' : 'bg-white text-zinc-600 border-zinc-200/80 hover:border-zinc-300 hover:bg-zinc-50 shadow-sm'" @click="switchTab('score')">
                  <ScanLine class="h-4 w-4 shrink-0" /> <span class="whitespace-nowrap"> 简历诊断</span>
                </button>
                <button class="flex-1 flex items-center justify-center gap-1.5 h-9 rounded-full px-4 text-[14px] font-medium transition-all duration-300 border select-none" :class="sidePanel === 'jd' ? 'bg-zinc-900 text-white border-zinc-900 shadow-md' : 'bg-white text-zinc-600 border-zinc-200/80 hover:border-zinc-300 hover:bg-zinc-50 shadow-sm'" @click="switchTab('jd')">
                  <Target class="h-4 w-4 shrink-0" /> <span class="whitespace-nowrap">JD 优化</span>
                </button>
              </nav>
            </header>

            <div class="relative min-h-0 flex-1 overflow-hidden p-0 md:p-0">
                <ResumeAiChatPanel v-if="sidePanel === 'chat'" key="chat" :messages="chatMessages" :loading="chatLoading" :error="chatError" :decision-loading-id="chatDecisionLoadingId" @send="sendChatMessage" @clear="clearChatMessages" @confirm="resolveChatDecision($event, 'apply')" @reject="resolveChatDecision($event, 'reject')" />
              <ResumeScorePanel v-else-if="sidePanel === 'score'" key="score" :score="score" :loading="scoreLoading" :error="scoreError" :stream-text="scoreStreamText" :is-wide="isWide" @refresh="refreshScore" />
              <JdOptimizeModal v-else key="jd" v-model="jdText" :result="jdResult" :loading="jdLoading" :error="jdError" :stream-text="jdStreamText" :current-data="resumeStore.resumeData" :is-wide="isWide" @optimize="optimizeJd" @apply="applyOptimizeResult(jdResult)" @clear="jdResult = null; jdError = ''; jdStreamText = ''" />
            </div>
          </div>
        </div>

        <!-- Resizer Handle -->
        <div
          v-if="!isMobile"
          class="relative z-30 w-4 -ml-2 h-full cursor-col-resize flex items-center justify-center group"
          @mousedown="startResize"
        >
           <!-- Subtle hover line -->
           <div class="absolute inset-y-0 left-1/2 -ml-[0.5px] w-[1px] bg-blue-500 opacity-0 group-hover:opacity-100 group-active:opacity-100 transition-opacity duration-300 delay-75"></div>
           
           <!-- Drag pill -->
           <div class="relative z-10 flex h-8 w-1 rounded-full bg-zinc-300 shadow-sm ring-1 ring-black/5 group-hover:bg-blue-500 group-active:bg-blue-600 transition-all duration-300 group-hover:scale-125"></div>
        </div>

        <!-- Preview Canvas -->
        <div :class="['relative flex-1 bg-zinc-100/50 flex-col overflow-hidden', mobileTab === 'preview' ? 'flex' : 'hidden md:flex']">
          <A4Preview class="flex-1" :html="resumeStore.previewHtml" :scale="editor.previewScale" @zoom-in="editor.setPreviewScale(Math.min(1, editor.previewScale + 0.05))" @zoom-out="editor.setPreviewScale(Math.max(0.45, editor.previewScale - 0.05))" />
          <div v-if="previewRefreshing" class="pointer-events-none absolute right-5 top-16 rounded-full border border-zinc-200 bg-white/90 px-3 py-1 text-xs font-medium text-zinc-500 shadow-sm backdrop-blur">
            预览更新中
          </div>
        </div>
      </div>

      <!-- Style remains a focused utility drawer. -->
      <Transition name="slide-panel">
        <aside v-if="sidePanel === 'style'" class="absolute bottom-0 right-0 top-0 z-[60] flex w-full flex-col border-l border-zinc-200/80 bg-white/95 backdrop-blur-2xl shadow-2xl md:w-[420px]">
          <div class="shrink-0 border-b border-zinc-100/80 p-5 bg-white/50">
            <div class="flex items-center justify-between gap-3">
              <h2 class="text-lg font-semibold text-zinc-900 tracking-tight">{{ sidePanelTitle }}</h2>
              <Button size="icon" variant="ghost" class="text-zinc-400 hover:bg-zinc-100 hover:text-zinc-900 rounded-full h-8 w-8 transition-colors" @click="closeSidePanel">
                <X class="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div class="min-h-0 flex-1 overflow-y-auto p-6 thin-scrollbar bg-white/40">
            <StyleConfigPanel :config="resumeStore.templateConfig" @change="markChanged" />
          </div>
        </aside>
      </Transition>

      <Transition name="apply-success">
        <div v-if="applySuccess" class="pointer-events-none absolute inset-0 z-[64] flex items-center justify-center overflow-hidden">
          <div class="apply-success-ring absolute h-72 w-72 rounded-full border border-blue-400/40"></div>
          <div class="apply-success-ring apply-success-ring--delay absolute h-72 w-72 rounded-full border border-blue-400/30"></div>
          <div class="relative flex items-center gap-3 rounded-2xl border border-blue-100 bg-white/95 px-5 py-4 shadow-2xl backdrop-blur-xl">
            <span class="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white"><CheckCircle2 class="h-5 w-5" /></span>
            <div><div class="text-sm font-semibold text-zinc-950">修改已写入简历</div><div class="mt-0.5 text-xs text-zinc-500">预览已同步更新</div></div>
          </div>
        </div>
      </Transition>
    </div>

    <Transition name="export-fade">
      <div v-if="exportLoading" class="fixed inset-0 z-[80] flex items-center justify-center bg-zinc-950/45 px-6 backdrop-blur-sm">
        <div class="w-full max-w-[320px] rounded-2xl border border-white/20 bg-white px-6 py-7 text-center shadow-2xl">
          <LoaderCircle class="mx-auto h-10 w-10 animate-spin text-zinc-900" />
          <h3 class="mt-4 text-base font-semibold text-zinc-900">
            {{ exportLoading === 'pdf' ? '正在导出 PDF' : '正在导出 Word' }}
          </h3>
          <p class="mt-2 text-sm leading-6 text-zinc-500">
            正在生成文件，请勿关闭页面。
          </p>
        </div>
      </div>
    </Transition>

    <!-- Mobile Bottom Nav -->
    <div class="md:hidden fixed bottom-0 left-0 right-0 h-14 bg-white border-t border-zinc-200 flex items-center z-50">
      <button class="flex flex-col items-center justify-center flex-1 h-full gap-1 transition-colors" :class="mobileTab === 'edit' ? 'text-zinc-900' : 'text-zinc-400 hover:text-zinc-600'" @click="mobileTab = 'edit'">
        <Edit3 class="w-5 h-5" />
        <span class="text-[10px] font-medium leading-none">编辑</span>
      </button>
      <button class="flex flex-col items-center justify-center flex-1 h-full gap-1 transition-colors" :class="mobileTab === 'preview' ? 'text-zinc-900' : 'text-zinc-400 hover:text-zinc-600'" @click="mobileTab = 'preview'">
        <Eye class="w-5 h-5" />
        <span class="text-[10px] font-medium leading-none">预览</span>
      </button>
    </div>
  </div>
  <div v-else class="flex h-screen flex-col items-center justify-center bg-zinc-50">
    <div class="h-8 w-8 animate-spin rounded-full border-4 border-zinc-200 border-t-zinc-900 mb-4"></div>
    <span class="text-sm font-medium text-zinc-500 tracking-wide">加载简历中...</span>
  </div>
</template>

<style scoped>
.slide-form-enter-active,
.slide-form-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-form-enter-from,
.slide-form-leave-to {
  opacity: 0;
  transform: translateX(-20px);
  margin-left: -560px; /* Collapse space smoothly */
}

/* Slide Right Panel */
.slide-panel-enter-active,
.slide-panel-leave-active {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease;
}
.slide-panel-enter-from,
.slide-panel-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.workspace-surface {
  transform-origin: 50% 45%;
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), filter 0.45s ease, opacity 0.45s ease;
}

.ai-launcher::before {
  position: absolute;
  inset: 0;
  content: "";
  background: linear-gradient(110deg, transparent 20%, rgba(255,255,255,0.75) 46%, transparent 68%);
  transform: translateX(-140%);
  transition: transform 0.7s ease;
}
.ai-launcher:hover::before { transform: translateX(140%); }
.ai-launcher-orb::after {
  position: absolute;
  inset: -3px;
  content: "";
  border: 1px solid currentColor;
  border-radius: 999px;
  opacity: 0.16;
  animation: ai-orbit 3s ease-in-out infinite;
}

.ai-workbench-layer {
  background:
    radial-gradient(circle at 50% 8%, rgba(99,102,241,0.10), transparent 38%),
    rgba(24,24,27,0.38);
  backdrop-filter: blur(12px);
}
.ai-workbench::after {
  position: absolute;
  inset: 0;
  z-index: 20;
  border-radius: inherit;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.9);
  content: "";
  pointer-events: none;
}
.ai-workbench-aurora {
  background:
    radial-gradient(circle at 20% 0%, rgba(124,58,237,0.12), transparent 34%),
    radial-gradient(circle at 60% -20%, rgba(14,165,233,0.11), transparent 38%),
    radial-gradient(circle at 90% 10%, rgba(16,185,129,0.10), transparent 32%);
}
.ai-core::before,
.ai-core::after {
  position: absolute;
  inset: -6px;
  content: "";
  border: 1px solid rgba(99,102,241,0.28);
  border-radius: 18px;
  animation: ai-core-pulse 2.8s ease-out infinite;
}
.ai-core::after { animation-delay: 1.4s; }

.ai-mode-tab {
  display: flex;
  height: 38px;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border-radius: 12px;
  color: #71717a;
  font-size: 13px;
  font-weight: 600;
  transition: color 0.2s ease, background 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
}
.ai-mode-tab:hover { color: #18181b; transform: translateY(-1px); }
.ai-mode-tab--active {
  color: #18181b;
  background: rgba(255,255,255,0.96);
  box-shadow: 0 5px 18px rgba(24,24,27,0.08), inset 0 0 0 1px rgba(228,228,231,0.9);
}
.ai-mode-tab--chat svg { color: #7c3aed; }
.ai-mode-tab--score svg { color: #d97706; }
.ai-mode-tab--jd svg { color: #059669; }

.ai-workbench-enter-active,
.ai-workbench-leave-active { transition: opacity 0.4s ease; }
.ai-workbench-enter-active .ai-workbench,
.ai-workbench-leave-active .ai-workbench { transition: transform 0.52s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.35s ease, clip-path 0.52s cubic-bezier(0.16, 1, 0.3, 1); }
.ai-workbench-enter-from,
.ai-workbench-leave-to { opacity: 0; }
.ai-workbench-enter-from .ai-workbench,
.ai-workbench-leave-to .ai-workbench {
  opacity: 0;
  transform: translate(32%, -46%) scale(0.1);
  clip-path: inset(0 0 86% 82% round 999px);
}

.ai-content-enter-active,
.ai-content-leave-active { transition: opacity 0.2s ease, transform 0.28s cubic-bezier(0.16, 1, 0.3, 1); }
.ai-content-enter-from { opacity: 0; transform: translateY(12px) scale(0.992); }
.ai-content-leave-to { opacity: 0; transform: translateY(-6px) scale(0.992); }

.apply-success-enter-active,
.apply-success-leave-active { transition: opacity 0.28s ease; }
.apply-success-enter-active > div:last-child { animation: success-pop 0.55s cubic-bezier(0.16, 1, 0.3, 1) both; }
.apply-success-enter-from,
.apply-success-leave-to { opacity: 0; }
.apply-success-ring { animation: success-ring 1.45s ease-out both; }
.apply-success-ring--delay { animation-delay: 0.18s; }

.export-fade-enter-active,
.export-fade-leave-active {
  transition: opacity 0.18s ease;
}
.export-fade-enter-from,
.export-fade-leave-to {
  opacity: 0;
}

@keyframes ai-orbit {
  0%, 100% { transform: scale(0.92); opacity: 0.1; }
  50% { transform: scale(1.18); opacity: 0.3; }
}
@keyframes ai-core-pulse {
  0% { transform: scale(0.78); opacity: 0; }
  25% { opacity: 0.7; }
  100% { transform: scale(1.4); opacity: 0; }
}
@keyframes success-pop {
  from { opacity: 0; transform: translateY(18px) scale(0.88); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes success-ring {
  from { opacity: 0.75; transform: scale(0.2); }
  to { opacity: 0; transform: scale(2.2); }
}

@media (max-width: 767px) {
  .workspace-surface--ai { transform: scale(0.99); }
  .ai-workbench-enter-from .ai-workbench,
  .ai-workbench-leave-to .ai-workbench {
    transform: translateY(90%) scale(0.96);
    clip-path: inset(88% 3% 0 3% round 28px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .workspace-surface,
  .ai-launcher,
  .ai-workbench-enter-active .ai-workbench,
  .ai-workbench-leave-active .ai-workbench { transition-duration: 0.01ms !important; }
  .ai-launcher-orb::after,
  .ai-core::before,
  .ai-core::after,
  .apply-success-ring { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; }
}
</style>

<style>
/* Ultimate Premium Spatial Float & Settle Morph for AI Hero Icon */

/* Prevent the transition overlay from blocking user clicks! */
::view-transition {
  pointer-events: none;
}

::view-transition-group(ai-hero-icon) {
  animation-duration: 0.85s;
  animation-timing-function: cubic-bezier(0.22, 1, 0.36, 1);
}

::view-transition-old(ai-hero-icon) {
  animation: 0.85s cubic-bezier(0.22, 1, 0.36, 1) both ai-hero-fade-out;
  transform-origin: center;
}

::view-transition-new(ai-hero-icon) {
  animation: 0.85s cubic-bezier(0.22, 1, 0.36, 1) both ai-hero-fade-in;
  transform-origin: center;
}

@keyframes ai-hero-fade-out {
  0% { 
    opacity: 1; 
    transform: scale(1) translateY(0); 
    filter: blur(0); 
  }
  25% { 
    opacity: 0; 
    transform: scale(0.6) translateY(12px); 
    filter: blur(10px); 
  }
  100% { 
    opacity: 0; 
  }
}

@keyframes ai-hero-fade-in {
  0% { 
    opacity: 0; 
    transform: scale(1.8) translateY(-25px); 
    filter: blur(16px); 
  }
  35% { 
    opacity: 1; 
    transform: scale(1.1) translateY(-6px); 
    filter: blur(0); 
  }
  100% { 
    opacity: 1; 
    transform: scale(1) translateY(0); 
    filter: blur(0); 
  }
}
</style>
