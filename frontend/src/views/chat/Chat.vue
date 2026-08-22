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
          <div v-if="m.hit === false" class="miss">⚠️ 未命中：问题已记录，工程师会尽快补充知识。</div>
        </div>
      </div>
      <div v-if="loading" class="msg assistant"><div class="bubble">思考中…</div></div>
    </div>
    <div class="input-row">
      <el-input v-model="question" placeholder="描述你的问题，如：E012 报警怎么处理" @keyup.enter="send" :disabled="loading" />
      <el-button type="primary" @click="send" :loading="loading">发送</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import http from '../../api/http'

const messages = ref([{ role: 'assistant', text: '你好！我是注塑机上位机智能助手，请描述你遇到的问题。' }])
const question = ref('')
const loading = ref(false)
const msgBox = ref(null)

async function send() {
  const q = question.value.trim()
  if (!q || loading.value) return
  messages.value.push({ role: 'user', text: q })
  question.value = ''
  loading.value = true
  try {
    const r = await http.post('/qa', { question: q })
    messages.value.push({ role: 'assistant', text: r.answer, sources: r.sources, hit: r.hit })
  } catch (e) {
    messages.value.push({ role: 'assistant', text: '请求失败，请稍后重试。' })
  } finally {
    loading.value = false
    nextTick(() => { msgBox.value && (msgBox.value.scrollTop = msgBox.value.scrollHeight) })
  }
}

onMounted(() => {})
</script>

<style scoped>
.chat-card { height: calc(100vh - 140px); display: flex; flex-direction: column; }
.messages { flex: 1; overflow-y: auto; padding: 8px; }
.msg { display: flex; margin-bottom: 12px; }
.msg.user { justify-content: flex-end; }
.bubble { max-width: 80%; padding: 10px 14px; border-radius: 8px; background: #f0f2f5; white-space: pre-wrap; }
.msg.user .bubble { background: #d9ecff; }
.sources { margin-top: 8px; font-size: 12px; color: #666; }
.miss { margin-top: 6px; color: #e6a23c; font-size: 12px; }
.input-row { display: flex; gap: 8px; margin-top: 12px; }
</style>
