import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('../views/Dashboard.vue') },
      { path: 'chat', component: () => import('../views/Placeholder.vue') },
      { path: 'knowledge', component: () => import('../views/knowledge/KnowledgeBrowse.vue') },
      { path: 'knowledge/:id', component: () => import('../views/knowledge/KnowledgeDetail.vue') },
      { path: 'tickets', component: () => import('../views/Placeholder.vue') },
      { path: 'manage', component: () => import('../views/knowledge/KnowledgeList.vue'), meta: { roles: ['engineer', 'admin'] } },
      { path: 'manage/edit/:id?', component: () => import('../views/knowledge/KnowledgeEdit.vue'), meta: { roles: ['engineer', 'admin'] } },
      { path: 'review', component: () => import('../views/knowledge/ReviewCenter.vue'), meta: { roles: ['engineer', 'admin'] } },
      { path: 'admin/users', component: () => import('../views/admin/Users.vue'), meta: { roles: ['admin'] } }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.public) return true
  if (!auth.token) return '/login'
  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return '/login'
    }
  }
  if (to.meta.roles && !to.meta.roles.includes(auth.user.role)) return '/'
  return true
})

export default router
