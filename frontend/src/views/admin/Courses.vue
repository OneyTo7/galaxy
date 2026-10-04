<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { listCourses, createCourse, listClasses, createClass, listEnrollments } from '@/api/organization'
import { ElMessage } from 'element-plus'
import type { EnrollmentOut } from '@/types/api'

interface Course { id: number; name: string; code: string }
interface ClassItem { id: number; course_id: number; name: string }

const courses = ref<Course[]>([])
const selectedCourse = ref<number | null>(null)
const classes = ref<ClassItem[]>([])
const enrollments = ref<EnrollmentOut[]>([])
const courseForm = ref({ name: '', code: '' })
const classForm = ref('')

async function loadCourses() {
  try {
    courses.value = await listCourses()
  } catch (e) {
    console.error('加载课程失败', e)
  }
}

async function handleCreateCourse() {
  if (!courseForm.value.name || !courseForm.value.code) return
  try {
    await createCourse(courseForm.value.name, courseForm.value.code)
    ElMessage.success('课程已创建')
    courseForm.value = { name: '', code: '' }
    loadCourses()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  }
}

watch(selectedCourse, async (id) => {
  if (id) {
    try {
      classes.value = await listClasses(id)
    } catch (e) {
      console.error('加载班级失败', e)
    }
  }
})

async function handleCreateClass() {
  if (!selectedCourse.value || !classForm.value) return
  try {
    await createClass(selectedCourse.value, classForm.value)
    ElMessage.success('班级已创建')
    classForm.value = ''
    classes.value = await listClasses(selectedCourse.value)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  }
}

async function loadEnrollments(classId: number) {
  try {
    enrollments.value = await listEnrollments(classId)
  } catch (e) {
    console.error('加载选课失败', e)
  }
}

onMounted(loadCourses)
</script>

<template>
  <div class="page admin-page">
    <div class="page-header">
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><School /></el-icon></span>
        <div>
          <h1>课程管理</h1>
          <p class="page-desc">创建课程、班级并管理选课学生。</p>
        </div>
      </div>
    </div>

    <div class="panel section rise-in" style="--enter-idx:0">
      <div class="section-title"><span class="title-ico"><el-icon><Plus /></el-icon></span>创建课程</div>
      <div class="form-bar">
        <el-input v-model="courseForm.name" placeholder="课程名称" />
        <el-input v-model="courseForm.code" placeholder="课程代码" />
        <el-button type="primary" @click="handleCreateCourse"><el-icon style="margin-right:4px"><Plus /></el-icon>创建</el-button>
      </div>
    </div>

    <div class="panel section rise-in" style="--enter-idx:1">
      <div class="section-title"><span class="title-ico"><el-icon><Collection /></el-icon></span>课程列表</div>
      <el-select v-model="selectedCourse" placeholder="选择课程查看班级" style="width: 300px">
        <el-option v-for="c in courses" :key="c.id" :label="`${c.name} (${c.code})`" :value="c.id" />
      </el-select>
    </div>

    <div v-if="selectedCourse" class="panel section rise-in" style="--enter-idx:2">
      <div class="section-title"><span class="title-ico"><el-icon><Notebook /></el-icon></span>班级管理</div>
      <div class="form-bar">
        <el-input v-model="classForm" placeholder="班级名称" />
        <el-button type="primary" @click="handleCreateClass"><el-icon style="margin-right:4px"><Plus /></el-icon>创建班级</el-button>
      </div>
      <el-table :data="classes" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="班级名称" />
        <el-table-column label="选课" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="loadEnrollments(row.id)"><el-icon style="margin-right:4px"><View /></el-icon>查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div v-if="enrollments.length" class="panel section rise-in" style="--enter-idx:3">
      <div class="section-title"><span class="title-ico"><el-icon><User /></el-icon></span>选课学生</div>
      <el-table :data="enrollments" border>
        <el-table-column prop="student_id" label="学生 ID" />
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.admin-page { max-width: 900px; }
.section { margin-bottom: var(--space-lg); }
.form-bar { display: flex; gap: var(--space-sm); margin-bottom: var(--space-sm); }
</style>
