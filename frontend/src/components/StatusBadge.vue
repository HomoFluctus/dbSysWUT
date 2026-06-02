<template>
  <span class="badge" :class="status">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'
import { getStatusLabel } from '../utils/date.js'

const props = defineProps({ status: String })
const label = computed(() => getStatusLabel(props.status))
</script>

<style scoped>
.badge {
  display: inline-block; padding: 2px 10px; border-radius: 12px;
  font-size: 11px; font-weight: 600;
}
.todo { background: #334155; color: #94a3b8; }
.in_progress { background: #1e3a5f; color: #60a5fa; }
.done { background: #14532d; color: #4ade80; }
.cancelled { background: #3f3f46; color: #a1a1aa; }
</style>
