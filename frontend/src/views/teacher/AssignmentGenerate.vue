<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { generateAssignment } from '@/api/assignment'
import { listCourses } from '@/api/organization'
import { ElMessage } from 'element-plus'
import type { AssignmentOut } from '@/types/api'

const router = useRouter()
const prompt = ref('')
const courseId = ref<number | null>(null)
const courses = ref<{ id: number; name: string; code: string }[]>([])
const result = ref<AssignmentOut | null>(null)
const loading = ref(false)

const examples = [
  '出一道考察数组边界的入门题',
  '出一道考察循环终止条件的中等题',
  '出一道考察递归基础的中等题',
]

async function loadCourses() {
  try { courses.value = await listCourses() } catch (e) { console.error('加载课程失败', e) }
}

async function handleGenerate() {
  if (!prompt.value.trim()) { ElMessage.warning('请先输入题目描述'); return }
  loading.value = true
  result.value = null
  try {
    result.value = await generateAssignment(courseId.value, prompt.value)
    ElMessage.success('命题成功，可在「我的作业」发布')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '命题失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadCourses)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><MagicStick /></el-icon></span>
        <div>
          <h1>AI 命题</h1>
          <p class="page-desc">用一句话描述你要出的题，AI 自动生成题面、测试用例、评分细则和参考实现。</p>
        </div>
      </div>
    </div>

    <div class="panel input-card rise-in" style="--enter-idx:0">
      <el-input v-model="prompt" type="textarea" :rows="3" placeholder="描述你要出的题，如：出一道考察数组边界的入门题" />
      <div class="examples">
        <span class="examples-label">试试：</span>
        <el-tag v-for="ex in examples" :key="ex" size="small" class="example-tag" @click="prompt = ex">{{ ex }}</el-tag>
      </div>
      <div class="action-bar">
        <div class="course-select">
          <span class="label">课程（选填）</span>
          <el-select v-model="courseId" placeholder="选择课程" clearable style="width: 200px">
            <el-option v-for="c in courses" :key="c.id" :label="`${c.name} (${c.code})`" :value="c.id" />
          </el-select>
        </div>
        <el-button type="primary" :loading="loading" @click="handleGenerate"><el-icon style="margin-right:4px"><Promotion /></el-icon>生成作业</el-button>
      </div>
    </div>

    <div v-if="result" class="panel result-card rise-in" style="--enter-idx:1">
      <div class="result-head">
        <h2>{{ result.title }}</h2>
        <div class="tags">
          <el-tag size="small">{{ result.lang }}</el-tag>
          <el-tag size="small" type="info">{{ result.test_cases?.length || 0 }} 个用例</el-tag>
          <el-tag size="small" type="warning">草稿</el-tag>
        </div>
      </div>
      <div class="result-section">
        <div class="section-title"><span class="title-ico"><el-icon><Document /></el-icon></span>题面</div>
        <p class="desc-text">{{ result.description }}</p>
      </div>
      <div v-if="result.test_cases?.length" class="result-section">
        <div class="section-title"><span class="title-ico"><el-icon><List /></el-icon></span>测试用例</div>
        <div v-for="tc in result.test_cases" :key="tc.id" class="tc-item">
          <span class="tc-icon">{{ tc.is_hidden ? '🔒' : '👁' }}</span>
          <span class="tc-name">{{ tc.name || '用例' }}</span>
          <pre>输入: {{ tc.input }}</pre>
          <pre>期望: {{ tc.expected_output }}</pre>
        </div>
      </div>
      <div v-if="result.scoring_rubric" class="result-section">
        <div class="section-title"><span class="title-ico"><el-icon><Histogram /></el-icon></span>评分细则</div>
        <p class="desc-text">{{ result.scoring_rubric }}</p>
      </div>
      <div v-if="result.reference_code" class="result-section">
        <div class="section-title"><span class="title-ico"><el-icon><Reading /></el-icon></span>参考实现</div>
        <pre class="ref-code">{{ result.reference_code }}</pre>
      </div>
      <div class="result-actions">
        <el-button @click="router.push('/assignments')"><el-icon style="margin-right:4px"><Promotion /></el-icon>去发布</el-button>
        <el-button text @click="result = null"><el-icon style="margin-right:4px"><Refresh /></el-icon>重新生成</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>

.examples { display: flex; align-items: center; gap: var(--space-xs); margin-top: var(--space-sm); flex-wrap: wrap; }
.examples-label { font-size: var(--fs-caption); color: var(--text-secondary); }
.example-tag { cursor: pointer; }
.action-bar { display: flex; justify-content: space-between; align-items: center; margin-top: var(--space-sm); }
.course-select { display: flex; align-items: center; gap: var(--space-xs); }
.label { font-size: var(--fs-body); color: var(--text-secondary); }

.result-head { padding-bottom: var(--space-sm); border-bottom: 1px solid var(--border); margin-bottom: var(--space-md); }
.tags { display: flex; gap: var(--space-xs); margin-top: var(--space-xs); }
.result-section { margin-bottom: var(--space-md); }
.desc-text { color: var(--text-secondary); white-space: pre-wrap; line-height: 1.6; font-size: var(--fs-body); }
.tc-item { background: var(--bg-sunken); border-radius: var(--radius-md); padding: var(--space-sm); margin-bottom: var(--space-xs); }
.tc-icon { margin-right: var(--space-xs); }
.tc-name { font-weight: 500; font-size: var(--fs-body); }
.tc-item pre { margin: var(--space-xs) 0 0; font-size: var(--fs-code); color: var(--text-secondary); }
.ref-code { background: var(--bg-sunken); border-radius: var(--radius-md); padding: var(--space-sm); font-size: var(--fs-code); overflow-x: auto; }
.result-actions { display: flex; gap: var(--space-xs); }
</style>
