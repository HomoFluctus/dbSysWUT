<template>
  <div class="categories-page">
    <h2>&#x1f3a8; 分类管理</h2>

    <div class="create-row">
      <el-input v-model="newName" placeholder="分类名称" style="width: 200px" />
      <el-color-picker v-model="newColor" />
      <el-button type="primary" @click="handleCreate" :icon="Plus">添加</el-button>
    </div>

    <div class="cat-list" v-loading="loading">
      <div v-for="c in catStore.categories" :key="c.category_id" class="cat-item">
        <div class="cat-left">
          <el-icon :size="16"><Folder /></el-icon>
          <span class="cat-name">{{ c.name }}</span>
          <el-tag v-if="c.is_default" size="small" type="info">默认</el-tag>
        </div>
        <div class="cat-right">
          <el-color-picker v-model="editColors[c.category_id]" @change="updateColor(c.category_id)" size="small" />
          <el-popconfirm title="删除此分类？" @confirm="handleDelete(c.category_id)">
            <template #reference>
              <el-button type="danger" :icon="Delete" circle size="small" :disabled="c.is_default" />
            </template>
          </el-popconfirm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive } from 'vue'
import { useCategoryStore } from '../stores/categories.js'
import { ElMessage } from 'element-plus'
import { Plus, Delete, Folder } from '@element-plus/icons-vue'

const catStore = useCategoryStore()
const newName = ref('')
const newColor = ref('#6366f1')
const editColors = reactive({})
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    await catStore.fetchCategories()
    catStore.categories.forEach(c => { editColors[c.category_id] = c.color })
  } finally {
    loading.value = false
  }
})

async function handleCreate() {
  if (!newName.value.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  try {
    await catStore.createCategory({ name: newName.value.trim(), color: newColor.value })
    newName.value = ''
    ElMessage.success('分类已添加')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function updateColor(id) {
  try {
    await catStore.updateCategory(id, { color: editColors[id] })
    ElMessage.success('颜色已更新')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function handleDelete(id) {
  try {
    await catStore.deleteCategory(id)
    ElMessage.success('分类已删除')
  } catch (e) {
    ElMessage.error(e.message)
  }
}
</script>

<style scoped>
.categories-page { max-width: 600px; }
.categories-page h2 { font-size: 24px; color: var(--text-primary); margin-bottom: 20px; }
.create-row { display: flex; gap: 10px; align-items: center; margin-bottom: 20px; }

.cat-list { display: flex; flex-direction: column; gap: 8px; }
.cat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 10px;
}
.cat-left { display: flex; align-items: center; gap: 10px; }
.cat-name { font-size: 14px; color: var(--text-secondary); font-weight: 500; }
.cat-right { display: flex; align-items: center; gap: 8px; }
</style>
