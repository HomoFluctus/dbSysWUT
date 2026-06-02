<template>
  <span class="badge" :style="{ background: bg, color: '#fff' }">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'
import { getPriorityLabel, getPriorityColor } from '../utils/date.js'

const props = defineProps({ priority: String })
const label = computed(() => getPriorityLabel(props.priority))
const bg = computed(() => getPriorityColor(props.priority))
</script>

<style scoped>
.badge {
  display: inline-block; padding: 2px 8px; border-radius: 12px;
  font-size: 11px; font-weight: 600;
}
</style>
