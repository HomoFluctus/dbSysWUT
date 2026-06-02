<template>
  <div class="categories-page">
    <h2>&#x1f3a8; 分类管理</h2>

    <div class="create-row">
      <el-input v-model="newName" placeholder="分类名称" style="width: 200px" @keyup.enter="handleCreate" />
      <el-color-picker v-model="newColor" />
      <el-button type="primary" @click="handleCreate" :icon="Plus">添加</el-button>
    </div>

    <div class="cat-list" v-loading="loading">
      <div v-for="c in catStore.categories" :key="c.category_id" class="cat-item">
        <div class="cat-left">
          <span class="cat-dot" :style="{ background: c.color }"></span>
          <template v-if="editingId === c.category_id">
            <el-input
              v-model="editName"
              size="small"
              style="width: 140px"
              @keyup.enter="saveName(c.category_id)"
              @blur="saveName(c.category_id)"
              ref="nameInputRef"
            />
          </template>
          <template v-else>
            <span class="cat-name" @click="startEdit(c)">{{ c.name }}</span>
          </template>
          <el-tag v-if="c.is_default" size="small" type="info">默认</el-tag>
          <span class="cat-count">{{ c.schedule_count }} 项</span>
        </div>
        <div class="cat-right">
          <el-color-picker v-model="editColors[c.category_id]" @change="updateColor(c.category_id)" size="small" />
          <el-button
            :icon="Edit"
            circle
            size="small"
            @click="startEdit(c)"
            v-if="editingId !== c.category_id"
          />
          <el-popconfirm title="删除此分类？关联的日程不会删除" @confirm="handleDelete(c.category_id)">
            <template #reference>
              <el-button type="danger" :icon="Delete" circle size="small" :disabled="c.is_default" />
            </template>
          </el-popconfirm>
        </div>
      </div>
      <el-empty v-if="!loading && catStore.categories.length === 0" description="暂无分类" :image-size="60" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive, nextTick } from 'vue'
import { useCategoryStore } from '../stores/categories.js'
import { ElMessage } from 'element-plus'
import { Plus, Delete, Edit } from '@element-plus/icons-vue'

const catStore = useCategoryStore()
const newName = ref('')
const newColor = ref('#6366f1')
const editColors = reactive({})
const loading = ref(false)
const editingId = ref(null)
const editName = ref('')
const nameInputRef = ref(null)

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
    catStore.categories.forEach(c => { editColors[c.category_id] = c.color })
    newName.value = ''
    ElMessage.success('分类已添加')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

function startEdit(c) {
  editingId.value = c.category_id
  editName.value = c.name
  nextTick(() => {
    const input = document.querySelector('.cat-item input')
    if (input) input.focus()
  })
}

async function saveName(id) {
  if (!editName.value.trim()) {
    editingId.value = null
    return
  }
  try {
    await catStore.updateCategory(id, { name: editName.value.trim() })
    ElMessage.success('名称已更新')
  } catch (e) {
    ElMessage.error(e.message)
  }
  editingId.value = null
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
.cat-left { display: flex; align-items: center; gap: 10px; flex: 1; }
.cat-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.cat-name {
  font-size: 14px; color: var(--text-primary); font-weight: 500;
  cursor: pointer; padding: 2px 4px; border-radius: 4px;
  transition: background var(--transition-fast);
}
.cat-name:hover { background: var(--el-fill-color); }
.cat-count { font-size: 12px; color: var(--text-muted); }
.cat-right { display: flex; align-items: center; gap: 8px; }
</style>
