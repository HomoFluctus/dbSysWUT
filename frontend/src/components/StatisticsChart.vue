<template>
  <div class="chart-wrapper">
    <canvas ref="canvasRef"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

const props = defineProps({
  type: { type: String, default: 'bar' },
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({}) },
})

const canvasRef = ref(null)
let chart = null

function render() {
  if (chart) chart.destroy()
  if (!canvasRef.value) return
  chart = new Chart(canvasRef.value, {
    type: props.type,
    data: props.data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#94a3b8', padding: 16, usePointStyle: true, pointStyleWidth: 8 },
        },
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#f1f5f9',
          bodyColor: '#e2e8f0',
          borderColor: '#334155',
          borderWidth: 1,
        },
      },
      scales: props.type !== 'doughnut' && props.type !== 'pie' ? {
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' }, border: { color: '#334155' } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' }, border: { color: '#334155' } },
      } : {},
      ...props.options,
    },
  })
}

onMounted(render)
watch(() => props.data, render, { deep: true })
onUnmounted(() => { if (chart) chart.destroy() })
</script>

<style scoped>
.chart-wrapper { position: relative; height: 260px; }
</style>
