import { defineStore } from "pinia"

export const useEditorStore = defineStore("editor", {
  state: () => ({
    currentSection: "basics",
    saving: false,
    saved: true,
    saveError: false,
    previewScale: 0.72,
  }),
  actions: {
    setCurrentSection(section: string) {
      this.currentSection = section
    },
    setPreviewScale(scale: number) {
      this.previewScale = scale
    },
    setSaving(value: boolean) {
      this.saving = value
    },
    setSaved(value: boolean) {
      this.saved = value
      this.saveError = false
    },
  },
})
