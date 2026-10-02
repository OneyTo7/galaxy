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
  <div class="admin-page">
    <h1>课程管理</h1>
    <div class="section">
      <h3>创建课程</h3>
      <div class="form-bar">
        <el-input v-model="courseForm.name" placeholder="课程名称" />
        <el-input v-model="courseForm.code" placeholder="课程代码" />
        <el-button type="primary" @click="handleCreateCourse">创建</el-button>
      </div>
    </div>
    <div class="section">
      <h3>课程列表</h3>
      <el-select v-model="selectedCourse" placeholder="选择课程查看班级" style="width: 300px">
        <el-option v-for="c in courses" :key="c.id" :label="`${c.name} (${c.code})`" :value="c.id" />
      </el-select>
    </div>
    <div v-if="selectedCourse" class="section">
      <h3>班级管理</h3>
      <div class="form-bar">
        <el-input v-model="classForm" placeholder="班级名称" />
        <el-button type="primary" @click="handleCreateClass">创建班级</el-button>
      </div>
      <el-table :data="classes" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="班级名称" />
        <el-table-column label="选课" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="loadEnrollments(row.id)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div v-if="enrollments.length" class="section">
      <h3>选课学生</h3>
      <el-table :data="enrollments" border>
        <el-table-column prop="student_id" label="学生 ID" />
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.admin-page { max-width: 900px; }
.section { margin-bottom: 32px; }
.section h3 { font-size: 16px; margin: 0 0 12px; }
.form-bar { display: flex; gap: 12px; margin-bottom: 12px; }
</style>
