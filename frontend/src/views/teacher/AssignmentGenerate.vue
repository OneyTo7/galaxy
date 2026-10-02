<script setup lang="ts">
import { ref } from 'vue'
import { generateAssignment } from '@/api/assignment'
import { ElMessage } from 'element-plus'
import type { AssignmentOut } from '@/types/api'

const prompt = ref('出一道考察数组边界的入门题')
const courseId = ref<number | null>(null)
const result = ref<AssignmentOut | null>(null)
const loading = ref(false)

async function handleGenerate() {
  loading.value = true
  result.value = null
  try {
    result.value = await generateAssignment(courseId.value, prompt.value)
    ElMessage.success('命题成功')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '命题失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="generate-page">
    <h1>AI 命题</h1>
    <p class="desc">输入一句话，AI 自动生成题面、测试用例、评分细则与参考实现。</p>
    <div class="form">
      <el-input v-model="prompt" type="textarea" :rows="2" placeholder="描述你要出的题" />
      <div class="form-bar">
        <span>课程 ID（可选）</span>
        <el-input-number v-model="courseId" :min="1" />
        <el-button type="primary" :loading="loading" @click="handleGenerate">生成作业</el-button>
      </div>
    </div>
    <div v-if="result" class="result">
      <h2>{{ result.title }}</h2>
      <p class="desc-text">{{ result.description }}</p>
      <div class="meta">
        <el-tag>语言 {{ result.lang }}</el-tag>
        <el-tag type="info">状态 {{ result.status }}</el-tag>
      </div>
      <div v-if="result.test_cases?.length" class="cases">
        <h3>测试用例（{{ result.test_cases.length }} 个）</h3>
        <div v-for="tc in result.test_cases" :key="tc.id" class="case-item">
          <span class="case-name">{{ tc.is_hidden ? '🔒' : '👁' }} {{ tc.name || '用例 ' + tc.id }}</span>
          <pre>输入: {{ tc.input }}</pre>
          <pre>期望: {{ tc.expected_output }}</pre>
        </div>
      </div>
      <div v-if="result.scoring_rubric" class="rubric">
        <h3>评分细则</h3>
        <p>{{ result.scoring_rubric }}</p>
      </div>
      <div v-if="result.reference_code" class="ref">
        <h3>参考实现</h3>
        <pre>{{ result.reference_code }}</pre>
      </div>
    </div>
  </div>
</template>

<style scoped>
.generate-page { max-width: 900px; }
.desc { color: var(--galaxy-text-secondary); margin-bottom: 24px; }
.form { margin-bottom: 32px; }
.form-bar { display: flex; align-items: center; gap: 12px; margin-top: 12px; }
.result { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: 8px; padding: 24px; }
.result h2 { margin: 0 0 8px; }
.desc-text { color: var(--galaxy-text-secondary); white-space: pre-wrap; line-height: 1.6; }
.meta { display: flex; gap: 8px; margin: 16px 0; }
.cases { margin-top: 24px; }
.cases h3 { font-size: 16px; margin: 0 0 12px; }
.case-item { background: var(--galaxy-bg); border-radius: 6px; padding: 12px; margin-bottom: 8px; }
.case-name { font-weight: 500; }
.case-item pre { margin: 8px 0 0; font-family: 'JetBrains Mono'; font-size: 13px; color: var(--galaxy-text-secondary); }
.rubric, .ref { margin-top: 24px; }
.rubric h3, .ref h3 { font-size: 16px; margin: 0 0 8px; }
.ref pre { background: var(--galaxy-bg); border-radius: 6px; padding: 12px; font-family: 'JetBrains Mono'; font-size: 13px; overflow-x: auto; }
</style>
