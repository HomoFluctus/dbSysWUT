<template>
  <div class="streak-card" v-if="streaks">
    <el-row :gutter="16">
      <el-col :span="12">
        <div class="streak-item current">
          <div class="streak-flame">&#x1f525;</div>
          <div class="streak-value">{{ streaks.current_streak }}</div>
          <div class="streak-label">当前连续</div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="streak-item longest">
          <div class="streak-flame">&#x1f3c6;</div>
          <div class="streak-value">{{ streaks.longest_streak }}</div>
          <div class="streak-label">最长连续</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../utils/api.js'

const streaks = ref(null)

onMounted(async () => {
  try {
    streaks.value = await api.getStreaks()
  } catch (e) {
    // silently fail for streaks
  }
})
</script>

<style scoped>
.streak-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 24px;
}
.streak-item {
  text-align: center;
  padding: 10px;
  border-radius: 10px;
}
.streak-item.current { background: rgba(249,115,22,0.08); }
.streak-item.longest { background: rgba(234,179,8,0.08); }
.streak-flame { font-size: 22px; margin-bottom: 2px; }
.streak-value { font-size: 30px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
.streak-label { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
</style>
