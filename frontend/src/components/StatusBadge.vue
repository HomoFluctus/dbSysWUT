<template>
  <el-tag :type="type" size="small" effect="dark">
    {{ label }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ status: String })
const map = {
  todo: { label: '待办', type: 'info' },
  in_progress: { label: '进行中', type: '' },
  done: { label: '已完成', type: 'success' },
  cancelled: { label: '已取消', type: 'danger' },
}
const label = computed(() => map[props.status]?.label || props.status)
const type = computed(() => map[props.status]?.type || 'info')
</script>
