<template>
  <el-card v-loading="loading">
    <h2>{{ item?.title }}</h2>
    <el-tag size="small">{{ item?.kind }}</el-tag>
    <el-tag size="small" type="info">{{ item?.category }}</el-tag>
    <el-tag size="small" type="warning">v{{ item?.version }}</el-tag>
    <div class="body markdown-body" v-html="rendered"></div>
  </el-card>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import MarkdownIt from 'markdown-it'
import http from '../../api/http'

const md = new MarkdownIt()
const route = useRoute()
const item = ref(null)
const loading = ref(false)
const rendered = computed(() => md.render(item.value?.body || ''))

onMounted(async () => {
  loading.value = true
  try {
    item.value = await http.get(`/knowledge/${route.params.id}`)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.body { margin-top: 16px; line-height: 1.7; }
</style>
