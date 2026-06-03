<template>
  <div class="template-picker">
    <el-button @click="visible = true" :icon="Collection" size="default">
      从模板加载
    </el-button>

    <el-dialog v-model="visible" title="日程模板" width="480px">
      <div v-if="tplStore.templates.length === 0" style="text-align: center; padding: 30px;">
        <el-empty description="暂无模板" :image-size="60" />
        <p style="color: var(--text-muted); font-size: 13px;">在日程详情页可以将日程保存为模板</p>
      </div>
      <div v-else class="tpl-list">
        <div v-for="t in tplStore.templates" :key="t.template_id" class="tpl-item">
          <div class="tpl-info">
            <div class="tpl-title">{{ t.title }}</div>
            <div class="tpl-meta" v-if="t.description">{{ t.description }}</div>
          </div>
          <div class="tpl-actions">
            <el-button size="small" type="primary" @click="applyTemplate(t.template_id)">使用</el-button>
            <el-button size="small" type="danger" @click="removeTemplate(t.template_id)">删除</el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useTemplateStore } from '../stores/templates.js'
import { api } from '../utils/api.js'
import { ElMessage } from 'element-plus'
import { Collection } from '@element-plus/icons-vue'

const emit = defineEmits(['apply'])
const tplStore = useTemplateStore()
const visible = ref(false)

async function applyTemplate(id) {
  try {
    const data = await api.applyTemplate(id)
    visible.value = false
    emit('apply', data)
    ElMessage.success('模板已加载')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function removeTemplate(id) {
  try {
    await tplStore.deleteTemplate(id)
    ElMessage.success('模板已删除')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

defineExpose({ open: () => { tplStore.fetchTemplates(); visible.value = true } })
</script>

<style scoped>
.template-picker { display: inline-block; }
.tpl-list { display: flex; flex-direction: column; gap: 8px; }
.tpl-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: var(--bg-base);
  border: 1px solid var(--border-color);
  border-radius: 10px;
}
.tpl-title { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.tpl-meta { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.tpl-actions { display: flex; gap: 6px; flex-shrink: 0; }
</style>
