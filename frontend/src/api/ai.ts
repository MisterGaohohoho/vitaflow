import request from "./request"

export const generateResumeApi = (data: any) => request.post("/ai/generate-resume", data)
export const scoreResumeApi = (data: any) => request.post("/ai/score-resume", data)
export const optimizeSectionApi = (data: any) => request.post("/ai/optimize-section", data)
export const optimizeResumeApi = (data: any) => request.post("/ai/optimize-resume", data)
export const optimizeByJdApi = (data: any) => request.post("/ai/optimize-by-jd", data)
export const generateSummaryApi = (data: any) => request.post("/ai/generate-summary", data)
export const optimizeProjectApi = (data: any) => request.post("/ai/optimize-project", data)
export const getResumeChatMessagesApi = (resumeId: number) => request.get(`/ai/resume-chat/${resumeId}/messages`)
export const sendResumeChatMessageApi = (resumeId: number, data: { content: string }) => request.post(`/ai/resume-chat/${resumeId}/messages`, data)
export const clearResumeChatMessagesApi = (resumeId: number) => request.delete(`/ai/resume-chat/${resumeId}/messages`)
export const decideResumeChatChangeApi = (resumeId: number, messageId: number, action: "apply" | "reject") =>
  request.post(`/ai/resume-chat/${resumeId}/messages/${messageId}/decision`, { action })

type StreamCallbacks<T = any> = {
  onStart?: () => void
  onDelta?: (text: string) => void
  onPhase?: (phase: string, text: string) => void
  onResult?: (data: T) => void
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api"

async function postAiStream<T = any>(path: string, data: any, callbacks: StreamCallbacks<T> = {}) {
  const token = localStorage.getItem("vitaflow_token")
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(data),
  })

  if (response.status === 401) {
    localStorage.removeItem("vitaflow_token")
    window.location.href = "/login"
    throw new Error("登录已过期，请重新登录")
  }
  if (!response.ok || !response.body) {
    const message = await response.text().catch(() => "")
    throw new Error(message || "AI 请求失败")
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder("utf-8")
  let buffer = ""
  let finalResult: T | null = null

  const handleLine = (line: string) => {
    if (!line.trim()) return
    const event = JSON.parse(line)
    if (event.type === "start") callbacks.onStart?.()
    if (event.type === "delta") callbacks.onDelta?.(String(event.text || ""))
    if (event.type === "phase") callbacks.onPhase?.(String(event.phase || ""), String(event.text || ""))
    if (event.type === "result") {
      finalResult = event.data as T
      callbacks.onResult?.(finalResult)
    }
    if (event.type === "error") throw new Error(event.message || "AI 生成失败")
  }

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split("\n")
    buffer = lines.pop() || ""
    for (const line of lines) handleLine(line)
  }
  buffer += decoder.decode()
  if (buffer.trim()) handleLine(buffer)
  if (!finalResult) throw new Error("AI 未返回有效结果")
  return finalResult
}

export const generateResumeStreamApi = (data: any, callbacks?: StreamCallbacks) => postAiStream("/ai/generate-resume/stream", data, callbacks)
export const scoreResumeStreamApi = (data: any, callbacks?: StreamCallbacks) => postAiStream("/ai/score-resume/stream", data, callbacks)
export const optimizeSectionStreamApi = (data: any, callbacks?: StreamCallbacks) => postAiStream("/ai/optimize-section/stream", data, callbacks)
export const optimizeByJdStreamApi = (data: any, callbacks?: StreamCallbacks) => postAiStream("/ai/optimize-by-jd/stream", data, callbacks)
export const sendResumeChatMessageStreamApi = (resumeId: number, data: { content: string }, callbacks?: StreamCallbacks) =>
  postAiStream(`/ai/resume-chat/${resumeId}/messages/stream`, data, callbacks)
