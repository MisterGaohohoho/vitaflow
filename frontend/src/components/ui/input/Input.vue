<script setup lang="ts">
defineProps<{ modelValue?: string | number; placeholder?: string; type?: string }>()
defineEmits<{ "update:modelValue": [value: string] }>()
</script>
<template>
  <input :type="type || 'text'" :value="modelValue" :placeholder="placeholder" class="h-9 w-full rounded-md border border-zinc-200 bg-white px-3 text-[14px] outline-none transition-all placeholder:text-zinc-400 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 shadow-sm" @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)" />
</template>
