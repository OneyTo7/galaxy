<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAssignment } from '@/api/assignment'
import { listMySubmissions } from '@/api/submission'
import { getEvaluation } from '@/api/submission'
import { getAssignmentReport } from '@/api/report'
import { ElMessage } from 'element-plus'
import type { AssignmentOut, SubmissionOut, EvaluationOut, LearningReport } from '@/types/api'

const route = useRoute()
const router = useRouter()
const assignment = ref<AssignmentOut | null>(null)
const submissions = ref<SubmissionOut[]>([])
const report = ref<LearningReport | null>(null)
const loading = ref(false)
const selectedSubmission = ref<SubmissionOut | null>(null)
const evaluation = ref<EvaluationOut | null>(null)
const evalLoading = ref(false)

async function load() {
  const id = Number(route.query.assignment)
  if (!id) return
  loading.value = true
  try {
    const [a, subs, rep] = await Promise.all([
      getAssignment(id),
      listMySubmissions(),
      getAssignmentReport(id).catch(() => null),
    ])
    assignment.value = a
    submissions.value = subs.filter(s => s.assignment_id === id)
    report.value = rep
  } catch (e) { console.error('加载失败', e) }
  finally { loading.value = false }
}

async function viewSubmission(sub: SubmissionOut) {
  selectedSubmission.value = sub
  evaluation.value = null
  evalLoading.value = true
  try { evaluation.value = await getEvaluation(sub.id) }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '加载评测失败') }
  finally { evalLoading.value = false }
}

const passRate = computed(() => {
  if (!report.value || !report.value.submission_count) return 0
  return Math.round((report.value.submission_count - (report.value.misconception_stats?.reduce((s, m) => s + m.count, 0) || 0)) / report.value.submission_count * 100)
})

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <div class="page-header">
      <div>
        <h1>{{ assignment?.title || '作业详情' }}</h1>
        <p class="page-desc">查看作业内容、提交统计与学生提交详情。</p>
      </div>
      <el-button @click="router.back()">返回</el-button>
    </div>

    <div v-if="assignment" class="split-layout">
      <aside class="sidebar">
        <div class="card">
          <h3>题目信息</h3>
          <div class="meta-tags">
            <el-tag size="small">{{ assignment.lang }}</el-tag>
            <el-tag size="small" type="info">{{ assignment.test_cases?.length || 0 }} 个用例</el-tag>
          </div>
          <div class="section">
            <h4>题目描述</h4>
            <p class="desc-text">{{ assignment.description }}</p>
          </div>
          <div v-if="assignment.test_cases?.length" class="section">
            <h4>测试用例</h4>
            <div v-for="tc in assignment.test_cases" :key="tc.id" class="tc-item">
              <span class="tc-tag">{{ tc.is_hidden ? '🔒' : '👁' }} {{ tc.name || '用例 ' + tc.id }}</span>
              <pre>输入: {{ tc.input }}</pre>
              <pre>期望: {{ tc.expected_output }}</pre>
            </div>
          </div>
        </div>
      </aside>

      <main class="main-content">
        <div v-if="report" class="stat-row">
          <div class="stat-card">
            <span class="stat-num">{{ report.submission_count }}</span>
            <span class="stat-label">提交数</span>
          </div>
          <div class="stat-card">
            <span class="stat-num">{{ report.avg_score }}</span>
            <span class="stat-label">平均分</span>
          </div>
          <div class="stat-card">
            <span class="stat-num">{{ passRate }}%</span>
            <span class="stat-label">通过率</span>
          </div>
        </div>

        <div class="card">
          <h3>学生提交</h3>
          <el-table :data="submissions" border size="small" @row-click="viewSubmission" highlight-current-row>
            <el-table-column prop="id" label="提交 ID" width="80" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'done' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="分数" width="60" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button size="small" text @click.stop="viewSubmission(row)">查看代码</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="selectedSubmission" class="card">
          <h3>提交 #{{ selectedSubmission.id }} 评测详情</h3>
          <div v-loading="evalLoading">
            <div v-if="evaluation" class="eval-detail">
              <div class="eval-header">
                <el-tag :type="evaluation.status === 'done' ? 'success' : 'warning'" size="small">{{ evaluation.status }}</el-tag>
                <span class="eval-score">得分 {{ evaluation.score }}</span>
              </div>
              <div v-for="r in evaluation.results" :key="r.case_id" class="eval-case" :class="{ fail: !r.passed }">
                <span class="case-icon">{{ r.passed ? '✓' : '✗' }}</span>
                <span>用例 {{ r.case_id }}</span>
                <span v-if="r.stderr" class="case-err">{{ r.stderr }}</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-lg); }
.page-desc { margin: 0; font-size: var(--fs-body); color: var(--text-secondary); }

.split-layout { display: grid; grid-template-columns: 340px 1fr; gap: var(--space-lg); }

.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-md); margin-bottom: var(--space-md); box-shadow: var(--shadow-card); }
.card h3 { margin: 0 0 var(--space-sm); font-size: var(--fs-h3); }

.meta-tags { display: flex; gap: var(--space-xs); margin-bottom: var(--space-md); }
.section { margin-bottom: var(--space-md); }
.section h4 { font-size: var(--fs-body); font-weight: 500; margin: 0 0 var(--space-xs); }
.desc-text { color: var(--text-secondary); white-space: pre-wrap; line-height: 1.6; font-size: var(--fs-body); }
.tc-item { background: var(--bg-page); border-radius: var(--radius-md); padding: var(--space-sm); margin-bottom: var(--space-xs); }
.tc-tag { font-size: var(--fs-caption); font-weight: 500; }
.tc-item pre { margin: var(--space-xs) 0 0; font-size: var(--fs-code); color: var(--text-secondary); }

.stat-row { display: flex; gap: var(--space-md); margin-bottom: var(--space-md); }
.stat-card { flex: 1; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-md); box-shadow: var(--shadow-card); }
.stat-num { font-size: var(--fs-data); font-weight: 700; display: block; }
.stat-label { font-size: var(--fs-caption); color: var(--text-secondary); display: block; margin-top: 4px; }

.eval-header { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-sm); }
.eval-score { font-weight: 700; font-size: var(--fs-h3); color: var(--primary); }
.eval-case { display: flex; align-items: center; gap: var(--space-xs); padding: var(--space-xs) 0; border-bottom: 1px solid var(--border); font-size: var(--fs-body); }
.eval-case.fail { color: var(--danger); }
.case-icon { font-weight: 700; }
.case-err { color: var(--danger); font-size: var(--fs-code); }
</style>
