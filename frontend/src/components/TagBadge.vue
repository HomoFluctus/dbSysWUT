<template>
  <span class="tag-badge" :style="{ background: tag.color + '30', color: tag.color, borderColor: tag.color + '50' }">
    {{ tag.name }}
  </span>
</template>

<script setup>
defineProps({ tag: Object })
</script>

<style scoped>
.tag-badge {
  display: inline-block; padding: 1px 8px; border-radius: 10px;
  font-size: 11px; border: 1px solid; margin-right: 4px;
}
</style>
