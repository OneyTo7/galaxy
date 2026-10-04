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
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><Collection /></el-icon></span>
        <div>
          <h1>选课</h1>
          <p class="page-desc">浏览全部课程，展开查看班级并完成选课。</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button v-if="auth.role === 'student'" @click="openEnrollDialog">
          <el-icon style="margin-right: 4px"><Plus /></el-icon>选课
        </el-button>
        <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/admin')">
          <el-icon style="margin-right: 4px"><Plus /></el-icon>创建课程
        </el-button>
      </div>
    </div>

    <div v-if="!loading && courses.length === 0" class="empty-state-v2 rise-in" style="--enter-idx:0">
      <div class="empty-ico"><el-icon><Collection /></el-icon></div>
      <p>{{ auth.role === 'teacher' ? '暂无课程，去创建一门吧' : '暂未选课' }}</p>
      <el-button v-if="auth.role === 'student'" type="primary" @click="openEnrollDialog">
        <el-icon style="margin-right: 4px"><Plus /></el-icon>去选课
      </el-button>
      <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/admin')">
        <el-icon style="margin-right: 4px"><Plus /></el-icon>创建课程
      </el-button>
    </div>

    <div v-else class="split-layout">
      <aside class="sidebar">
        <div class="section-title side-title"><span class="title-ico"><el-icon><Collection /></el-icon></span>全部课程</div>
        <div v-for="(c, idx) in courses" :key="c.id" class="panel sidebar-item rise-in" :style="{ '--enter-idx': idx }" :class="{ active: selectedCourse?.id === c.id }" @click="selectCourse(c)">
          <div class="course-ico"><el-icon><Reading /></el-icon></div>
          <div class="course-meta">
            <h4>{{ c.name }}</h4>
            <span class="code">{{ c.code }}</span>
          </div>
        </div>
      </aside>

      <main class="panel main-content rise-in" style="--enter-idx:1" v-loading="detailLoading">
        <template v-if="selectedCourse">
          <div class="detail-header">
            <h2>{{ selectedCourse.name }}</h2>
            <span class="code-tag">{{ selectedCourse.code }}</span>
          </div>
          <p class="detail-desc">选择课程后可查看作业进度与成绩。</p>
        </template>
        <div v-else class="empty-state-v2">
          <div class="empty-ico"><el-icon><Collection /></el-icon></div>
          <p>请选择左侧课程查看详情</p>
        </div>
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
.header-actions { display: flex; gap: var(--space-xs); }

.split-layout { display: grid; grid-template-columns: 280px 1fr; gap: var(--space-md); }
.sidebar { display: flex; flex-direction: column; gap: var(--space-xs); }
.side-title { margin-bottom: var(--space-xs); }
.sidebar-item {
  display: flex; align-items: center; gap: var(--space-sm);
  cursor: pointer; padding: var(--space-sm) var(--space-md);
}
.sidebar-item .course-ico {
  display: inline-flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; border-radius: 10px;
  background: rgba(79, 124, 255, 0.10); color: var(--primary);
  flex-shrink: 0;
}
.sidebar-item .course-meta { display: flex; flex-direction: column; min-width: 0; }
.sidebar-item:hover { border-color: var(--primary); }
.sidebar-item.active { border-color: var(--primary); background: var(--bg-hover); }
.sidebar-item h4 { margin: 0; font-size: var(--fs-body); color: var(--ink); }
.code { font-size: var(--fs-caption); color: var(--text-placeholder); font-family: 'JetBrains Mono'; }

.main-content { min-height: 300px; }
.detail-header { display: flex; align-items: center; gap: var(--space-xs); margin-bottom: var(--space-xs); }
.detail-header h2 { margin: 0; font-size: var(--fs-h2); color: var(--ink); }
.code-tag { font-size: var(--fs-caption); color: var(--text-secondary); background: var(--bg-hover); padding: 3px 10px; border-radius: var(--radius-sm); font-family: 'JetBrains Mono'; }
.detail-desc { color: var(--text-secondary); font-size: var(--fs-body); }

/* 选课弹窗 */
.enroll-list { display: flex; flex-direction: column; gap: var(--space-xs); }
.enroll-course { border: 1px solid var(--border); border-radius: var(--radius-md); overflow: hidden; }
.enroll-course-head { display: flex; justify-content: space-between; align-items: center; padding: var(--space-sm) var(--space-md); cursor: pointer; background: var(--bg-page); transition: background var(--duration) var(--ease); }
.enroll-course-head:hover { background: var(--bg-hover); }
.enroll-course-head h4 { margin: 0 0 2px; font-size: var(--fs-body); color: var(--ink); }
.enroll-status { display: flex; align-items: center; }
.class-list { padding: var(--space-xs) var(--space-md); }
.class-item { display: flex; justify-content: space-between; align-items: center; padding: var(--space-xs) 0; border-bottom: 1px solid var(--border); }
.class-item:last-child { border-bottom: none; }
.empty-inline { color: var(--text-placeholder); font-size: var(--fs-caption); padding: var(--space-xs) 0; }
</style>
