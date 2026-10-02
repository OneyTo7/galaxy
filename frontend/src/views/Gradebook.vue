<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { generateGradebook, getGradebook } from '@/api/grade'
import { ElMessage } from 'element-plus'
import type { GradeOut } from '@/types/api'

const route = useRoute()
const assignmentId = ref(Number(route.query.assignment) || 2)
const grades = ref<GradeOut[]>([])
const loading = ref(false)

async function handleGenerate() {
  loading.value = true
  try {
    await generateGradebook(assignmentId.value)
    ElMessage.success('成绩册已生成')
    loadGrades()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '生成失败')
  } finally {
    loading.value = false
  }
}

async function loadGrades() {
  try {
    grades.value = await getGradebook(assignmentId.value)
  } catch (e) {
    console.error('加载成绩册失败', e)
  }
}
</script>

<template>
  <div class="gradebook-page">
    <h1>成绩册</h1>
    <div class="form-bar">
      <span>作业 ID</span>
      <el-input-number v-model="assignmentId" :min="1" />
      <el-button type="primary" :loading="loading" @click="handleGenerate">生成成绩册</el-button>
      <el-button @click="loadGrades">刷新</el-button>
    </div>
    <el-table v-if="grades.length" :data="grades" border>
      <el-table-column prop="student_id" label="学生 ID" width="100" />
      <el-table-column prop="final_score" label="最终成绩" width="100" />
      <el-table-column prop="status" label="状态" width="100" />
    </el-table>
  </div>
</template>

<style scoped>
.gradebook-page { max-width: 800px; }
.form-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
</style>
