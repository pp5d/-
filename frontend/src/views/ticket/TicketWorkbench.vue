<template>
  <el-card>
    <el-table :data="items" border stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="question" label="问题" min-width="220" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="open(row)">答复</el-button>
          <el-button v-if="row.status==='answered'" size="small" @click="sink(row)">沉淀为知识</el-button>
          <el-button v-if="row.status!=='closed'" size="small" type="danger" @click="close(row)">关闭</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" title="答复工单" width="560px">
      <p><b>问题：</b>{{ current?.question }}</p>
      <el-input v-model="answer" type="textarea" :rows="6" placeholder="填写解决方案/排查步骤" />
      <template #footer>
        <el-button @click="dialog=false">取消</el-button>
        <el-button type="primary" @click="submitAnswer">提交答复</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const items = ref([])
const loading = ref(false)
const dialog = ref(false)
const current = ref(null)
const answer = ref('')

async function load() {
  loading.value = true
  try { items.value = await http.get('/tickets') } finally { loading.value = false }
}

function open(row) { current.value = row; answer.value = row.answer || ''; dialog.value = true }

async function submitAnswer() {
  await http.post(`/tickets/${current.value.id}/answer`, { answer: answer.value })
  ElMessage.success('已答复')
  dialog.value = false
  load()
}

async function close(row) {
  try {
    await ElMessageBox.confirm('确定关闭该工单？', '提示', { type: 'warning' })
  } catch {
    return
  }
  await http.post(`/tickets/${row.id}/close`)
  ElMessage.success('已关闭')
  load()
}

async function sink(row) {
  await http.post(`/tickets/${row.id}/to-knowledge`)
  ElMessage.success('已沉淀为知识草稿，请在知识管理中完善后发布')
  load()
}

onMounted(load)
</script>
