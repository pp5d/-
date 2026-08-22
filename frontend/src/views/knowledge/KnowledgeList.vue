<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="$router.push('/manage/edit')">新建知识</el-button>
      <el-select v-model="fKind" placeholder="类型" clearable style="width:120px">
        <el-option label="问答对" value="qa" /><el-option label="文章" value="article" />
        <el-option label="故障案例" value="case" /><el-option label="代码表格" value="code" />
      </el-select>
      <el-select v-model="fStatus" placeholder="状态" clearable style="width:120px">
        <el-option label="草稿" value="draft" /><el-option label="待审核" value="pending" />
        <el-option label="已发布" value="published" /><el-option label="已归档" value="archived" />
      </el-select>
      <el-button @click="load">查询</el-button>
    </div>
    <el-table :data="items" border stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column prop="kind" label="类型" width="100" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="category" label="分类" width="110" />
      <el-table-column prop="version" label="版本" width="70" />
      <el-table-column label="操作" width="280">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/manage/edit/${row.id}`)">编辑</el-button>
          <el-button v-if="row.status==='draft'" size="small" type="primary" @click="submit(row)">提交审核</el-button>
          <el-button v-if="row.status==='published'" size="small" @click="togglePub(row)">{{ row.publish_to_public ? '取消公网' : '发布公网' }}</el-button>
          <el-button v-if="row.status==='draft'" size="small" type="danger" @click="del(row)">删除</el-button>
          <el-button v-if="row.status==='published'" size="small" type="warning" @click="archive(row)">下架</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const items = ref([])
const loading = ref(false)
const fKind = ref('')
const fStatus = ref('')

async function load() {
  loading.value = true
  try {
    const params = {}
    if (fKind.value) params.kind = fKind.value
    if (fStatus.value) params.status = fStatus.value
    items.value = await http.get('/knowledge', { params })
  } finally {
    loading.value = false
  }
}

async function submit(row) {
  await http.post(`/knowledge/${row.id}/submit`)
  ElMessage.success('已提交审核')
  load()
}
async function togglePub(row) {
  await http.post(`/knowledge/${row.id}/publish-toggle`)
  ElMessage.success('已切换')
  load()
}
async function archive(row) {
  await ElMessageBox.confirm(`确定下架「${row.title}」吗？下架后售后和公网将看不到此知识。`, '下架确认', { type: 'warning' }).catch(() => {})
  await http.post(`/knowledge/${row.id}/archive`)
  ElMessage.success('已下架')
  load()
}
async function del(row) {
  await ElMessageBox.confirm(`确定删除草稿「${row.title}」吗？删除后不可恢复。`, '删除确认', { type: 'warning' }).catch(() => {})
  await http.delete(`/knowledge/${row.id}`)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; display: flex; gap: 8px; }
</style>
