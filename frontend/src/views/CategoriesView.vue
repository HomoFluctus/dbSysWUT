<template>
  <div class="categories-page">
    <h2>Categories</h2>

    <form @submit.prevent="handleCreate" class="create-form">
      <input v-model="newName" placeholder="Category name" required />
      <input v-model="newColor" type="color" value="#6366f1" />
      <button type="submit" class="btn-sm">Add</button>
    </form>

    <div class="cat-list">
      <div v-for="c in catStore.categories" :key="c.category_id" class="cat-item">
        <span class="cat-color" :style="{ background: c.color }"></span>
        <span class="cat-name">{{ c.name }}</span>
        <span v-if="c.is_default" class="default-badge">Default</span>
        <div class="cat-actions">
          <input v-model="editColors[c.category_id]" type="color" style="width:32px;height:32px;padding:0;border:none" @change="updateColor(c.category_id)" />
          <button @click="handleDelete(c.category_id)" class="btn-del">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive } from 'vue'
import { useCategoryStore } from '../stores/categories.js'

const catStore = useCategoryStore()
const newName = ref('')
const newColor = ref('#6366f1')
const editColors = reactive({})

onMounted(async () => {
  await catStore.fetchCategories()
  catStore.categories.forEach(c => { editColors[c.category_id] = c.color })
})

async function handleCreate() {
  await catStore.createCategory({ name: newName.value, color: newColor.value })
  newName.value = ''
}

async function updateColor(id) {
  await catStore.updateCategory(id, { color: editColors[id] })
}

async function handleDelete(id) {
  if (confirm('Delete this category?')) {
    await catStore.deleteCategory(id)
  }
}
</script>

<style scoped>
.categories-page { max-width: 600px; }
h2 { font-size: 24px; color: #f1f5f9; margin-bottom: 20px; }
.create-form { display: flex; gap: 8px; margin-bottom: 20px; }
.create-form input[type="text"] {
  flex: 1; padding: 10px; border-radius: 8px; border: 1px solid #334155;
  background: #1e293b; color: #e2e8f0; font-size: 14px;
}
.btn-sm { padding: 10px 16px; background: #6366f1; color: #fff; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; }
.btn-sm:hover { background: #4f46e5; }

.cat-item {
  display: flex; align-items: center; gap: 12px; padding: 14px;
  background: #1e293b; border: 1px solid #334155; border-radius: 10px; margin-bottom: 8px;
}
.cat-color { width: 16px; height: 16px; border-radius: 50%; flex-shrink: 0; }
.cat-name { flex: 1; font-size: 14px; color: #e2e8f0; }
.default-badge { font-size: 11px; color: #6366f1; background: #1e1b4b; padding: 2px 8px; border-radius: 8px; }
.cat-actions { display: flex; gap: 8px; align-items: center; }
.btn-del {
  padding: 6px 12px; background: none; border: 1px solid #7f1d1d; color: #f87171;
  border-radius: 6px; cursor: pointer; font-size: 12px;
}
.btn-del:hover { background: #7f1d1d; }
</style>
