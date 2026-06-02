<template>
  <el-tag
    :style="{ borderColor: tag.color + '60', color: tag.color, background: tag.color + '18' }"
    size="small"
    effect="plain"
  >
    {{ tag.name }}
  </el-tag>
</template>

<script setup>
defineProps({ tag: Object })
</script>
