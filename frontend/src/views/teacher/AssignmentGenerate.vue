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
  if (!prompt.value.trim()) {
    ElMessage.warning('请先输入题目描述')
    return
  }
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
  <div class="gen-page">
    <div class="header">
      <h1>AI 命题</h1>
      <p class="desc">用一句话描述你要出的题，AI 自动生成题面、测试用例、评分细则和参考实现。</p>
    </div>

    <div class="input-card">
      <el-input v-model="prompt" type="textarea" :rows="3" placeholder="描述你要出的题，如：出一道考察数组边界的入门题" />
      <div class="examples">
        <span class="examples-label">试试：</span>
        <el-tag v-for="ex in examples" :key="ex" size="small" class="example-tag" @click="prompt = ex">{{ ex }}</el-tag>
      </div>
      <div class="action-bar">
        <div class="course-input">
          <span class="label">课程（选填）</span>
          <el-select v-model="courseId" placeholder="选择课程" clearable style="width: 200px">
            <el-option v-for="c in courses" :key="c.id" :label="`${c.name} (${c.code})`" :value="c.id" />
          </el-select>
        </div>
        <el-button type="primary" :loading="loading" @click="handleGenerate">生成作业</el-button>
      </div>
    </div>

    <div v-if="result" class="result-card">
      <div class="result-head">
        <h2>{{ result.title }}</h2>
        <div class="tags">
          <el-tag size="small">{{ result.lang }}</el-tag>
          <el-tag size="small" type="info">{{ result.test_cases?.length || 0 }} 个用例</el-tag>
          <el-tag size="small" type="warning">草稿</el-tag>
        </div>
      </div>
      <div class="result-section">
        <h3>题面</h3>
        <p class="desc-text">{{ result.description }}</p>
      </div>
      <div v-if="result.test_cases?.length" class="result-section">
        <h3>测试用例</h3>
        <div v-for="tc in result.test_cases" :key="tc.id" class="tc-item">
          <span class="tc-icon">{{ tc.is_hidden ? '🔒' : '👁' }}</span>
          <span class="tc-name">{{ tc.name || '用例' }}</span>
          <pre class="tc-io">输入: {{ tc.input }}</pre>
          <pre class="tc-io">期望: {{ tc.expected_output }}</pre>
        </div>
      </div>
      <div v-if="result.scoring_rubric" class="result-section">
        <h3>评分细则</h3>
        <p class="desc-text">{{ result.scoring_rubric }}</p>
      </div>
      <div v-if="result.reference_code" class="result-section">
        <h3>参考实现</h3>
        <pre class="ref-code">{{ result.reference_code }}</pre>
      </div>
      <div class="result-actions">
        <el-button @click="router.push('/assignments')">去发布 →</el-button>
        <el-button text @click="result = null">重新生成</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.gen-page { max-width: 900px; }
.header { margin-bottom: 32px; }
.header h1 { font-family: 'Space Grotesk'; font-size: 28px; margin: 0 0 8px; }
.desc { color: var(--galaxy-text-secondary); font-size: 15px; margin: 0; }

.input-card {
  background: var(--galaxy-card);
  border: 1px solid var(--galaxy-border);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
}
.examples { display: flex; align-items: center; gap: 8px; margin-top: 16px; flex-wrap: wrap; }
.examples-label { font-size: 13px; color: var(--galaxy-text-secondary); }
.example-tag { cursor: pointer; }
.action-bar { display: flex; justify-content: space-between; align-items: center; margin-top: 16px; }
.course-input { display: flex; align-items: center; gap: 8px; }
.label { font-size: 14px; color: var(--galaxy-text-secondary); }

.result-card {
  background: var(--galaxy-card);
  border: 1px solid var(--galaxy-border);
  border-radius: 12px;
  overflow: hidden;
}
.result-head {
  padding: 24px;
  border-bottom: 1px solid var(--galaxy-border);
}
.result-head h2 { margin: 0 0 12px; font-size: 22px; }
.tags { display: flex; gap: 8px; }
.result-section { padding: 20px 24px; border-bottom: 1px solid var(--galaxy-border); }
.result-section h3 { font-size: 15px; margin: 0 0 12px; }
.desc-text { color: var(--galaxy-text-secondary); white-space: pre-wrap; line-height: 1.7; font-size: 14px; }
.tc-item { background: var(--galaxy-bg); border-radius: 6px; padding: 12px; margin-bottom: 8px; }
.tc-icon { margin-right: 8px; }
.tc-name { font-weight: 500; font-size: 14px; }
.tc-io { margin: 6px 0 0; font-family: 'JetBrains Mono'; font-size: 12px; color: var(--galaxy-text-secondary); }
.ref-code { background: var(--galaxy-bg); border-radius: 6px; padding: 12px; font-family: 'JetBrains Mono'; font-size: 13px; overflow-x: auto; }
.result-actions { padding: 20px 24px; display: flex; gap: 12px; }
</style>
