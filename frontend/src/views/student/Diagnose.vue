<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { diagnose } from '@/api/diagnose'
import { listMySubmissions } from '@/api/submission'
import { ElMessage } from 'element-plus'
import type { DiagnoseOut, SubmissionOut } from '@/types/api'

const route = useRoute()
const router = useRouter()
const submissions = ref<SubmissionOut[]>([])
const submissionId = ref(Number(route.query.submission) || undefined)
const result = ref<DiagnoseOut | null>(null)
const loading = ref(false)

async function loadSubmissions() {
  try {
    submissions.value = await listMySubmissions()
  } catch (e) {
    console.error('加载提交列表失败', e)
  }
}

async function handleDiagnose() {
  if (!submissionId.value) {
    ElMessage.warning('请先选择一条提交记录')
    return
  }
  loading.value = true
  result.value = null
  try {
    result.value = await diagnose(submissionId.value)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '诊断失败')
  } finally {
    loading.value = false
  }
}
onMounted(loadSubmissions)
</script>

<template>
  <div class="diagnose-page">
    <div class="header">
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><Aim /></el-icon></span>
        <div>
          <h1>误区诊断</h1>
          <p class="desc">AI 读取你的代码与评测结果，分析你卡在哪个误区上，给出证据和对应知识点。</p>
        </div>
      </div>
    </div>

    <div class="action-bar">
      <div class="input-group">
        <span class="label"><el-icon><Document /></el-icon> 选择提交</span>
        <el-select v-model="submissionId" placeholder="选择一条提交" style="width: 280px">
          <el-option v-for="s in submissions" :key="s.id" :label="`#${s.id} 作业${s.assignment_id} ${s.status} ${s.score}分`" :value="s.id" />
        </el-select>
      </div>
      <el-button type="primary" :loading="loading" @click="handleDiagnose">
        <el-icon style="margin-right: 4px"><VideoPlay /></el-icon>开始诊断
      </el-button>
      <el-button text @click="router.push('/my-submissions')">从我的提交选择</el-button>
    </div>

    <div v-if="result" class="result-card rise-in" style="--enter-idx:1">
      <div class="result-main">
        <div class="result-type">
          <span class="type-label">误区类型</span>
          <h2 class="type-value">{{ result.misconception_type }}</h2>
        </div>
        <div class="confidence-bar">
          <span class="conf-label">置信度 {{ (result.confidence * 100).toFixed(0) }}%</span>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: (result.confidence * 100) + '%' }" />
          </div>
        </div>
      </div>

      <div class="result-detail">
        <div class="detail-block">
          <span class="detail-label">证据</span>
          <p class="detail-text">{{ result.evidence }}</p>
          <div class="evidence-badge" :class="{ validated: result.evidence_validated, unvalidated: !result.evidence_validated }">
            <el-icon v-if="result.evidence_validated"><CircleCheck /></el-icon>
            <el-icon v-else><Warning /></el-icon>
            <span v-if="result.evidence_validated">证据已校验（命中真实报错）</span>
            <span v-else>低置信（证据未命中真实信号，已降级）</span>
          </div>
        </div>
        <div class="detail-block">
          <span class="detail-label">知识点</span>
          <div class="kp-tags">
            <el-tag size="large" effect="plain">{{ result.knowledge_point }}</el-tag>
          </div>
        </div>
        <div class="detail-block" v-if="result.status === 'overcome'">
          <div class="overcome-banner"><el-icon><CircleCheck /></el-icon> 该误区已被克服（变式练习通过后自动标记）</div>
        </div>
      </div>

      <div class="result-actions">
        <el-button type="primary" @click="router.push(`/variant?submission=${submissionId}`)">
          <el-icon style="margin-right: 4px"><MagicStick /></el-icon>去做变式练习
        </el-button>
      </div>
    </div>

    <div v-else-if="!loading" class="empty-state-v2">
      <div class="empty-ico"><el-icon><Aim /></el-icon></div>
      <p>选择一条提交记录，点击开始诊断</p>
    </div>
  </div>
</template>

<style scoped>
.diagnose-page { max-width: 820px; }

.header { margin-bottom: 28px; }
.desc { color: var(--text-secondary); font-size: 14px; margin: 0; }

.action-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}
.input-group { display: flex; align-items: center; gap: 8px; }
.label { font-size: 13px; color: var(--text-secondary); display: inline-flex; align-items: center; gap: 4px; }
.label .el-icon { font-size: 14px; color: var(--primary); }

.result-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-1);
}

.result-main {
  background: linear-gradient(135deg, rgba(79, 124, 255, 0.08), rgba(96, 165, 250, 0.02));
  padding: 28px 32px;
  border-bottom: 1px solid var(--border);
}

.result-type { margin-bottom: 20px; }
.type-label {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.type-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--primary);
  margin: 4px 0 0;
  letter-spacing: -0.01em;
}

.confidence-bar { display: flex; flex-direction: column; gap: 6px; }
.conf-label { font-size: 12px; color: var(--text-secondary); }
.bar-track {
  height: 6px;
  background: var(--bg-sunken);
  border-radius: 3px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: var(--grad-primary);
  border-radius: 3px;
  transition: width 0.5s var(--ease);
}

.result-detail { padding: 24px 32px; }
.detail-block { margin-bottom: 20px; }
.detail-label {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}
.detail-text {
  font-size: 13px;
  line-height: 1.7;
  margin: 0 0 10px;
  color: var(--ink-2);
  font-family: 'SF Mono', monospace;
  background: var(--bg-sunken);
  padding: 10px 12px;
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-word;
}

.result-actions { padding: 0 32px 28px; }

.evidence-badge { display: inline-flex; align-items: center; gap: 5px; margin-top: 4px; padding: 5px 11px; border-radius: 6px; font-size: 12px; font-weight: 500; }
.evidence-badge .el-icon { font-size: 14px; }
.evidence-badge.validated { background: rgba(18, 183, 106, 0.10); color: var(--success); }
.evidence-badge.unvalidated { background: rgba(245, 158, 11, 0.12); color: #C77D00; }
.kp-tags { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.overcome-banner { display: flex; align-items: center; gap: 8px; padding: 12px 16px; background: rgba(18, 183, 106, 0.08); border: 1px solid rgba(18, 183, 106, 0.28); border-radius: 10px; color: var(--success); font-weight: 500; font-size: 13px; }
.overcome-banner .el-icon { font-size: 16px; }
</style>
