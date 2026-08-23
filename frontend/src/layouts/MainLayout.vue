<template>
  <el-container style="min-height:100vh">
    <el-aside width="210px" class="aside">
      <div class="logo">注塑机智能问答</div>
      <el-menu :default-active="$route.path" router background-color="#001529" text-color="#a6adb4" active-text-color="#ffffff">
        <el-menu-item index="/"><el-icon><HomeFilled /></el-icon><span>首页</span></el-menu-item>
        <template v-if="!auth.isEngineer">
          <el-menu-item index="/chat"><el-icon><ChatDotRound /></el-icon><span>智能问答</span></el-menu-item>
          <el-menu-item index="/knowledge"><el-icon><Reading /></el-icon><span>知识库</span></el-menu-item>
          <el-menu-item index="/tickets"><el-icon><Tickets /></el-icon><span>我的工单</span></el-menu-item>
        </template>
        <template v-else>
          <el-menu-item index="/chat"><el-icon><ChatDotRound /></el-icon><span>智能问答</span></el-menu-item>
          <el-menu-item index="/knowledge"><el-icon><Reading /></el-icon><span>知识库</span></el-menu-item>
          <el-menu-item index="/manage"><el-icon><Notebook /></el-icon><span>知识管理</span></el-menu-item>
          <el-menu-item index="/review"><el-icon><Checked /></el-icon><span>审核中心</span></el-menu-item>
          <el-menu-item index="/tickets"><el-icon><Tickets /></el-icon><span>工单处理</span></el-menu-item>
          <el-menu-item v-if="auth.isAdmin" index="/admin/users"><el-icon><User /></el-icon><span>用户管理</span></el-menu-item>
          <el-menu-item v-if="auth.isAdmin" index="/admin/stats"><el-icon><DataAnalysis /></el-icon><span>统计报表</span></el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>{{ auth.isEngineer ? '内网系统（工程师）' : '公网门户（售后/试机）' }}</span>
        <el-dropdown @command="onCommand">
          <span class="user">{{ auth.user?.username }}（{{ auth.user?.role }}）<el-icon><ArrowDown /></el-icon></span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useAuthStore } from '../stores/auth'

const app = useAppStore()
const auth = useAuthStore()
const router = useRouter()

onMounted(() => { if (!app.mode) app.fetchHealth() })

function onCommand(cmd) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.aside { background: #001529; }
.logo { color: #fff; font-size: 16px; font-weight: 600; text-align: center; padding: 18px 0; }
.header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e4e7ed; }
.user { cursor: pointer; display: flex; align-items: center; gap: 4px; }
</style>
