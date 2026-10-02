<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { listAssignments, listPublished, publishAssignment, deleteAssignment } from '@/api/assignment'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { AssignmentOut } from '@/types/api'

const auth = useAuthStore()
const router = useRouter()
const assignments = ref<AssignmentOut[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    if (auth.role === 'teacher') {
      assignments.value = await listAssignments()
    } else {
      assignments.value = await listPublished()
    }
  } catch (e) {
    console.error('加载作业失败', e)
  } finally {
    loading.value = false
  }
}

async function handlePublish(id: number) {
  try {
    await publishAssignment(id)
    ElMessage.success('作业已发布，学生现在可以提交')
    load()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '发布失败')
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确认删除此作业？', '提示')
    await deleteAssignment(id)
    ElMessage.success('已删除')
    load()
  } catch {}
}

function goToSubmit(assignmentId: number) {
  router.push(`/submit?assignment=${assignmentId}`)
}

onMounted(load)
</script>

<template>
  <div class="assignment-list">
    <div class="header">
      <h1>{{ auth.role === 'teacher' ? '我的作业' : '可提交的作业' }}</h1>
      <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/assignment-generate')">AI 命题</el-button>
    </div>
    <p class="desc" v-if="auth.role === 'teacher'">AI 生成的作业默认为草稿，点击「发布」后学生可见。</p>
    <p class="desc" v-else>点击「去做」进入代码编辑器提交作业。</p>
    <div v-if="!loading && assignments.length === 0" class="empty">
      <p>暂无作业</p>
    </div>
    <div class="cards">
      <div v-for="a in assignments" :key="a.id" class="card">
        <div class="card-header">
          <h3>{{ a.title }}</h3>
          <el-tag v-if="auth.role === 'teacher'" :type="a.status === 'published' ? 'success' : 'info'" size="small">
            {{ a.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </div>
        <p class="card-desc">{{ a.description.substring(0, 120) }}{{ a.description.length > 120 ? '...' : '' }}</p>
        <div class="card-meta">
          <span>语言 {{ a.lang }}</span>
          <span>{{ a.test_cases?.length || 0 }} 个用例</span>
        </div>
        <div class="card-actions">
          <el-button v-if="auth.role === 'teacher' && a.status !== 'published'" type="primary" size="small" @click="handlePublish(a.id)">发布</el-button>
          <el-button v-if="auth.role === 'teacher'" type="danger" size="small" @click="handleDelete(a.id)">删除</el-button>
          <el-button v-if="auth.role === 'student'" type="primary" size="small" @click="goToSubmit(a.id)">去做</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.assignment-list { max-width: 1000px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.desc { color: var(--galaxy-text-secondary); margin-bottom: 24px; }
.empty { text-align: center; padding: 60px 0; color: var(--galaxy-text-secondary); }
.cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.card { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: 8px; padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.card-header h3 { margin: 0; font-size: 16px; }
.card-desc { color: var(--galaxy-text-secondary); font-size: 14px; line-height: 1.6; margin: 0 0 12px; }
.card-meta { display: flex; gap: 16px; font-size: 13px; color: var(--galaxy-text-secondary); margin-bottom: 16px; }
.card-actions { display: flex; gap: 8px; }
</style>
