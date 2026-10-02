<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { createAppeal, listPendingAppeals, reviewAppeal } from '@/api/appeal'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import type { AppealOut } from '@/types/api'

const auth = useAuthStore()
const route = useRoute()
const submissionId = ref(Number(route.query.submission) || 8)
const reason = ref('')
const appeals = ref<AppealOut[]>([])
const loading = ref(false)
const reviewDialog = ref(false)
const currentAppeal = ref<AppealOut | null>(null)
const reviewForm = ref({ approved: true, comment: '', new_score: null as number | null })

async function handleSubmit() {
  loading.value = true
  try {
    await createAppeal(submissionId.value, reason.value)
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
</script>

<template>
  <div class="appeal-page">
    <h1>申诉</h1>
    <div v-if="auth.role === 'student'" class="section">
      <h3>提交申诉</h3>
      <div class="form-bar">
        <span>提交 ID</span>
        <el-input-number v-model="submissionId" :min="1" />
      </div>
      <el-input v-model="reason" type="textarea" :rows="3" placeholder="申诉理由" />
      <div style="margin-top: 12px">
        <el-button type="primary" :loading="loading" @click="handleSubmit">提交申诉</el-button>
      </div>
    </div>
    <div v-if="auth.role === 'teacher'" class="section">
      <h3>待审申诉</h3>
      <el-button @click="loadPending" style="margin-bottom: 12px">刷新列表</el-button>
      <el-table :data="appeals" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="submission_id" label="提交ID" width="80" />
        <el-table-column prop="reason" label="理由" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="openReview(row)">终审</el-button>
          </template>
        </el-table-column>
      </el-table>
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
.section { margin-bottom: 32px; }
.form-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
</style>
