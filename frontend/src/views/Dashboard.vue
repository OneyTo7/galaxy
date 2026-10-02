<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { listMyCourses, listCourseAssignments, listCourseStudents } from '@/api/organization'
import { ElMessage } from 'element-plus'

interface Course {
  id: number
  name: string
  code: string
  teacher_id: number
  created_at: string
}

interface CourseAssign {
  id: number
  title: string
  status: string
  lang: string
}

const auth = useAuthStore()
const router = useRouter()
const courses = ref<Course[]>([])
const loading = ref(false)
const selectedCourse = ref<Course | null>(null)
const assignments = ref<CourseAssign[]>([])
const students = ref<[number, string][]>([])
const detailLoading = ref(false)

async function loadCourses() {
  loading.value = true
  try {
    courses.value = await listMyCourses()
    if (courses.value.length > 0) {
      selectCourse(courses.value[0])
    }
  } catch (e) {
    console.error('加载课程失败', e)
  } finally {
    loading.value = false
  }
}

async function selectCourse(c: Course) {
  selectedCourse.value = c
  detailLoading.value = true
  assignments.value = []
  students.value = []
  try {
    const [a, s] = await Promise.all([
      listCourseAssignments(c.id),
      auth.role === 'teacher' ? listCourseStudents(c.id) : Promise.resolve([]),
    ])
    assignments.value = a
    students.value = s
  } catch (e) {
    console.error('加载课程详情失败', e)
  } finally {
    detailLoading.value = false
  }
}

onMounted(loadCourses)
</script>

<template>
  <div class="courses-page">
    <div class="header">
      <h1>我的课程</h1>
      <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/admin')">创建课程</el-button>
    </div>
    <p class="desc">{{ auth.role === 'teacher' ? '管理你的课程、作业与班级学情。' : '查看你选的课程，做作业、看诊断、查成绩。' }}</p>

    <div v-if="!loading && courses.length === 0" class="empty">
      <p class="empty-text">{{ auth.role === 'teacher' ? '暂无课程，去创建一门吧' : '暂未选课' }}</p>
      <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/admin')">创建课程</el-button>
    </div>

    <div v-else class="layout">
      <aside class="course-list">
        <div
          v-for="c in courses"
          :key="c.id"
          class="course-item"
          :class="{ active: selectedCourse?.id === c.id }"
          @click="selectCourse(c)"
        >
          <h4>{{ c.name }}</h4>
          <span class="course-code">{{ c.code }}</span>
        </div>
      </aside>

      <main class="course-detail" v-loading="detailLoading">
        <template v-if="selectedCourse">
          <div class="detail-header">
            <h2>{{ selectedCourse.name }}</h2>
            <span class="course-code-tag">{{ selectedCourse.code }}</span>
          </div>

          <div class="stats-row">
            <div class="stat">
              <span class="stat-num">{{ assignments.length }}</span>
              <span class="stat-label">作业</span>
            </div>
            <div class="stat" v-if="auth.role === 'teacher'">
              <span class="stat-num">{{ students.length }}</span>
              <span class="stat-label">学生</span>
            </div>
            <div class="stat">
              <span class="stat-num">{{ assignments.filter(a => a.status === 'published').length }}</span>
              <span class="stat-label">已发布</span>
            </div>
          </div>

          <div class="section">
            <div class="section-header">
              <h3>课程作业</h3>
              <el-button v-if="auth.role === 'teacher'" size="small" @click="router.push('/assignment-generate')">AI命题</el-button>
            </div>
            <div v-if="assignments.length === 0" class="section-empty">暂无作业</div>
            <div v-for="a in assignments" :key="a.id" class="assignment-row">
              <div class="assign-info">
                <span class="assign-title">{{ a.title }}</span>
                <el-tag :type="a.status === 'published' ? 'success' : 'info'" size="small">
                  {{ a.status === 'published' ? '已发布' : '草稿' }}
                </el-tag>
                <span class="assign-lang">{{ a.lang }}</span>
              </div>
              <el-button v-if="auth.role === 'student'" size="small" type="primary" @click="router.push(`/submit?assignment=${a.id}`)">去做</el-button>
            </div>
          </div>

          <div v-if="auth.role === 'teacher' && students.length" class="section">
            <h3>选课学生</h3>
            <el-table :data="students.map(([id, cls]) => ({ student_id: id, class_name: cls }))" border size="small">
              <el-table-column prop="student_id" label="学生 ID" width="100" />
              <el-table-column prop="class_name" label="班级" />
            </el-table>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<style scoped>
.courses-page { max-width: 1100px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.header h1 { font-family: 'Space Grotesk'; font-size: 28px; margin: 0; }
.desc { color: var(--galaxy-text-secondary); font-size: 15px; margin: 0 0 24px; }

.empty { text-align: center; padding: 60px 0; }
.empty-text { color: var(--galaxy-text-secondary); margin-bottom: 16px; }

.layout { display: grid; grid-template-columns: 240px 1fr; gap: 16px; }
.course-list { display: flex; flex-direction: column; gap: 8px; }
.course-item {
  background: var(--galaxy-card-solid); border: 1px solid var(--galaxy-border);
  border-radius: 8px; padding: 14px 16px; cursor: pointer; transition: all 0.15s;
}
.course-item:hover { border-color: var(--galaxy-accent); }
.course-item.active { border-color: var(--galaxy-accent); background: var(--galaxy-accent-soft); }
.course-item h4 { margin: 0 0 4px; font-size: 14px; }
.course-code { font-size: 12px; color: var(--galaxy-text-secondary); font-family: 'JetBrains Mono'; }

.course-detail {
  background: var(--galaxy-card-solid); border: 1px solid var(--galaxy-border);
  border-radius: 12px; padding: 24px; min-height: 400px;
}
.detail-header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.detail-header h2 { margin: 0; font-size: 22px; }
.course-code-tag { font-size: 12px; color: var(--galaxy-text-secondary); background: var(--galaxy-bg); padding: 4px 10px; border-radius: 4px; }

.stats-row { display: flex; gap: 24px; margin-bottom: 32px; }
.stat { display: flex; flex-direction: column; align-items: center; }
.stat-num { font-family: 'Space Grotesk'; font-size: 32px; font-weight: 700; color: var(--galaxy-accent); }
.stat-label { font-size: 13px; color: var(--galaxy-text-secondary); }

.section { margin-bottom: 32px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.section-header h3 { font-size: 16px; margin: 0; }
.section-empty { color: var(--galaxy-text-secondary); font-size: 14px; padding: 16px 0; }
.assignment-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; border-bottom: 1px solid var(--galaxy-border);
}
.assign-info { display: flex; align-items: center; gap: 8px; }
.assign-title { font-size: 14px; }
.assign-lang { font-size: 12px; color: var(--galaxy-text-secondary); }
</style>
