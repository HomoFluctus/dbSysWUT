<template>
  <el-tag :color="color" :style="{ color: '#fff', border: 'none', fontWeight: 600 }" size="small" effect="dark">
    {{ label }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ priority: String })
const map = {
  low: { label: '低', color: '#22c55e' },
  medium: { label: '中', color: '#ca8a04' },
  high: { label: '高', color: '#ea580c' },
  urgent: { label: '紧急', color: '#dc2626' },
}
const label = computed(() => map[props.priority]?.label || props.priority)
const color = computed(() => map[props.priority]?.color || '#64748b')
</script>
