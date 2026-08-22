<template>
  <el-card>
    <div class="toolbar">
      <el-input v-model="q" placeholder="搜索标题" clearable style="width:220px" @keyup.enter="load" />
      <el-button @click="load">搜索</el-button>
    </div>
    <el-table :data="items" border stripe v-loading="loading" @row-click="(r)=>$router.push(`/knowledge/${r.id}`)">
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="kind" label="类型" width="100" />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column prop="machines" label="适用机型" width="120" />
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from '../../api/http'

const items = ref([])
const loading = ref(false)
const q = ref('')

async function load() {
  loading.value = true
  try {
    const params = {}
    if (q.value) params.q = q.value
    items.value = await http.get('/knowledge', { params })
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; display: flex; gap: 8px; }
</style>
