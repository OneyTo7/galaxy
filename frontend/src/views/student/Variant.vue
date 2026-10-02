<script setup lang="ts">
import { ref } from 'vue'
import { generateVariant } from '@/api/variant'
import CodeEditor from '@/components/CodeEditor.vue'
import { ElMessage } from 'element-plus'
import type { VariantOut } from '@/types/api'

const submissionId = ref(8)
const variant = ref<VariantOut | null>(null)
const code = ref('')
const loading = ref(false)

async function handleGenerate() {
  loading.value = true
  variant.value = null
  try {
    variant.value = await generateVariant(submissionId.value)
    code.value = ''
    ElMessage.success('变式题已生成')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '变式生成失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="variant-page">
    <h1>变式练习</h1>
    <p class="desc">基于你的误区，AI 生成换情境的变式题，对症练习。</p>
    <div class="form-bar">
      <span>提交 ID</span>
      <el-input-number v-model="submissionId" :min="1" />
      <el-button type="primary" :loading="loading" @click="handleGenerate">生成变式题</el-button>
    </div>
    <div v-if="variant" class="result">
      <h2>{{ variant.title }}</h2>
      <p class="desc-text">{{ variant.description }}</p>
      <div v-if="variant.cases?.length" class="cases">
        <h3>测试用例</h3>
        <div v-for="(c, i) in variant.cases" :key="i" class="case-item">
          <pre>输入: {{ c.input }}</pre>
          <pre>期望: {{ c.expected_output }}</pre>
        </div>
      </div>
      <div v-if="variant.scoring_points?.length" class="points">
        <h3>评分点</h3>
        <ul>
          <li v-for="p in variant.scoring_points" :key="p">{{ p }}</li>
        </ul>
      </div>
      <h3>你的代码</h3>
      <CodeEditor v-model="code" :lang="variant.lang" />
    </div>
  </div>
</template>

<style scoped>
.variant-page { max-width: 900px; }
.desc { color: var(--galaxy-text-secondary); margin-bottom: 24px; }
.form-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 32px; }
.result { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: 8px; padding: 24px; }
.result h2 { margin: 0 0 8px; }
.desc-text { color: var(--galaxy-text-secondary); white-space: pre-wrap; line-height: 1.6; }
.cases, .points { margin-top: 24px; }
.cases h3, .points h3 { font-size: 16px; margin: 0 0 12px; }
.case-item { background: var(--galaxy-bg); border-radius: 6px; padding: 12px; margin-bottom: 8px; }
.case-item pre { margin: 4px 0 0; font-family: 'JetBrains Mono'; font-size: 13px; color: var(--galaxy-text-secondary); }
.points ul { padding-left: 20px; }
.points li { margin-bottom: 4px; }
</style>
