<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { createAppeal, listPendingAppeals, reviewAppeal } from '@/api/appeal'
import { listMySubmissions } from '@/api/submission'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import type { AppealOut, SubmissionOut } from '@/types/api'

const auth = useAuthStore()
const route = useRoute()
const submissions = ref<SubmissionOut[]>([])
const submissionId = ref(Number(route.query.submission) || undefined)
const reason = ref('')
const appeals = ref<AppealOut[]>([])
const loading = ref(false)
const reviewDialog = ref(false)
const currentAppeal = ref<AppealOut | null>(null)
const reviewForm = ref({ approved: true, comment: '', new_score: null as number | null })

async function loadSubmissions() {
  try { submissions.value = await listMySubmissions() } catch (e) { console.error('加载提交列表失败', e) }
}

async function handleSubmit() {
  loading.value = true
  try {
    await createAppeal(submissionId.value!, reason.value)
    ElMessage.success('申诉已提交')
    reason.value = ''
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '申诉失败')
  } finally {
    loading.value = false
  }
}

async function loadPending() {
  loading.value = true
  try {
    appeals.value = await listPendingAppeals()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

function openReview(appeal: AppealOut) {
  currentAppeal.value = appeal
  reviewForm.value = { approved: true, comment: '', new_score: null }
  reviewDialog.value = true
}

async function handleReview() {
  if (!currentAppeal.value) return
  loading.value = true
  try {
    await reviewAppeal(currentAppeal.value.id, reviewForm.value.approved, reviewForm.value.comment, reviewForm.value.new_score)
    ElMessage.success('终审完成')
    reviewDialog.value = false
    loadPending()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '终审失败')
  } finally {
    loading.value = false
  }
}
onMounted(loadSubmissions)
</script>

<template>
  <div class="page appeal-page">
    <div class="page-header">
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><ChatDotSquare /></el-icon></span>
        <div>
          <h1>申诉</h1>
          <p class="page-desc">学生对成绩存疑时可提交申诉，教师在此进行终审。</p>
        </div>
      </div>
    </div>

    <div v-if="auth.role === 'student'" class="panel section rise-in" style="--enter-idx:0">
      <div class="section-title"><span class="title-ico"><el-icon><EditPen /></el-icon></span>提交申诉</div>
      <div class="form-bar">
        <span class="label">选择提交</span>
        <el-select v-model="submissionId" placeholder="选择一条提交" style="width: 240px">
          <el-option v-for="s in submissions" :key="s.id" :label="`#${s.id} 作业${s.assignment_id} ${s.status} ${s.score}分`" :value="s.id" />
        </el-select>
      </div>
      <el-input v-model="reason" type="textarea" :rows="3" placeholder="申诉理由" />
      <div style="margin-top: var(--space-sm)">
        <el-button type="primary" :loading="loading" @click="handleSubmit"><el-icon style="margin-right:4px"><Promotion /></el-icon>提交申诉</el-button>
      </div>
    </div>

    <div v-if="auth.role === 'teacher'" class="panel section rise-in" style="--enter-idx:1">
      <div class="section-title"><span class="title-ico"><el-icon><List /></el-icon></span>待审申诉</div>
      <el-button @click="loadPending" style="margin-bottom: var(--space-sm)"><el-icon style="margin-right:4px"><Refresh /></el-icon>刷新列表</el-button>
      <el-table :data="appeals" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="submission_id" label="提交ID" width="80" />
        <el-table-column prop="reason" label="理由" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="openReview(row)"><el-icon style="margin-right:4px"><Aim /></el-icon>终审</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div v-if="auth.role === 'teacher' && !loading && appeals.length === 0" class="empty-state-v2 rise-in" style="--enter-idx:2">
      <span class="empty-ico"><el-icon><Document /></el-icon></span>
      <p>暂无待审申诉，点击「刷新列表」</p>
    </div>

    <el-dialog v-model="reviewDialog" title="申诉终审" width="500px">
      <el-form label-width="80px">
        <el-form-item label="审批">
          <el-switch v-model="reviewForm.approved" active-text="通过" inactive-text="驳回" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="reviewForm.comment" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item v-if="reviewForm.approved" label="改分">
          <el-input-number v-model="reviewForm.new_score" :min="0" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialog = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleReview">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.appeal-page { max-width: 900px; }
.section { margin-bottom: var(--space-lg); }
.form-bar { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-sm); }
.label { font-size: var(--fs-body); color: var(--text-secondary); }
</style>
