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

const detailAssignment = ref<AssignmentOut | null>(null)
const detailVisible = ref(false)

function showDetail(a: AssignmentOut) {
  detailAssignment.value = a
  detailVisible.value = true
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
          <el-button size="small" @click="showDetail(a)">查看详情</el-button>
          <el-button v-if="auth.role === 'teacher' && a.status !== 'published'" type="primary" size="small" @click="handlePublish(a.id)">发布</el-button>
          <el-button v-if="auth.role === 'teacher'" type="danger" size="small" @click="handleDelete(a.id)">删除</el-button>
          <el-button v-if="auth.role === 'student'" type="primary" size="small" @click="goToSubmit(a.id)">去做</el-button>
        </div>
      </div>
    </div>

    <el-dialog v-model="detailVisible" :title="detailAssignment?.title" width="700px" top="5vh">
      <div v-if="detailAssignment" class="detail-content">
        <div class="detail-meta">
          <el-tag size="small">语言 {{ detailAssignment.lang }}</el-tag>
          <el-tag size="small" type="info">{{ detailAssignment.test_cases?.length || 0 }} 个用例</el-tag>
          <el-tag v-if="auth.role === 'teacher'" size="small" :type="detailAssignment.status === 'published' ? 'success' : 'warning'">
            {{ detailAssignment.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </div>
        <div class="detail-section">
          <h4>题目描述</h4>
          <p class="detail-text">{{ detailAssignment.description }}</p>
        </div>
        <div v-if="detailAssignment.test_cases?.length" class="detail-section">
          <h4>测试用例</h4>
          <div v-for="tc in detailAssignment.test_cases" :key="tc.id" class="detail-case">
            <span class="case-tag">{{ tc.is_hidden ? '🔒 隐藏' : '👁 公开' }}</span>
            <span class="case-name">{{ tc.name || '用例 ' + tc.id }}</span>
            <pre>输入: {{ tc.input }}</pre>
            <pre>期望: {{ tc.expected_output }}</pre>
          </div>
        </div>
        <div v-if="detailAssignment.scoring_rubric" class="detail-section">
          <h4>评分细则</h4>
          <p class="detail-text">{{ detailAssignment.scoring_rubric }}</p>
        </div>
        <div v-if="detailAssignment.reference_code && auth.role === 'teacher'" class="detail-section">
          <h4>参考实现</h4>
          <pre class="ref-code">{{ detailAssignment.reference_code }}</pre>
        </div>
      </div>
      <template #footer>
        <el-button v-if="auth.role === 'student'" type="primary" @click="goToSubmit(detailAssignment!.id); detailVisible = false">去做这道题</el-button>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
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

.detail-content { max-height: 70vh; overflow-y: auto; }
.detail-meta { display: flex; gap: 8px; margin-bottom: 20px; }
.detail-section { margin-bottom: 24px; }
.detail-section h4 { font-size: 15px; margin: 0 0 10px; }
.detail-text { color: var(--galaxy-text-secondary); white-space: pre-wrap; line-height: 1.7; font-size: 14px; }
.detail-case { background: var(--galaxy-bg); border-radius: 6px; padding: 10px 12px; margin-bottom: 8px; }
.case-tag { font-size: 12px; color: var(--galaxy-text-secondary); margin-right: 8px; }
.case-name { font-weight: 500; font-size: 14px; }
.detail-case pre { margin: 6px 0 0; font-family: 'JetBrains Mono'; font-size: 12px; color: var(--galaxy-text-secondary); }
.ref-code { background: var(--galaxy-bg); border-radius: 6px; padding: 12px; font-family: 'JetBrains Mono'; font-size: 13px; overflow-x: auto; }
</style>
