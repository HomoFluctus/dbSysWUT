<template>
  <div class="categories-page">
    <div class="page-header">
      <h2>分类管理</h2>
      <p class="page-desc">管理日程分类，点击分类可筛选对应日程</p>
    </div>

    <!-- Add new category -->
    <div class="create-row">
      <el-input
        v-model="newName"
        placeholder="输入分类名称"
        style="width: 220px"
        maxlength="20"
        show-word-limit
        @keyup.enter="handleCreate"
      />
      <el-color-picker v-model="newColor" />
      <el-button type="primary" @click="handleCreate" :loading="creating">
        <el-icon><Plus /></el-icon>添加分类
      </el-button>
    </div>

    <!-- Category list -->
    <div v-loading="loading" class="cat-list">
      <div
        v-for="c in catStore.categories"
        :key="c.category_id"
        class="cat-item"
      >
        <div class="cat-left" @click="goFiltered(c)">
          <span class="cat-dot" :style="{ background: c.color }"></span>

          <!-- Inline name editor -->
          <template v-if="editingId === c.category_id">
            <el-input
              v-model="editName"
              size="small"
              style="width: 150px"
              maxlength="20"
              @keyup.enter.stop="saveName(c)"
              @blur="saveName(c)"
              ref="editInput"
            />
          </template>
          <template v-else>
            <span class="cat-name" @click="startEdit(c)">{{ c.name }}</span>
          </template>

          <el-tag v-if="c.is_default" size="small" type="info" effect="plain">默认</el-tag>
          <span class="cat-count" @click="goFiltered(c)">{{ c.schedule_count }} 个日程</span>
        </div>

        <div class="cat-right">
          <el-color-picker
            :model-value="c.color"
            @update:model-value="(val) => updateColor(c, val)"
            size="small"
          />
          <el-tooltip content="重命名" v-if="editingId !== c.category_id">
            <el-button :icon="Edit" circle size="small" @click="startEdit(c)" />
          </el-tooltip>
          <el-tooltip :content="c.is_default ? '不能删除默认分类' : '删除分类'">
            <el-button
              type="danger"
              :icon="Delete"
              circle
              size="small"
              :disabled="c.is_default"
              @click="confirmDelete(c)"
            />
          </el-tooltip>
        </div>
      </div>

      <el-empty
        v-if="!loading && catStore.categories.length === 0"
        description="还没有分类，创建一个吧"
        :image-size="80"
      >
        <el-button type="primary" @click="handleCreate">创建第一个分类</el-button>
      </el-empty>
    </div>

    <!-- Quick stats -->
    <div class="cat-footer" v-if="catStore.categories.length > 0">
      共 {{ catStore.categories.length }} 个分类，{{ totalSchedules }} 个日程
    </div>

    <!-- Delete confirmation dialog -->
    <el-dialog v-model="deleteDialogVisible" title="确认删除" width="420px">
      <template v-if="deletingCat">
        <p>确定要删除分类 <strong>{{ deletingCat.name }}</strong> 吗？</p>
        <p v-if="deletingCat.schedule_count > 0" class="delete-warn">
          该分类下有 {{ deletingCat.schedule_count }} 个日程，删除后这些日程的分类将变为空。
        </p>
      </template>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="executeDelete" :loading="deleting">
          确认删除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useCategoryStore } from '../stores/categories.js'
import { ElMessage } from 'element-plus'
import { Plus, Delete, Edit } from '@element-plus/icons-vue'

const router = useRouter()
const catStore = useCategoryStore()

const newName = ref('')
const newColor = ref('#6366f1')
const loading = ref(false)
const creating = ref(false)
const deleting = ref(false)
const editingId = ref(null)
const editName = ref('')
const editInput = ref(null)
const saving = ref(false)

const deleteDialogVisible = ref(false)
const deletingCat = ref(null)

const totalSchedules = computed(() =>
  catStore.categories.reduce((sum, c) => sum + c.schedule_count, 0)
)

onMounted(async () => {
  loading.value = true
  try {
    await catStore.fetchCategories()
  } finally {
    loading.value = false
  }
})

async function handleCreate() {
  const name = newName.value.trim()
  if (!name) {
    ElMessage.warning('请输入分类名称')
    return
  }
  creating.value = true
  try {
    await catStore.createCategory({ name, color: newColor.value })
    newName.value = ''
    newColor.value = '#6366f1'
    ElMessage.success('分类已添加')
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    creating.value = false
  }
}

function startEdit(c) {
  editingId.value = c.category_id
  editName.value = c.name
  nextTick(() => {
    // Find the input within the scope of the editing row
    const inputs = document.querySelectorAll('.cat-item .el-input__inner')
    inputs.forEach(el => {
      if (el.value === c.name) {
        el.focus()
        el.select()
      }
    })
  })
}

async function saveName(c) {
  if (saving.value) return
  const name = editName.value.trim()
  if (!name || name === c.name) {
    editingId.value = null
    return
  }
  saving.value = true
  try {
    await catStore.updateCategory(c.category_id, { name })
    ElMessage.success('名称已更新')
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    saving.value = false
    editingId.value = null
  }
}

async function updateColor(c, newColor) {
  if (!newColor || newColor === c.color) return
  try {
    await catStore.updateCategory(c.category_id, { color: newColor })
    ElMessage.success('颜色已更新')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

function goFiltered(c) {
  if (editingId.value) return
  router.push({ path: '/', query: { category_id: c.category_id } })
}

function confirmDelete(c) {
  deletingCat.value = c
  deleteDialogVisible.value = true
}

async function executeDelete() {
  if (!deletingCat.value) return
  deleting.value = true
  try {
    await catStore.deleteCategory(deletingCat.value.category_id)
    ElMessage.success('分类已删除')
    deleteDialogVisible.value = false
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.categories-page { max-width: 640px; }
.page-header { margin-bottom: 24px; }
.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}
.page-desc { font-size: 13px; color: var(--text-muted); }

.create-row {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.cat-list { display: flex; flex-direction: column; gap: 8px; min-height: 100px; }
.cat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  transition: all var(--transition-fast);
  cursor: default;
}
.cat-item:hover { border-color: var(--el-color-primary); }

.cat-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}
.cat-dot {
  width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0;
  box-shadow: 0 0 6px rgba(0,0,0,0.15);
}
.cat-name {
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  transition: background var(--transition-fast);
  white-space: nowrap;
}
.cat-name:hover { background: var(--el-fill-color); }
.cat-count {
  font-size: 12px;
  color: var(--text-muted);
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all var(--transition-fast);
  white-space: nowrap;
}
.cat-count:hover {
  background: var(--el-fill-color);
  color: var(--el-color-primary);
}

.cat-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }

.delete-warn {
  color: var(--el-color-warning);
  font-size: 13px;
  margin-top: 8px;
}
.cat-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}
</style>
