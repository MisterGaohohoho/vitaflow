import request from "./request"
import type { ResumeItem } from "@/types/resume"

export const listResumesApi = () => request.get<ResumeItem[], ResumeItem[]>("/resumes")
export const createResumeApi = (data: Partial<ResumeItem>) => request.post<any, ResumeItem>("/resumes", data)
export const getResumeApi = (id: number) => request.get<ResumeItem, ResumeItem>(`/resumes/${id}`)
export const updateResumeApi = (id: number, data: Partial<ResumeItem>) => request.put<any, ResumeItem>(`/resumes/${id}`, data)
export const deleteResumeApi = (id: number) => request.delete(`/resumes/${id}`)
export const duplicateResumeApi = (id: number) => request.post<any, ResumeItem>(`/resumes/${id}/duplicate`)
export const previewHtmlApi = (id: number) => request.get<string, string>(`/resumes/${id}/preview-html`, { responseType: "text" as any })
/** 获取简历的 PDF 预览文件流 */
export async function previewPdfApi(id: number): Promise<Blob> {
  const res = await request.get(`/resumes/${id}/preview-pdf`, { responseType: "blob", timeout: 120000 })
  return ((res as any).data || res) as Blob
}
