<script setup lang="ts">
import {
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectIcon,
  SelectPortal,
  SelectContent,
  SelectViewport,
  SelectItem,
  SelectItemText,
  SelectItemIndicator,
} from 'radix-vue'
import { ChevronDown, Check } from 'lucide-vue-next'

const props = defineProps<{
  modelValue?: any
  options?: any[]
  placeholder?: string
  disabled?: boolean
  class?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: any]
  change: [value: any]
}>()

const getOptionValue = (option: any) => typeof option === 'object' && option !== null ? option.value : option
const getOptionLabel = (option: any) => typeof option === 'object' && option !== null ? option.label : option

const updateValue = (strVal: string) => {
  const selectedOption = props.options?.find(o => String(getOptionValue(o)) === strVal)
  const realVal = selectedOption !== undefined ? getOptionValue(selectedOption) : strVal
  emit('update:modelValue', realVal)
  emit('change', realVal)
}
</script>

<template>
  <SelectRoot :model-value="modelValue !== undefined ? String(modelValue) : undefined" @update:model-value="updateValue" :disabled="disabled">
    <SelectTrigger 
      class="flex w-full h-9 items-center justify-between rounded-md border border-zinc-200 bg-white px-3 text-sm shadow-sm ring-offset-white placeholder:text-zinc-500 focus:outline-none focus:ring-1 focus:ring-zinc-900 disabled:cursor-not-allowed disabled:opacity-50 transition-all hover:border-zinc-300 data-[state=open]:border-zinc-900 data-[state=open]:ring-1 data-[state=open]:ring-zinc-900"
      :class="props.class"
    >
      <SelectValue :placeholder="placeholder" />
      <SelectIcon>
        <ChevronDown class="h-4 w-4 opacity-50" />
      </SelectIcon>
    </SelectTrigger>
    
    <SelectPortal>
      <SelectContent 
        class="relative z-50 min-w-[8rem] overflow-hidden rounded-md border border-zinc-200 bg-white text-zinc-950 shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2"
        position="popper"
        :side-offset="4"
      >
        <SelectViewport class="p-1">
          <SelectItem 
            v-for="option in options" 
            :key="String(getOptionValue(option))" 
            :value="String(getOptionValue(option))"
            class="relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-zinc-100 focus:text-zinc-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
          >
            <span class="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
              <SelectItemIndicator>
                <Check class="h-4 w-4" />
              </SelectItemIndicator>
            </span>
            <SelectItemText>{{ getOptionLabel(option) }}</SelectItemText>
          </SelectItem>
        </SelectViewport>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>
