<script setup lang="ts">
import Textarea from "@/components/ui/textarea/Textarea.vue"

const props = defineProps<{ modelValue: string; placeholder?: string }>()
defineEmits<{ "update:modelValue": [value: string] }>()
</script>
<template>
  <div class="grid">
    <Textarea :model-value="modelValue" :placeholder="placeholder" :rows="7" @update:model-value="$emit('update:modelValue', $event)" />
  </div>
</template>
