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
  <div class="my-submissions">
    <h1>我的提交</h1>
    <p class="desc">查看你的提交记录，点击操作进行误区诊断、变式练习或申诉。</p>
    <div v-if="!loading && submissions.length === 0" class="empty">
      <p>暂无提交记录，去作业列表提交吧。</p>
    </div>
    <el-table v-if="submissions.length" :data="submissions" border>
      <el-table-column prop="id" label="提交 ID" width="80" />
      <el-table-column prop="assignment_id" label="作业 ID" width="80" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 'done' ? 'success' : 'warning'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="score" label="得分" width="60" />
      <el-table-column label="操作" width="240">
        <template #default="{ row }">
          <el-button size="small" @click="goToDiagnose(row.id)">诊断</el-button>
          <el-button size="small" @click="goToVariant(row.id)">变式</el-button>
          <el-button size="small" @click="goToAppeal(row.id)">申诉</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.my-submissions { max-width: 900px; }
.desc { color: var(--galaxy-text-secondary); margin-bottom: 24px; }
.empty { text-align: center; padding: 60px 0; color: var(--galaxy-text-secondary); }
</style>
