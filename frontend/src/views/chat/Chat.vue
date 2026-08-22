<template>
  <el-card class="chat-card">
    <div class="messages" ref="msgBox">
      <div v-for="(m, i) in messages" :key="i" :class="['msg', m.role]">
        <div class="bubble">
          <div class="text">{{ m.text }}</div>
          <div v-if="m.sources && m.sources.length" class="sources">
            参考来源：
            <el-tag v-for="s in m.sources" :key="s.id" size="small" style="margin-right:4px" @click="$router.push(`/knowledge/${s.id}`)">{{ s.title }}</el-tag>
          </div>
          <div v-if="m.question" class="miss-actions">
            <el-button size="small" type="primary" plain :disabled="loading" @click="freeAnswer(i)">用 AI 通用知识回答</el-button>
            <el-button size="small" :disabled="loading" @click="toEngineer">转给工程师处理</el-button>
          </div>
        </div>
      </div>
      <div v-if="loading" class="msg assistant"><div class="bubble">思考中…</div></div>
    </div>
    <div class="input-row">
      <el-input v-model="question" placeholder="描述你的问题，如：E012 报警怎么处理" @keyup.enter="send" :disabled="loading" />
      <el-button type="primary" @click="send" :loading="loading">发送</el-button>
      <el-button @click="clear">清空</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const STORAGE_KEY = 'aiqa_chat_history'
const MAX_MESSAGES = 30
const DEFAULT_WELCOME = { role: 'assistant', text: '你好！我是注塑机上位机智能助手，请描述你遇到的问题。' }

const messages = ref([{ ...DEFAULT_WELCOME }])
const question = ref('')
const loading = ref(false)
const msgBox = ref(null)

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.value.slice(-MAX_MESSAGES)))
  } catch (e) {
    /* ignore */
  }
}

async function send() {
  const q = question.value.trim()
  if (!q || loading.value) return
  messages.value.push({ role: 'user', text: q })
  question.value = ''
  loading.value = true
  try {
    const r = await http.post('/qa', { question: q })
    const msg = { role: 'assistant', text: r.answer, sources: r.sources, hit: r.hit }
    if (r.hit === false && !(r.sources && r.sources.length)) {
      msg.question = q
    }
    messages.value.push(msg)
  } catch (e) {
    messages.value.push({ role: 'assistant', text: '请求失败，请稍后重试。' })
  } finally {
    loading.value = false
    persist()
    nextTick(() => { msgBox.value && (msgBox.value.scrollTop = msgBox.value.scrollHeight) })
  }
}

async function freeAnswer(i) {
  const m = messages.value[i]
  const q = m && m.question
  if (!q || loading.value) return
  loading.value = true
  try {
    const r = await http.post('/qa', { question: q, allow_free: true })
    messages.value.push({ role: 'assistant', text: r.answer, hit: false, sources: [] })
    m.question = ''
  } catch (e) {
    messages.value.push({ role: 'assistant', text: '请求失败，请稍后重试。' })
  } finally {
    loading.value = false
    persist()
    nextTick(() => { msgBox.value && (msgBox.value.scrollTop = msgBox.value.scrollHeight) })
  }
}

function toEngineer() {
  ElMessage.info('工单功能将在后续版本上线，请先联系工程师处理。')
}

function clear() {
  messages.value = [{ ...DEFAULT_WELCOME }]
  localStorage.removeItem(STORAGE_KEY)
}

onMounted(() => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const arr = JSON.parse(raw)
      if (Array.isArray(arr) && arr.length) {
        messages.value = arr.slice(-MAX_MESSAGES)
        nextTick(() => { msgBox.value && (msgBox.value.scrollTop = msgBox.value.scrollHeight) })
      }
    }
  } catch (e) {
    /* ignore */
  }
})
</script>

<style scoped>
.chat-card { height: calc(100vh - 140px); display: flex; flex-direction: column; }
.messages { flex: 1; overflow-y: auto; padding: 8px; }
.msg { display: flex; margin-bottom: 12px; }
.msg.user { justify-content: flex-end; }
.bubble { max-width: 80%; padding: 10px 14px; border-radius: 8px; background: #f0f2f5; white-space: pre-wrap; }
.msg.user .bubble { background: #d9ecff; }
.sources { margin-top: 8px; font-size: 12px; color: #666; }
.miss-actions { margin-top: 8px; display: flex; gap: 8px; }
.input-row { display: flex; gap: 8px; margin-top: 12px; }
</style>
