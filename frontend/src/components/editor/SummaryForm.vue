<script setup lang="ts">
import Label from "@/components/ui/label/Label.vue"
import MarkdownEditor from "./MarkdownEditor.vue"
defineProps<{ summary: { content: string } }>()
defineEmits<{ change: [] }>()
</script>
<template>
  <div class="max-w-3xl mx-auto py-2">
    <Label class="text-[13px] text-zinc-600 mb-2 block font-medium">个人简介</Label>
    <MarkdownEditor v-model="summary.content" @update:model-value="$emit('change')" />
  </div>
</template>
