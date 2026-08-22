<template>
  <div class="login-wrap">
    <el-card class="login-card">
      <h2 style="text-align:center">注塑机上位机智能问答</h2>
      <el-tabs v-model="tab">
        <el-tab-pane label="登录" name="login">
          <el-form @submit.prevent="doLogin">
            <el-form-item><el-input v-model="form.username" placeholder="用户名" /></el-form-item>
            <el-form-item><el-input v-model="form.password" type="password" placeholder="密码" show-password /></el-form-item>
            <el-button type="primary" style="width:100%" :loading="loading" @click="doLogin">登 录</el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form @submit.prevent="doRegister">
            <el-form-item><el-input v-model="form.username" placeholder="用户名" /></el-form-item>
            <el-form-item><el-input v-model="form.phone" placeholder="手机号" /></el-form-item>
            <el-form-item><el-input v-model="form.password" type="password" placeholder="密码（至少6位）" show-password /></el-form-item>
            <el-button type="primary" style="width:100%" :loading="loading" @click="doRegister">注 册</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const tab = ref('login')
const form = ref({ username: '', password: '', phone: '' })
const loading = ref(false)
const auth = useAuthStore()
const router = useRouter()

async function doLogin() {
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}

async function doRegister() {
  loading.value = true
  try {
    await auth.register(form.value.username, form.value.password, form.value.phone)
    ElMessage.success('注册成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f7fa; }
.login-card { width: 380px; padding: 12px 8px; }
</style>
