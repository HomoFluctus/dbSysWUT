import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../utils/api.js'

export const useCategoryStore = defineStore('categories', () => {
  const categories = ref([])

  async function fetchCategories() {
    categories.value = await api.listCategories()
  }

  async function createCategory(data) {
    const cat = await api.createCategory(data)
    await fetchCategories()
    return cat
  }

  async function updateCategory(id, data) {
    await api.updateCategory(id, data)
    await fetchCategories()
  }

  async function deleteCategory(id) {
    await api.deleteCategory(id)
    await fetchCategories()
  }

  return { categories, fetchCategories, createCategory, updateCategory, deleteCategory }
})
