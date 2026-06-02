<template>
  <div class="chart-container">
    <canvas ref="canvasRef"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
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
      plugins: { legend: { labels: { color: '#94a3b8' } } },
      scales: props.type !== 'doughnut' ? {
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
      } : {},
      ...props.options,
    },
  })
}

onMounted(render)
watch(() => props.data, render, { deep: true })
</script>

<style scoped>
.chart-container { position: relative; height: 280px; }
</style>
