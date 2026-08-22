import { defineStore } from 'pinia'
import http from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null
  }),
  getters: {
    isAdmin: (s) => s.user?.role === 'admin',
    isEngineer: (s) => s.user && ['engineer', 'admin'].includes(s.user.role),
    isLoggedIn: (s) => !!s.token
  },
  actions: {
    setSession(r) {
      this.token = r.access_token
      this.user = r.user
      localStorage.setItem('token', r.access_token)
    },
    async login(username, password) {
      const r = await http.post('/auth/login', { username, password })
      this.setSession(r)
    },
    async register(username, password, phone) {
      const r = await http.post('/auth/register', { username, password, phone })
      this.setSession(r)
    },
    async fetchMe() {
      this.user = await http.get('/auth/me')
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
