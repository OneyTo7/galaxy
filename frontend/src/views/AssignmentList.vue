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
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><Document /></el-icon></span>
        <div>
          <h1>{{ auth.role === 'teacher' ? '我的作业' : '可提交的作业' }}</h1>
          <p class="page-desc" v-if="auth.role === 'teacher'">AI 生成的作业默认为草稿，点击「发布」后学生可见。</p>
          <p class="page-desc" v-else>点击「去做」进入代码编辑器提交作业。</p>
        </div>
      </div>
      <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/assignment-generate')">
        <el-icon style="margin-right: 4px"><MagicStick /></el-icon>AI 命题
      </el-button>
    </div>

    <div v-if="!loading && assignments.length === 0" class="empty-state-v2 rise-in" style="--enter-idx:0">
      <div class="empty-ico"><el-icon><Document /></el-icon></div>
      <p>暂无作业</p>
    </div>

    <div class="cards-grid">
      <div v-for="(a, idx) in assignments" :key="a.id" class="panel assign-card rise-in" :style="{ '--enter-idx': idx }">
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
          <el-button size="small" @click="showDetail(a)">
            <el-icon style="margin-right: 4px"><View /></el-icon>查看详情
          </el-button>
          <el-button v-if="auth.role === 'teacher' && a.status !== 'published'" type="primary" size="small" @click="handlePublish(a.id)">
            <el-icon style="margin-right: 4px"><Promotion /></el-icon>发布
          </el-button>
          <el-button v-if="auth.role === 'teacher'" type="danger" size="small" @click="handleDelete(a.id)">
            <el-icon style="margin-right: 4px"><Delete /></el-icon>删除
          </el-button>
          <el-button v-if="auth.role === 'student'" type="primary" size="small" @click="goToSubmit(a.id)">
            <el-icon style="margin-right: 4px"><Edit /></el-icon>去做
          </el-button>
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
          <div class="section-title"><span class="title-ico"><el-icon><Document /></el-icon></span>题目描述</div>
          <p class="detail-text">{{ detailAssignment.description }}</p>
        </div>
        <div v-if="detailAssignment.test_cases?.length" class="detail-section">
          <div class="section-title"><span class="title-ico"><el-icon><List /></el-icon></span>测试用例</div>
          <div v-for="tc in detailAssignment.test_cases" :key="tc.id" class="detail-case">
            <span class="case-tag">{{ tc.is_hidden ? '🔒 隐藏' : '👁 公开' }}</span>
            <span class="case-name">{{ tc.name || '用例 ' + tc.id }}</span>
            <pre>输入: {{ tc.input }}</pre>
            <pre>期望: {{ tc.expected_output }}</pre>
          </div>
        </div>
        <div v-if="detailAssignment.scoring_rubric" class="detail-section">
          <div class="section-title"><span class="title-ico"><el-icon><Histogram /></el-icon></span>评分细则</div>
          <p class="detail-text">{{ detailAssignment.scoring_rubric }}</p>
        </div>
        <div v-if="detailAssignment.reference_code && auth.role === 'teacher'" class="detail-section">
          <div class="section-title"><span class="title-ico"><el-icon><Reading /></el-icon></span>参考实现</div>
          <pre class="ref-code">{{ detailAssignment.reference_code }}</pre>
        </div>
      </div>
      <template #footer>
        <el-button v-if="auth.role === 'student'" type="primary" @click="goToSubmit(detailAssignment!.id); detailVisible = false">
          <el-icon style="margin-right: 4px"><Edit /></el-icon>去做这道题
        </el-button>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>

.cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-md); }
.assign-card { display: flex; flex-direction: column; }
.card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-xs); }
.card-head h3 { margin: 0; font-size: var(--fs-h3); color: var(--ink); }
.card-desc { color: var(--text-secondary); font-size: var(--fs-body); line-height: 1.6; margin: 0 0 var(--space-sm); flex: 1; }
.card-meta { display: flex; gap: var(--space-md); font-size: var(--fs-caption); color: var(--text-placeholder); margin-bottom: var(--space-sm); }
.card-actions { display: flex; gap: var(--space-xs); flex-wrap: wrap; }

.detail-meta { display: flex; gap: var(--space-xs); margin-bottom: var(--space-md); }
.detail-section { margin-bottom: var(--space-md); }
.detail-text { color: var(--text-secondary); white-space: pre-wrap; line-height: 1.6; font-size: var(--fs-body); }
.detail-case { background: var(--bg-page); border-radius: var(--radius-md); padding: var(--space-sm); margin-bottom: var(--space-xs); }
.case-tag { font-size: var(--fs-caption); color: var(--text-secondary); margin-right: var(--space-xs); }
.case-name { font-weight: 500; font-size: var(--fs-body); }
.detail-case pre { margin: var(--space-xs) 0 0; font-size: var(--fs-code); color: var(--text-secondary); }
.ref-code { background: var(--bg-page); border-radius: var(--radius-md); padding: var(--space-sm); font-size: var(--fs-code); overflow-x: auto; }

@media (max-width: 768px) { .cards-grid { grid-template-columns: 1fr; } }
</style>
