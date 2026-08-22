<template>
  <el-card>
    <h2>欢迎，{{ auth.user?.username }}</h2>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="系统模式">{{ auth.isEngineer ? '内网系统' : '公网门户' }}</el-descriptions-item>
      <el-descriptions-item label="角色">{{ auth.user?.role }}</el-descriptions-item>
      <el-descriptions-item label="说明">
        {{ auth.isEngineer ? '工程师入口：知识管理、审核、工单处理。' : '售后/试机人员入口：智能问答、知识库、我的工单。' }}
      </el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>
