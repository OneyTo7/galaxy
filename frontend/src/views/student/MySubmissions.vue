<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listMySubmissions } from '@/api/submission'
import type { SubmissionOut } from '@/types/api'

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
          <el-button size="small" @click="goToDiagnose(s.id)">诊断</el-button>
          <el-button size="small" @click="goToVariant(s.id)">变式</el-button>
          <el-button size="small" @click="goToAppeal(s.id)">申诉</el-button>
        </div>
      </div>
    </div>
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
</style>
