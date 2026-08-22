<template>
  <el-card>
    <el-form label-width="90px">
      <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
      <el-form-item label="类型">
        <el-select v-model="form.kind">
          <el-option label="问答对" value="qa" /><el-option label="文章" value="article" />
          <el-option label="故障案例" value="case" /><el-option label="代码表格" value="code" />
        </el-select>
      </el-form-item>
      <el-form-item label="分类"><el-input v-model="form.category" /></el-form-item>
      <el-form-item label="适用机型"><el-input v-model="form.machines" placeholder="如 A5/A6，逗号分隔" /></el-form-item>

      <el-form-item v-if="form.kind==='case'" label="故障现象"><el-input v-model="form.case_fields.symptom" /></el-form-item>
      <el-form-item v-if="form.kind==='case'" label="排查步骤"><el-input v-model="form.case_fields.steps" type="textarea" /></el-form-item>
      <el-form-item v-if="form.kind==='case'" label="解决方案"><el-input v-model="form.case_fields.solution" type="textarea" /></el-form-item>
      <el-form-item v-if="form.kind==='case'" label="注意事项"><el-input v-model="form.case_fields.notice" /></el-form-item>

      <el-form-item label="正文(Markdown)">
        <el-input v-model="form.body" type="textarea" :rows="12" placeholder="支持 Markdown 语法" />
      </el-form-item>
      <el-form-item label="预览">
        <div class="preview markdown-body" v-html="rendered"></div>
      </el-form-item>

      <el-form-item label="问法别名">
        <div style="width:100%">
          <el-tag v-for="(a,i) in form.aliases" :key="i" closable @close="form.aliases.splice(i,1)" style="margin:0 4px 4px 0">{{ a }}</el-tag>
          <el-input v-model="aliasInput" placeholder="输入一个问法后回车" style="width:200px" @keyup.enter="addAlias" />
        </div>
      </el-form-item>

      <el-form-item label="附件">
        <el-upload :http-request="doUpload" :show-file-list="true" :file-list="attachments">
          <el-button>上传附件（图片/视频/PDF）</el-button>
        </el-upload>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="save">保存草稿</el-button>
        <el-button @click="$router.back()">返回</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'
import http from '../../api/http'

const md = new MarkdownIt({ validateLink: (url) => /^(https?:|mailto:|#|\/)/i.test(url) })
const route = useRoute()
const router = useRouter()
const aliasInput = ref('')
const attachments = ref([])
const form = reactive({ title: '', kind: 'article', category: '', machines: '', body: '', aliases: [], case_fields: {} })
const rendered = computed(() => md.render(form.body))

function addAlias() {
  const v = aliasInput.value.trim()
  if (v && !form.aliases.includes(v)) form.aliases.push(v)
  aliasInput.value = ''
}

async function doUpload(opt) {
  const fd = new FormData()
  fd.append('file', opt.file)
  const r = await http.post(`/files?knowledge_id=${form.id}`, fd)
  attachments.value.push({ name: r.filename, uid: r.id, status: 'success' })
  ElMessage.success('已上传')
}

async function save() {
  const body = { ...form, case_fields: form.kind === 'case' ? form.case_fields : null }
  if (form.id) {
    await http.put(`/knowledge/${form.id}`, body)
  } else {
    const r = await http.post('/knowledge', body)
    form.id = r.id
  }
  ElMessage.success('已保存')
  router.push('/manage')
}

onMounted(async () => {
  if (route.params.id) {
    const r = await http.get(`/knowledge/${route.params.id}`)
    Object.assign(form, r)
    form.case_fields = r.case_fields || {}
  }
})
</script>

<style scoped>
.preview { min-height: 80px; border: 1px dashed #ddd; padding: 8px; border-radius: 4px; }
</style>
