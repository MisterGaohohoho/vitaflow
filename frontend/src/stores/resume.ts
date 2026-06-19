import { defineStore } from "pinia"
import { createResumeApi, deleteResumeApi, duplicateResumeApi, getResumeApi, listResumesApi, previewHtmlApi, previewPdfApi, updateResumeApi } from "@/api/resume"
import type { ResumeData, ResumeItem, TemplateConfig } from "@/types/resume"

const builtInSections = ["basics", "summary", "education", "skills", "work", "projects", "awards"]
const builtInTitles: Record<string, string> = {
  basics: "基本信息",
  summary: "个人简介",
  education: "教育经历",
  skills: "专业技能",
  work: "工作经历",
  projects: "项目经历",
  awards: "荣誉奖项",
}

export function normalizeResumeData(input: any): ResumeData {
  const data = input && typeof input === "object" ? input : {}
  if (!data.basics || typeof data.basics !== "object" || Array.isArray(data.basics)) data.basics = {}
  if (!Array.isArray(data.basics.custom_fields)) data.basics.custom_fields = []
  if (!data.basics.field_config || typeof data.basics.field_config !== "object" || Array.isArray(data.basics.field_config)) data.basics.field_config = {
    phone: { label: "电话", icon: "Phone", row: 1, order: 1 },
    email: { label: "邮箱", icon: "Mail", row: 1, order: 2 },
    status: { label: "当前状态", icon: "Info", row: 1, order: 3 },
    location: { label: "地点", icon: "MapPin", row: 1, order: 4 },
    highest_degree: { label: "最高学历", icon: "GraduationCap", row: 2, order: 1 },
    website: { label: "个人网站", icon: "Globe", row: 2, order: 2 },
    github: { label: "代码仓库", icon: "Github", row: 2, order: 3 },
    expected_salary: { label: "期望薪资", icon: "Briefcase", row: 2, order: 4 },
  }
  const defaultFieldConfig: Record<string, any> = {
    phone: { label: "电话", icon: "Phone", row: 1, order: 1 },
    email: { label: "邮箱", icon: "Mail", row: 1, order: 2 },
    status: { label: "当前状态", icon: "Info", row: 1, order: 3 },
    location: { label: "地点", icon: "MapPin", row: 1, order: 4 },
    highest_degree: { label: "最高学历", icon: "GraduationCap", row: 2, order: 1 },
    website: { label: "个人网站", icon: "Globe", row: 2, order: 2 },
    github: { label: "代码仓库", icon: "Github", row: 2, order: 3 },
    expected_salary: { label: "期望薪资", icon: "Briefcase", row: 2, order: 4 },
  }
  for (const [key, value] of Object.entries(defaultFieldConfig)) {
    const current = data.basics.field_config[key]
    data.basics.field_config[key] = { ...value, ...(current && typeof current === "object" && !Array.isArray(current) ? current : {}), label: value.label }
  }
  data.summary ||= { content: "" }
  if (typeof data.summary === "string") data.summary = { content: data.summary }
  for (const key of ["education", "skills", "work", "projects", "awards", "custom_sections"]) {
    if (!Array.isArray(data[key])) data[key] = []
  }
  data.layout ||= {}
  const customIds = data.custom_sections.map((item: any) => item.id).filter(Boolean)
  data.layout.section_order = Array.isArray(data.layout.section_order) && data.layout.section_order.length
    ? data.layout.section_order.filter((key: string) => builtInSections.includes(key) || customIds.includes(key))
    : [...builtInSections, ...customIds]
  for (const key of [...builtInSections, ...customIds]) {
    if (!data.layout.section_order.includes(key)) data.layout.section_order.push(key)
  }
  data.layout.section_order = ["basics", ...data.layout.section_order.filter((key: string) => key !== "basics")]
  data.layout.hidden_sections = Array.isArray(data.layout.hidden_sections) ? data.layout.hidden_sections.filter((key: string) => key !== "basics") : []
  
  data.layout.section_titles ||= {}
  for (const key of builtInSections) {
    if (!data.layout.section_titles[key] || data.layout.section_titles[key] === key) data.layout.section_titles[key] = builtInTitles[key]
  }
  for (const item of data.custom_sections) {
    if (!data.layout.section_titles[item.id] || data.layout.section_titles[item.id] === item.id) {
      data.layout.section_titles[item.id] = item.title || "自定义模块"
    }
  }
  return data as ResumeData
}

function normalizeTemplateConfig(input: any, templateId = "tech"): TemplateConfig {
  const pageMarginTop = input?.page_margin_top ?? 14
  const pageMarginBottom = input?.page_margin_bottom ?? 14
  return {
    theme_color: "#2563eb",
    font_family: "vf-sans",
    name_font_size: 28,
    name_font_color: "#111827",
    title_font_size: 16,
    title_font_color: "#111827",
    body_font_size: 13,
    body_font_color: "#374151",
    icon_color: input?.icon_color || input?.theme_color || "#2563eb",
    header_icon_color: input?.header_icon_color || "#ffffff",
    line_height: 1.6,
    page_margin_right: 16,
    page_margin_left: 16,
    section_margin_top: 10,
    section_margin_bottom: 10,
    section_title_margin_bottom: 6,
    show_avatar: true,
    ...(input || {}),
    page_margin_top: pageMarginTop,
    page_margin_bottom: pageMarginBottom,
    next_page_margin_top: input?.next_page_margin_top ?? pageMarginTop,
    next_page_margin_bottom: input?.next_page_margin_bottom ?? pageMarginBottom,
    template_id: input?.template_id || templateId,
  }
}

export const useResumeStore = defineStore("resume", {
  state: () => ({
    resumeList: [] as ResumeItem[],
    currentResume: null as ResumeItem | null,
    previewHtml: "",
    previewPdfBlob: null as Blob | null,
  }),
  getters: {
    resumeData: (state) => state.currentResume?.resume_data as ResumeData | undefined,
    templateConfig: (state) => state.currentResume?.template_config as TemplateConfig | undefined,
  },
  actions: {
    async fetchResumeList() {
      this.resumeList = await listResumesApi()
    },
    async fetchResumeDetail(id: number) {
      this.currentResume = await getResumeApi(id)
      if (this.currentResume) {
        this.currentResume.resume_data = normalizeResumeData(this.currentResume.resume_data)
        this.currentResume.template_config = normalizeTemplateConfig(this.currentResume.template_config, this.currentResume.template_id)
      }
      await this.refreshPreviewHtml()
    },
    async createResume(templateId = "tech") {
      return await createResumeApi({
        title: "我的简历",
        template_id: templateId,
        template_config: normalizeTemplateConfig({}, templateId),
      } as any)
    },
    async createResumeFromAi(result: any) {
      const rawResumeData = result?.resume_data?.resume_data || result?.resume_data || result?.optimized_resume_data || (result?.basics ? result : null)
      const resumeData = normalizeResumeData(rawResumeData)
      if (!resumeData) throw new Error("AI 生成结果中没有简历数据")
      const title = resumeData?.basics?.title || result?.target_position || "AI 生成简历"
      const templateId = String(result.template_id || "tech")
      return await createResumeApi({
        title,
        template_id: templateId,
        resume_data: resumeData,
        template_config: normalizeTemplateConfig(result.template_config, templateId),
      } as any)
    },
    async updateResume(payload?: Partial<ResumeItem>) {
      if (!this.currentResume) return
      const updated = await updateResumeApi(this.currentResume.id, payload || this.currentResume)
      updated.resume_data = normalizeResumeData(updated.resume_data)
      updated.template_config = normalizeTemplateConfig(updated.template_config, updated.template_id)
      this.currentResume = updated
    },
    async deleteResume(id: number) {
      await deleteResumeApi(id)
      await this.fetchResumeList()
    },
    async duplicateResume(id: number) {
      await duplicateResumeApi(id)
      await this.fetchResumeList()
    },
    updateResumeData(data: ResumeData) {
      if (this.currentResume) this.currentResume.resume_data = normalizeResumeData(data)
    },
    updateTemplateConfig(config: TemplateConfig) {
      if (this.currentResume) this.currentResume.template_config = config
    },
    async refreshPreviewHtml() {
      if (!this.currentResume) return
      this.previewHtml = await previewHtmlApi(this.currentResume.id)
    },
    async refreshPreviewPdf() {
      if (!this.currentResume) return
      this.previewPdfBlob = await previewPdfApi(this.currentResume.id)
    },
  },
})
