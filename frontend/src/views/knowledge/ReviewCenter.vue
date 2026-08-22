<template>
  <el-card>
    <el-table :data="items" border stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column prop="kind" label="类型" width="100" />
      <el-table-column prop="category" label="分类" width="110" />
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" @click="open(row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" title="审核" width="640px">
      <h3>{{ current?.title }}</h3>
      <div class="body markdown-body" v-html="rendered"></div>
      <el-input v-model="comment" type="textarea" placeholder="审核意见（退回时必填）" />
      <template #footer>
        <el-button @click="doReview(false)" :disabled="!comment">退回</el-button>
        <el-button type="primary" @click="doReview(true)">通过</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'
import http from '../../api/http'

const md = new MarkdownIt({ validateLink: (url) => /^(https?:|mailto:|#|\/)/i.test(url) })
const items = ref([])
const loading = ref(false)
const dialog = ref(false)
const current = ref(null)
const comment = ref('')
const rendered = computed(() => md.render(current.value?.body || ''))

async function load() {
  loading.value = true
  try {
    items.value = await http.get('/knowledge', { params: { status: 'pending' } })
  } finally {
    loading.value = false
  }
}

function open(row) {
  current.value = row
  comment.value = ''
  dialog.value = true
}

async function doReview(approve) {
  await http.post(`/knowledge/${current.value.id}/review`, { approve, comment: comment.value })
  ElMessage.success(approve ? '已通过' : '已退回')
  dialog.value = false
  load()
}

onMounted(load)
</script>

<style scoped>
.body { max-height: 320px; overflow: auto; border: 1px solid #eee; padding: 8px; }
</style>
