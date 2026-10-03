<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { listMyCourses, listAllCourses, listClassesByCourse, enroll } from '@/api/organization'
import { listMySubmissions } from '@/api/submission'
import { ElMessage } from 'element-plus'

interface Course { id: number; name: string; code: string; teacher_id: number; created_at: string }
interface ClassItem { id: number; course_id: number; name: string; created_at: string }

const auth = useAuthStore()
const router = useRouter()
const courses = ref<Course[]>([])
const loading = ref(false)
const selectedCourse = ref<Course | null>(null)
const mySubmissions = ref<{ id: number; assignment_id: number; status: string; score: number }[]>([])
const detailLoading = ref(false)

// 选课弹窗
const enrollVisible = ref(false)
const allCourses = ref<Course[]>([])
const courseClasses = ref<ClassItem[]>([])
const enrollLoading = ref(false)
const expandedCourseId = ref<number | null>(null)

async function loadCourses() {
  loading.value = true
  try {
    courses.value = await listMyCourses()
    if (courses.value.length > 0) selectCourse(courses.value[0])
  } catch (e) { console.error('加载课程失败', e) }
  finally { loading.value = false }
}

async function selectCourse(c: Course) {
  selectedCourse.value = c
  detailLoading.value = true
  mySubmissions.value = []
  try {
    if (auth.role === 'student') {
      const allSubs = await listMySubmissions()
      mySubmissions.value = allSubs
    }
  } catch (e) { console.error('加载失败', e) }
  finally { detailLoading.value = false }
}

// 选课功能
async function openEnrollDialog() {
  enrollVisible.value = true
  try {
    allCourses.value = await listAllCourses()
  } catch (e) { console.error('加载课程列表失败', e) }
}

async function toggleCourseClasses(courseId: number) {
  if (expandedCourseId.value === courseId) {
    expandedCourseId.value = null
    courseClasses.value = []
    return
  }
  expandedCourseId.value = courseId
  try {
    courseClasses.value = await listClassesByCourse(courseId)
  } catch (e) { console.error('加载班级失败', e) }
}

async function handleEnroll(classId: number) {
  enrollLoading.value = true
  try {
    await enroll(classId)
    ElMessage.success('选课成功')
    enrollVisible.value = false
    loadCourses()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '选课失败')
  } finally {
    enrollLoading.value = false
  }
}

const enrolledCourseIds = computed(() => new Set(courses.value.map(c => c.id)))

onMounted(loadCourses)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>我的课程</h1>
        <p class="page-desc">{{ auth.role === 'teacher' ? '管理你的课程、作业与班级学情。' : '查看你选的课程，做作业、看诊断、查成绩。' }}</p>
      </div>
      <div class="header-actions">
        <el-button v-if="auth.role === 'student'" @click="openEnrollDialog">选课</el-button>
        <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/admin')">创建课程</el-button>
      </div>
    </div>

    <div v-if="!loading && courses.length === 0" class="empty-state">
      <p class="empty-text">{{ auth.role === 'teacher' ? '暂无课程，去创建一门吧' : '暂未选课' }}</p>
      <el-button v-if="auth.role === 'student'" type="primary" @click="openEnrollDialog">去选课</el-button>
      <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/admin')">创建课程</el-button>
    </div>

    <div v-else class="split-layout">
      <aside class="sidebar">
        <div v-for="c in courses" :key="c.id" class="sidebar-item" :class="{ active: selectedCourse?.id === c.id }" @click="selectCourse(c)">
          <h4>{{ c.name }}</h4>
          <span class="code">{{ c.code }}</span>
        </div>
      </aside>

      <main class="main-content" v-loading="detailLoading">
        <template v-if="selectedCourse">
          <div class="detail-header">
            <h2>{{ selectedCourse.name }}</h2>
            <span class="code-tag">{{ selectedCourse.code }}</span>
          </div>
          <p class="detail-desc">选择课程后可查看作业进度与成绩。</p>
        </template>
      </main>
    </div>

    <!-- 选课弹窗 -->
    <el-dialog v-model="enrollVisible" title="选课" width="600px">
      <div class="enroll-list">
        <div v-for="c in allCourses" :key="c.id" class="enroll-course">
          <div class="enroll-course-head" @click="toggleCourseClasses(c.id)">
            <div>
              <h4>{{ c.name }}</h4>
              <span class="code">{{ c.code }}</span>
            </div>
            <div class="enroll-status">
              <el-tag v-if="enrolledCourseIds.has(c.id)" type="success" size="small">已选</el-tag>
              <el-icon v-else><ArrowDown /></el-icon>
            </div>
          </div>
          <div v-if="expandedCourseId === c.id" class="class-list">
            <div v-for="cls in courseClasses" :key="cls.id" class="class-item">
              <span>{{ cls.name }}</span>
              <el-button size="small" type="primary" :loading="enrollLoading" @click="handleEnroll(cls.id)">选课</el-button>
            </div>
            <p v-if="courseClasses.length === 0" class="empty-inline">暂无班级</p>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="enrollVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { ArrowDown } from '@element-plus/icons-vue'
export default { components: { ArrowDown } }
</script>

<style scoped>
.page { max-width: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-lg); }
.page-desc { margin: 0; font-size: var(--fs-body); color: var(--text-secondary); }
.header-actions { display: flex; gap: var(--space-xs); }

.empty-state { text-align: center; padding: var(--space-xl) 0; }
.empty-text { color: var(--text-secondary); margin-bottom: var(--space-md); }

.split-layout { display: grid; grid-template-columns: 260px 1fr; gap: var(--space-lg); }
.sidebar { display: flex; flex-direction: column; gap: var(--space-xs); }
.sidebar-item { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-md); cursor: pointer; transition: all var(--duration) var(--ease); }
.sidebar-item:hover { border-color: var(--primary); }
.sidebar-item.active { border-color: var(--primary); background: var(--bg-hover); }
.sidebar-item h4 { margin: 0 0 4px; font-size: var(--fs-body); }
.code { font-size: var(--fs-caption); color: var(--text-placeholder); font-family: 'JetBrains Mono'; }

.main-content { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-lg); min-height: 300px; }
.detail-header { display: flex; align-items: center; gap: var(--space-xs); margin-bottom: var(--space-xs); }
.code-tag { font-size: var(--fs-caption); color: var(--text-secondary); background: var(--bg-hover); padding: 3px 10px; border-radius: var(--radius-sm); font-family: 'JetBrains Mono'; }
.detail-desc { color: var(--text-secondary); font-size: var(--fs-body); }

/* 选课弹窗 */
.enroll-list { display: flex; flex-direction: column; gap: var(--space-xs); }
.enroll-course { border: 1px solid var(--border); border-radius: var(--radius-md); overflow: hidden; }
.enroll-course-head { display: flex; justify-content: space-between; align-items: center; padding: var(--space-sm) var(--space-md); cursor: pointer; background: var(--bg-page); transition: background var(--duration) var(--ease); }
.enroll-course-head:hover { background: var(--bg-hover); }
.enroll-course-head h4 { margin: 0 0 2px; font-size: var(--fs-body); }
.enroll-status { display: flex; align-items: center; }
.class-list { padding: var(--space-xs) var(--space-md); }
.class-item { display: flex; justify-content: space-between; align-items: center; padding: var(--space-xs) 0; border-bottom: 1px solid var(--border); }
.class-item:last-child { border-bottom: none; }
.empty-inline { color: var(--text-placeholder); font-size: var(--fs-caption); padding: var(--space-xs) 0; }
</style>
