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
    submissions.value = subs.filter((s: any) => s.assignment_id === id)
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
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><Document /></el-icon></span>
        <div>
          <h1>{{ assignment?.title || '作业详情' }}</h1>
          <p class="page-desc">查看作业内容、提交统计与学生提交详情。</p>
        </div>
      </div>
      <el-button @click="router.back()"><el-icon style="margin-right:4px"><Back /></el-icon>返回</el-button>
    </div>

    <div v-if="assignment" class="split-layout">
      <aside class="sidebar rise-in" style="--enter-idx:0">
        <div class="panel">
          <div class="section-title"><span class="title-ico"><el-icon><Document /></el-icon></span>题目信息</div>
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
        <div v-if="report" class="stat-row rise-in" style="--enter-idx:1">
          <div class="stat-card-v2">
            <span class="stat-ico blue"><el-icon><Collection /></el-icon></span>
            <div>
              <span class="stat-num-v2">{{ report.submission_count }}</span>
              <span class="stat-label-v2">提交数</span>
            </div>
          </div>
          <div class="stat-card-v2">
            <span class="stat-ico green"><el-icon><TrendCharts /></el-icon></span>
            <div>
              <span class="stat-num-v2">{{ report.avg_score }}</span>
              <span class="stat-label-v2">平均分</span>
            </div>
          </div>
          <div class="stat-card-v2">
            <span class="stat-ico amber"><el-icon><CircleCheck /></el-icon></span>
            <div>
              <span class="stat-num-v2">{{ passRate }}%</span>
              <span class="stat-label-v2">通过率</span>
            </div>
          </div>
        </div>

        <div class="panel rise-in" style="--enter-idx:2">
          <div class="section-title"><span class="title-ico"><el-icon><List /></el-icon></span>学生提交</div>
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
                <el-button size="small" text @click.stop="viewSubmission(row)"><el-icon style="margin-right:4px"><View /></el-icon>查看代码</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="selectedSubmission" class="panel rise-in" style="--enter-idx:3">
          <div class="section-title"><span class="title-ico"><el-icon><DataAnalysis /></el-icon></span>提交 #{{ selectedSubmission.id }} 评测详情</div>
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

.split-layout { display: grid; grid-template-columns: 340px 1fr; gap: var(--space-lg); }

.meta-tags { display: flex; gap: var(--space-xs); margin-bottom: var(--space-md); }
.section { margin-bottom: var(--space-md); }
.section h4 { font-size: var(--fs-body); font-weight: 500; margin: 0 0 var(--space-xs); }
.desc-text { color: var(--text-secondary); white-space: pre-wrap; line-height: 1.6; font-size: var(--fs-body); }
.tc-item { background: var(--bg-sunken); border-radius: var(--radius-md); padding: var(--space-sm); margin-bottom: var(--space-xs); }
.tc-tag { font-size: var(--fs-caption); font-weight: 500; }
.tc-item pre { margin: var(--space-xs) 0 0; font-size: var(--fs-code); color: var(--text-secondary); }

.stat-row { display: flex; gap: var(--space-md); margin-bottom: var(--space-md); }

.eval-header { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-sm); }
.eval-score { font-weight: 700; font-size: var(--fs-h3); color: var(--primary); }
.eval-case { display: flex; align-items: center; gap: var(--space-xs); padding: var(--space-xs) 0; border-bottom: 1px solid var(--border); font-size: var(--fs-body); }
.eval-case.fail { color: var(--danger); }
.case-icon { font-weight: 700; }
.case-err { color: var(--danger); font-size: var(--fs-code); }
</style>
