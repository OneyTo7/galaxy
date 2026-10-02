<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listMySubmissions, getEvaluation } from '@/api/submission'
import { getAssignment } from '@/api/assignment'
import type { SubmissionOut, EvaluationOut, AssignmentOut } from '@/types/api'

const router = useRouter()
const submissions = ref<SubmissionOut[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    submissions.value = await listMySubmissions()
  } catch (e) {
    console.error('加载提交失败', e)
  } finally {
    loading.value = false
  }
}

function goToDiagnose(id: number) { router.push(`/diagnose?submission=${id}`) }
function goToVariant(id: number) { router.push(`/variant?submission=${id}`) }
function goToAppeal(id: number) { router.push(`/appeal?submission=${id}`) }

const detailVisible = ref(false)
const detailEval = ref<EvaluationOut | null>(null)
const detailAssignment = ref<AssignmentOut | null>(null)
const detailLoading = ref(false)

async function showDetail(s: SubmissionOut) {
  detailVisible.value = true
  detailEval.value = null
  detailAssignment.value = null
  detailLoading.value = true
  try {
    detailEval.value = await getEvaluation(s.id)
    detailAssignment.value = await getAssignment(s.assignment_id)
  } catch (e) {
    console.error('加载详情失败', e)
  } finally {
    detailLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="submissions-page">
    <div class="header">
      <h1>我的提交</h1>
      <p class="desc">查看你的提交记录，点击操作进行误区诊断、变式练习或申诉。</p>
    </div>

    <div v-if="!loading && submissions.length === 0" class="empty">
      <p class="empty-text">暂无提交记录</p>
      <el-button type="primary" @click="router.push('/assignments')">去做作业</el-button>
    </div>

    <div v-else class="list">
      <div v-for="s in submissions" :key="s.id" class="sub-card">
        <div class="sub-info">
          <span class="sub-id">#{{ s.id }}</span>
          <span class="sub-assign">作业 {{ s.assignment_id }}</span>
          <el-tag :type="s.status === 'done' ? 'success' : 'warning'" size="small">{{ s.status }}</el-tag>
          <span v-if="s.status === 'done'" class="sub-score">{{ s.score }}分</span>
        </div>
        <div class="sub-actions">
          <el-button size="small" @click="showDetail(s)">详情</el-button>
          <el-button size="small" @click="goToDiagnose(s.id)">诊断</el-button>
          <el-button size="small" @click="goToVariant(s.id)">变式</el-button>
          <el-button size="small" @click="goToAppeal(s.id)">申诉</el-button>
        </div>
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="提交详情" width="700px" top="5vh">
      <div v-loading="detailLoading" class="detail-content">
        <template v-if="detailEval && detailAssignment">
          <div class="detail-head">
            <h3>{{ detailAssignment.title }}</h3>
            <el-tag :type="detailEval.status === 'done' ? 'success' : 'warning'">{{ detailEval.status }}</el-tag>
            <span v-if="detailEval.status === 'done'" class="detail-score">{{ detailEval.score }}分</span>
          </div>
          <p class="detail-desc">{{ detailAssignment.description }}</p>
          <div v-if="detailEval.results?.length" class="detail-cases">
            <h4>评测结果</h4>
            <div v-for="r in detailEval.results" :key="r.case_id" class="case-row" :class="{ fail: !r.passed }">
              <span class="case-icon">{{ r.passed ? '✓' : '✗' }}</span>
              <span class="case-label">用例 {{ r.case_id }}</span>
              <span v-if="r.timed_out" class="case-err">超时</span>
              <span v-if="r.stderr" class="case-err">{{ r.stderr }}</span>
              <span class="case-time">{{ r.elapsed_ms }}ms</span>
            </div>
          </div>
          <div v-else class="no-results">
            <p>{{ detailEval.status === 'pending' ? '评测进行中，请稍后刷新' : '暂无评测结果' }}</p>
          </div>
        </template>
      </div>
      <template #footer>
        <el-button v-if="detailEval?.status === 'done'" type="primary" @click="goToDiagnose(detailEval.submission_id); detailVisible = false">去诊断</el-button>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.submissions-page { max-width: 800px; }
.header { margin-bottom: 32px; }
.header h1 { font-family: 'Space Grotesk'; font-size: 28px; margin: 0 0 8px; }
.desc { color: var(--galaxy-text-secondary); font-size: 15px; margin: 0; }

.empty { text-align: center; padding: 60px 0; }
.empty-text { color: var(--galaxy-text-secondary); font-size: 15px; margin-bottom: 16px; }

.list { display: flex; flex-direction: column; gap: 12px; }
.sub-card {
  display: flex; justify-content: space-between; align-items: center;
  background: var(--galaxy-card); border: 1px solid var(--galaxy-border);
  border-radius: 10px; padding: 16px 20px;
}
.sub-info { display: flex; align-items: center; gap: 12px; }
.sub-id { font-family: 'Space Grotesk'; font-weight: 700; font-size: 18px; color: var(--galaxy-accent); }
.sub-assign { font-size: 14px; color: var(--galaxy-text-secondary); }
.sub-score { font-family: 'Space Grotesk'; font-weight: 700; font-size: 16px; }
.sub-actions { display: flex; gap: 8px; }

.detail-content { min-height: 200px; }
.detail-head { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.detail-head h3 { margin: 0; font-size: 18px; }
.detail-score { font-family: 'Space Grotesk'; font-weight: 700; font-size: 20px; color: var(--galaxy-accent); }
.detail-desc { color: var(--galaxy-text-secondary); white-space: pre-wrap; line-height: 1.6; font-size: 14px; margin: 0 0 20px; }
.detail-cases h4 { font-size: 15px; margin: 0 0 12px; }
.case-row { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--galaxy-border); font-size: 14px; }
.case-row.fail { color: var(--galaxy-error); }
.case-icon { font-weight: 700; }
.case-label { flex: 1; }
.case-err { color: var(--galaxy-error); font-family: 'JetBrains Mono'; font-size: 12px; }
.case-time { color: var(--galaxy-text-secondary); font-size: 12px; }
.no-results { text-align: center; padding: 40px 0; color: var(--galaxy-text-secondary); }
</style>
