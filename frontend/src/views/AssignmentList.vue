<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
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
  } catch (e) { console.error('加载作业失败', e) }
  finally { loading.value = false }
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
  <div class="page">
    <div class="page-header">
      <div>
        <h1>{{ auth.role === 'teacher' ? '我的作业' : '可提交的作业' }}</h1>
        <p class="page-desc" v-if="auth.role === 'teacher'">AI 生成的作业默认为草稿，点击「发布」后学生可见。</p>
        <p class="page-desc" v-else>点击「去做」进入代码编辑器提交作业。</p>
      </div>
      <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/assignment-generate')">AI 命题</el-button>
    </div>

    <div v-if="!loading && assignments.length === 0" class="empty-state">
      <p class="empty-text">暂无作业</p>
    </div>

    <div class="cards-grid">
      <div v-for="a in assignments" :key="a.id" class="assign-card">
        <div class="card-head">
          <h3>{{ a.title }}</h3>
          <el-tag v-if="auth.role === 'teacher'" :type="a.status === 'published' ? 'success' : 'info'" size="small">
            {{ a.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </div>
        <p class="card-desc">{{ a.description.substring(0, 120) }}{{ a.description.length > 120 ? '...' : '' }}</p>
        <div class="card-meta">
          <span>{{ a.lang }}</span>
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
          <el-tag size="small">{{ detailAssignment.lang }}</el-tag>
          <el-tag size="small" type="info">{{ detailAssignment.test_cases?.length || 0 }} 个用例</el-tag>
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
.page { max-width: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-lg); }
.page-desc { margin: 0; font-size: var(--fs-body); color: var(--text-secondary); }

.empty-state { text-align: center; padding: var(--space-xl) 0; color: var(--text-secondary); }

.cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-md); }
.assign-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-md); transition: all var(--duration) var(--ease); }
.assign-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-2px); }
.card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-xs); }
.card-head h3 { margin: 0; font-size: var(--fs-h3); }
.card-desc { color: var(--text-secondary); font-size: var(--fs-body); line-height: 1.6; margin: 0 0 var(--space-sm); }
.card-meta { display: flex; gap: var(--space-md); font-size: var(--fs-caption); color: var(--text-placeholder); margin-bottom: var(--space-sm); }
.card-actions { display: flex; gap: var(--space-xs); }

.detail-meta { display: flex; gap: var(--space-xs); margin-bottom: var(--space-md); }
.detail-section { margin-bottom: var(--space-md); }
.detail-section h4 { font-size: var(--fs-h3); font-weight: 500; margin: 0 0 var(--space-xs); }
.detail-text { color: var(--text-secondary); white-space: pre-wrap; line-height: 1.6; font-size: var(--fs-body); }
.detail-case { background: var(--bg-page); border-radius: var(--radius-md); padding: var(--space-sm); margin-bottom: var(--space-xs); }
.case-tag { font-size: var(--fs-caption); color: var(--text-secondary); margin-right: var(--space-xs); }
.case-name { font-weight: 500; font-size: var(--fs-body); }
.detail-case pre { margin: var(--space-xs) 0 0; font-size: var(--fs-code); color: var(--text-secondary); }
.ref-code { background: var(--bg-page); border-radius: var(--radius-md); padding: var(--space-sm); font-size: var(--fs-code); overflow-x: auto; }

@media (max-width: 768px) { .cards-grid { grid-template-columns: 1fr; } }
</style>
