<script setup lang="ts">
import { Plus, Trash2 } from "lucide-vue-next"
import Button from "@/components/ui/button/Button.vue"
import Input from "@/components/ui/input/Input.vue"
import Label from "@/components/ui/label/Label.vue"
import MarkdownEditor from "./MarkdownEditor.vue"
defineProps<{ section: any }>()
defineEmits<{ change: [] }>()
</script>
<template>
  <div class="space-y-3">
    <Button size="sm" variant="outline" @click="section.items.push({ id: `item_${Date.now()}`, title: '', content: '' }); $emit('change')"><Plus class="h-4 w-4" />新增内容</Button>
    <div v-for="(item, i) in section.items" :key="item.id" class="rounded-lg border border-gray-200 p-4">
      <div class="mb-3 flex justify-between"><Label>标题</Label><Button size="icon" variant="ghost" @click="section.items.splice(i, 1); $emit('change')"><Trash2 class="h-4 w-4" /></Button></div>
      <Input v-model="item.title" @update:model-value="$emit('change')" />
      <div class="mt-3"><Label>内容</Label><MarkdownEditor v-model="item.content" @update:model-value="$emit('change')" /></div>
    </div>
  </div>
</template>
