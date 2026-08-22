import { defineStore } from 'pinia'
import http from '../api/http'

export const useAppStore = defineStore('app', {
  state: () => ({ mode: '' }),
  getters: {
    isPublic: (s) => s.mode === 'public',
    isFull: (s) => s.mode === 'full'
  },
  actions: {
    async fetchHealth() {
      const r = await http.get('/health')
      this.mode = r.mode
    }
  }
})
