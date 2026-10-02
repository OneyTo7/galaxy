<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { diagnose } from '@/api/diagnose'
import { ElMessage } from 'element-plus'
import type { DiagnoseOut } from '@/types/api'

const route = useRoute()
const router = useRouter()
const submissionId = ref(Number(route.query.submission) || 0)
const result = ref<DiagnoseOut | null>(null)
const loading = ref(false)

async function handleDiagnose() {
  if (!submissionId.value) {
    ElMessage.warning('请先从「我的提交」选择一条提交记录')
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
</script>

<template>
  <div class="diagnose-page">
    <div class="header">
      <h1>误区诊断</h1>
      <p class="desc">AI 读取你的代码与评测结果，分析你卡在哪个误区上，给出证据和对应知识点。</p>
    </div>

    <div class="action-bar">
      <div class="input-group">
        <span class="label">提交 ID</span>
        <el-input-number v-model="submissionId" :min="1" controls-position="right" style="width: 120px" />
      </div>
      <el-button type="primary" :loading="loading" @click="handleDiagnose">开始诊断</el-button>
      <el-button text @click="router.push('/my-submissions')">从我的提交选择</el-button>
    </div>

    <div v-if="result" class="result-card">
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
        </div>
        <div class="detail-block">
          <span class="detail-label">知识点</span>
          <el-tag size="large" effect="plain">{{ result.knowledge_point }}</el-tag>
        </div>
      </div>

      <div class="result-actions">
        <el-button type="primary" @click="router.push(`/variant?submission=${submissionId}`)">去做变式练习 →</el-button>
      </div>
    </div>

    <div v-else-if="!loading" class="empty-state">
      <p>输入提交 ID 或从「我的提交」选择，点击开始诊断。</p>
    </div>
  </div>
</template>

<style scoped>
.diagnose-page { max-width: 800px; }

.header { margin-bottom: 32px; }
.header h1 { font-family: 'Space Grotesk'; font-size: 28px; margin: 0 0 8px; }
.desc { color: var(--galaxy-text-secondary); font-size: 15px; margin: 0; }

.action-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}
.input-group { display: flex; align-items: center; gap: 8px; }
.label { font-size: 14px; color: var(--galaxy-text-secondary); }

.result-card {
  background: var(--galaxy-card);
  border: 1px solid var(--galaxy-border);
  border-radius: 12px;
  overflow: hidden;
}

.result-main {
  background: linear-gradient(135deg, rgba(91, 127, 255, 0.08), rgba(91, 127, 255, 0.02));
  padding: 32px;
  border-bottom: 1px solid var(--galaxy-border);
}

.result-type { margin-bottom: 20px; }
.type-label {
  font-size: 12px;
  color: var(--galaxy-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.type-value {
  font-family: 'Space Grotesk';
  font-size: 28px;
  font-weight: 700;
  color: var(--galaxy-accent);
  margin: 4px 0 0;
}

.confidence-bar { display: flex; flex-direction: column; gap: 6px; }
.conf-label { font-size: 13px; color: var(--galaxy-text-secondary); }
.bar-track {
  height: 6px;
  background: var(--galaxy-border);
  border-radius: 3px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: var(--galaxy-accent);
  border-radius: 3px;
  transition: width 0.5s;
}

.result-detail { padding: 24px 32px; }
.detail-block { margin-bottom: 20px; }
.detail-label {
  display: block;
  font-size: 12px;
  color: var(--galaxy-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}
.detail-text {
  font-size: 15px;
  line-height: 1.7;
  margin: 0;
  color: var(--galaxy-text);
}

.result-actions { padding: 0 32px 32px; }

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--galaxy-text-secondary);
  font-size: 15px;
}
</style>
