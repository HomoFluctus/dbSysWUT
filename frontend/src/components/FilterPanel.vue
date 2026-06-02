<template>
  <div class="filter-panel">
    <select v-model="localFilters.status" @change="emit">
      <option value="">All Status</option>
      <option value="todo">Todo</option>
      <option value="in_progress">In Progress</option>
      <option value="done">Done</option>
      <option value="cancelled">Cancelled</option>
    </select>
    <select v-model="localFilters.priority" @change="emit">
      <option value="">All Priority</option>
      <option value="low">Low</option>
      <option value="medium">Medium</option>
      <option value="high">High</option>
      <option value="urgent">Urgent</option>
    </select>
    <select v-model="localFilters.category_id" @change="emit">
      <option value="">All Categories</option>
      <option v-for="c in categories" :key="c.category_id" :value="c.category_id">{{ c.name }}</option>
    </select>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({ filters: Object, categories: Array })
const emit = defineEmits(['update:filters'])

const localFilters = reactive({ ...props.filters })

watch(() => props.filters, (v) => Object.assign(localFilters, v))

function emit() {
  emit('update:filters', { ...localFilters })
}
</script>

<style scoped>
.filter-panel { display: flex; gap: 12px; margin-bottom: 20px; }
select {
  padding: 8px 14px; border-radius: 8px; border: 1px solid #334155;
  background: #1e293b; color: #e2e8f0; font-size: 13px;
}
</style>
