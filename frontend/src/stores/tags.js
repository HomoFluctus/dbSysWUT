import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../utils/api.js'

export const useTagStore = defineStore('tags', () => {
  const tags = ref([])

  async function fetchTags() {
    tags.value = await api.listTags()
  }

  async function createTag(data) {
    await api.createTag(data)
    await fetchTags()
  }

  async function deleteTag(id) {
    await api.deleteTag(id)
    await fetchTags()
  }

  return { tags, fetchTags, createTag, deleteTag }
})
