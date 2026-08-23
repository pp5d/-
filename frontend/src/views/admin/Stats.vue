<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="6" v-for="c in cards" :key="c.label">
        <el-card><div class="num">{{ c.value }}</div><div class="lbl">{{ c.label }}</div></el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:16px">
      <template #header>
        <span>高频问题 Top</span>
        <el-button type="primary" size="small" style="float:right" @click="sync">同步到公网</el-button>
      </template>
      <el-table :data="topQuestions" border stripe>
        <el-table-column prop="question" label="问题" min-width="260" show-overflow-tooltip />
        <el-table-column prop="count" label="次数" width="100" />
      </el-table>
    </el-card>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card header="知识利用率 Top">
          <el-table :data="knowledgeUsage" border stripe>
            <el-table-column prop="title" label="知识" min-width="180" show-overflow-tooltip />
            <el-table-column prop="view_count" label="引用次数" width="100" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="工单概况">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="已答复工单">{{ ticketResp.answered_count }}</el-descriptions-item>
            <el-descriptions-item label="平均响应时长">{{ Math.round(ticketResp.avg_response_seconds / 60) }} 分钟</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const overview = ref({})
const topQuestions = ref([])
const knowledgeUsage = ref([])
const ticketResp = ref({})

const cards = computed(() => [
  { label: '知识总数', value: overview.value.knowledge_total ?? 0 },
  { label: '已发布知识', value: overview.value.knowledge_published ?? 0 },
  { label: '待审核', value: overview.value.knowledge_pending ?? 0 },
  { label: '未答复工单', value: overview.value.ticket_open ?? 0 },
])

async function load() {
  overview.value = await http.get('/stats/overview')
  topQuestions.value = await http.get('/stats/top-questions')
  knowledgeUsage.value = await http.get('/stats/knowledge-usage')
  ticketResp.value = await http.get('/stats/ticket-response')
}

async function sync() {
  try {
    const r = await http.post('/sync/push')
    ElMessage.success(`同步成功，共 ${r.count} 条知识`)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '同步失败，请确认已配置公网地址')
  }
}

onMounted(load)
</script>

<style scoped>
.num { font-size: 28px; font-weight: 700; }
.lbl { color: #888; margin-top: 4px; }
</style>
