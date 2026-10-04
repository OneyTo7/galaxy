<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAssignment } from '@/api/assignment'
import { listMySubmissions, getEvaluation } from '@/api/submission'
import { diagnose } from '@/api/diagnose'
import { ElMessage } from 'element-plus'
import type { AssignmentOut, SubmissionOut, EvaluationOut, DiagnoseOut } from '@/types/api'

const route = useRoute()
const router = useRouter()
const assignment = ref<AssignmentOut | null>(null)
const submissions = ref<SubmissionOut[]>([])
const loading = ref(false)
const selectedSubmission = ref<SubmissionOut | null>(null)
const evaluation = ref<EvaluationOut | null>(null)
const diagnosis = ref<DiagnoseOut | null>(null)
const detailLoading = ref(false)

async function load() {
  const id = Number(route.query.assignment)
  if (!id) return
  loading.value = true
  try {
    const [a, subs] = await Promise.all([getAssignment(id), listMySubmissions()])
    assignment.value = a
    submissions.value = subs.filter((s: any) => s.assignment_id === id)
    if (submissions.value.length > 0) viewSubmission(submissions.value[0])
  } catch (e) { console.error('加载失败', e) }
  finally { loading.value = false }
}

async function viewSubmission(sub: SubmissionOut) {
  selectedSubmission.value = sub
  evaluation.value = null
  diagnosis.value = null
  detailLoading.value = true
  try {
    evaluation.value = await getEvaluation(sub.id)
    try { diagnosis.value = await diagnose(sub.id) } catch {}
  } catch (e: any) { ElMessage.error(e.response?.data?.detail || '加载失败') }
  finally { detailLoading.value = false }
}

const avgScore = computed(() => {
  const done = submissions.value.filter(s => s.status === 'done')
  if (!done.length) return 0
  return Math.round(done.reduce((sum, s) => sum + s.score, 0) / done.length)
})

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <div class="page-header">
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><EditPen /></el-icon></span>
        <div>
          <h1>代码批改</h1>
          <p class="page-desc">{{ assignment?.title || '查看学生提交与 AI 诊断' }}</p>
        </div>
      </div>
      <el-button @click="router.back()"><el-icon style="margin-right:4px"><Back /></el-icon>返回</el-button>
    </div>

    <div class="split-layout">
      <aside class="sidebar rise-in" style="--enter-idx:0">
        <div class="panel">
          <div class="section-title"><span class="title-ico"><el-icon><List /></el-icon></span>提交列表</div>
          <div class="stat-mini">
            <span>总提交 {{ submissions.length }}</span>
            <span>平均分 {{ avgScore }}</span>
          </div>
          <div class="sub-list">
            <div v-for="s in submissions" :key="s.id" class="sub-item" :class="{ active: selectedSubmission?.id === s.id }" @click="viewSubmission(s)">
              <span class="sub-id">#{{ s.id }}</span>
              <el-tag :type="s.status === 'done' ? 'success' : 'warning'" size="small">{{ s.status }}</el-tag>
              <span v-if="s.status === 'done'" class="sub-score">{{ s.score }}分</span>
            </div>
          </div>
        </div>
      </aside>

      <main class="main-content">
        <div v-if="selectedSubmission" v-loading="detailLoading">
          <div class="panel rise-in" style="--enter-idx:1">
            <div class="eval-header">
              <div class="section-title" style="margin:0"><span class="title-ico"><el-icon><DataLine /></el-icon></span>提交 #{{ selectedSubmission.id }}</div>
              <el-tag :type="selectedSubmission.status === 'done' ? 'success' : 'warning'" size="small">{{ selectedSubmission.status }}</el-tag>
              <span v-if="selectedSubmission.status === 'done'" class="score-big">{{ selectedSubmission.score }}分</span>
            </div>

            <div v-if="evaluation" class="section">
              <h4>评测结果</h4>
              <div v-for="r in evaluation.results" :key="r.case_id" class="case-row" :class="{ fail: !r.passed }">
                <span class="case-icon">{{ r.passed ? '✓' : '✗' }}</span>
                <span>用例 {{ r.case_id }}</span>
                <span v-if="r.stderr" class="case-err">{{ r.stderr }}</span>
                <span class="case-time">{{ r.elapsed_ms }}ms</span>
              </div>
            </div>
          </div>

          <div v-if="diagnosis" class="panel diagnosis-card rise-in" style="--enter-idx:2">
            <div class="diag-head">
              <span class="diag-badge"><el-icon style="margin-right:4px;vertical-align:-2px"><Aim /></el-icon>AI 误区诊断</span>
              <span class="diag-conf">{{ (diagnosis.confidence * 100).toFixed(0) }}%</span>
            </div>
            <div class="diag-body">
              <div class="diag-row">
                <span class="diag-label">误区类型</span>
                <span class="diag-value primary">{{ diagnosis.misconception_type }}</span>
              </div>
              <div class="diag-row">
                <span class="diag-label">证据</span>
                <p class="diag-text">{{ diagnosis.evidence }}</p>
              </div>
              <div class="diag-row">
                <span class="diag-label">知识点</span>
                <el-tag size="small">{{ diagnosis.knowledge_point }}</el-tag>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state-v2 rise-in" style="--enter-idx:1">
          <span class="empty-ico"><el-icon><Document /></el-icon></span>
          <p>从左侧选择一条提交查看详情</p>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-lg); }

.split-layout { display: grid; grid-template-columns: 260px 1fr; gap: var(--space-lg); }

.stat-mini { display: flex; gap: var(--space-md); font-size: var(--fs-caption); color: var(--text-secondary); margin-bottom: var(--space-sm); }
.sub-list { display: flex; flex-direction: column; gap: var(--space-xs); }
.sub-item { display: flex; align-items: center; gap: var(--space-xs); padding: var(--space-xs) var(--space-sm); border-radius: var(--radius-md); cursor: pointer; transition: all var(--duration) var(--ease); }
.sub-item:hover { background: var(--bg-hover); }
.sub-item.active { background: var(--bg-hover); border-left: 3px solid var(--primary); }
.sub-id { font-weight: 700; font-size: var(--fs-body); }
.sub-score { font-weight: 700; color: var(--primary); }

.eval-header { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-md); }
.score-big { font-size: var(--fs-h2); font-weight: 700; color: var(--primary); }

.section { margin-bottom: var(--space-md); }
.case-row { display: flex; align-items: center; gap: var(--space-xs); padding: var(--space-xs) 0; border-bottom: 1px solid var(--border); font-size: var(--fs-body); }
.case-row.fail { color: var(--danger); }
.case-icon { font-weight: 700; }
.case-err { color: var(--danger); font-size: var(--fs-code); }
.case-time { margin-left: auto; color: var(--text-secondary); font-size: var(--fs-caption); }

.diagnosis-card { border-left: 3px solid var(--primary); }
.diag-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-sm); }
.diag-badge { font-size: var(--fs-caption); font-weight: 600; color: var(--primary); background: rgba(79,124,255,0.1); padding: 3px 10px; border-radius: var(--radius-sm); }
.diag-conf { font-weight: 700; font-size: var(--fs-body); color: var(--text-secondary); }
.diag-row { margin-bottom: var(--space-sm); }
.diag-label { display: block; font-size: var(--fs-caption); color: var(--text-secondary); margin-bottom: 4px; }
.diag-value { font-size: var(--fs-body); font-weight: 600; }
.diag-value.primary { color: var(--primary); font-size: var(--fs-h3); }
.diag-text { margin: 0; font-size: var(--fs-body); line-height: 1.6; }
</style>
