import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../utils/api.js'

export const useTemplateStore = defineStore('templates', () => {
  const templates = ref([])

  async function fetchTemplates() {
    templates.value = await api.listTemplates()
  }

  async function createTemplate(data) {
    const tmpl = await api.createTemplate(data)
    await fetchTemplates()
    return tmpl
  }

  async function deleteTemplate(id) {
    await api.deleteTemplate(id)
    await fetchTemplates()
  }

  return { templates, fetchTemplates, createTemplate, deleteTemplate }
})
