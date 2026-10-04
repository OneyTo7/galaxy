<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { generateGradebook, getGradebook } from '@/api/grade'
import { listAssignments } from '@/api/assignment'
import { ElMessage } from 'element-plus'
import type { GradeOut, AssignmentOut } from '@/types/api'

const assignments = ref<AssignmentOut[]>([])
const selectedId = ref<number | null>(null)
const grades = ref<GradeOut[]>([])
const loading = ref(false)

async function loadAssignments() {
  try { assignments.value = await listAssignments() } catch (e) { console.error('加载作业失败', e) }
}

async function handleGenerate() {
  if (!selectedId.value) return
  loading.value = true
  try {
    await generateGradebook(selectedId.value)
    ElMessage.success('成绩册已生成')
    loadGrades()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '生成失败')
  } finally {
    loading.value = false
  }
}

async function loadGrades() {
  if (!selectedId.value) return
  try { grades.value = await getGradebook(selectedId.value) } catch (e) { console.error('加载成绩册失败', e) }
}

watch(selectedId, loadGrades)
onMounted(loadAssignments)
</script>

<template>
  <div class="page gradebook-page">
    <div class="page-header">
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><DataAnalysis /></el-icon></span>
        <div>
          <h1>成绩册</h1>
          <p class="page-desc">选择作业，聚合学生最高分生成成绩册。</p>
        </div>
      </div>
    </div>

    <div class="panel action-bar rise-in" style="--enter-idx:0">
      <el-select v-model="selectedId" placeholder="选择作业" style="width: 400px" :loading="loading">
        <el-option v-for="a in assignments" :key="a.id" :label="a.title" :value="a.id" />
      </el-select>
      <el-button type="primary" :loading="loading" @click="handleGenerate"><el-icon style="margin-right:4px"><Promotion /></el-icon>生成成绩册</el-button>
      <el-button @click="loadGrades"><el-icon style="margin-right:4px"><Refresh /></el-icon>刷新</el-button>
    </div>

    <div v-if="!selectedId && assignments.length === 0" class="empty-state-v2 rise-in" style="--enter-idx:1">
      <span class="empty-ico"><el-icon><Document /></el-icon></span>
      <p>暂无作业</p>
    </div>
    <div v-if="selectedId && !loading && grades.length === 0" class="empty-state-v2 rise-in" style="--enter-idx:1">
      <span class="empty-ico"><el-icon><Document /></el-icon></span>
      <p>暂无成绩数据，点击「生成成绩册」</p>
    </div>
    <el-table v-if="grades.length" :data="grades" border stripe class="rise-in" style="--enter-idx:2">
      <el-table-column prop="student_id" label="学生 ID" width="100" />
      <el-table-column prop="final_score" label="最终成绩" width="100">
        <template #default="{ row }">
          <span :class="{ high: row.final_score >= 80, low: row.final_score < 60 }" class="score-cell">{{ row.final_score }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" />
    </el-table>
  </div>
</template>

<style scoped>
.gradebook-page { max-width: 800px; }
.action-bar { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-lg); }
.score-cell { font-weight: 700; }
.score-cell.high { color: var(--success); }
.score-cell.low { color: var(--danger); }
</style>
