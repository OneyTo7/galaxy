<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { listMyCourses, listCourseAssignments, listCourseStudents } from '@/api/organization'
import { listMySubmissions } from '@/api/submission'
import { ElMessage } from 'element-plus'

interface Course { id: number; name: string; code: string; teacher_id: number; created_at: string }
interface CourseAssign { id: number; title: string; status: string; lang: string }
interface MySubmission { id: number; assignment_id: number; status: string; score: number }

const auth = useAuthStore()
const router = useRouter()
const courses = ref<Course[]>([])
const loading = ref(false)
const selectedCourse = ref<Course | null>(null)
const assignments = ref<CourseAssign[]>([])
const students = ref<[number, string][]>([])
const mySubmissions = ref<MySubmission[]>([])
const detailLoading = ref(false)

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
  assignments.value = []
  students.value = []
  mySubmissions.value = []
  try {
    const [a, s] = await Promise.all([
      listCourseAssignments(c.id),
      auth.role === 'teacher' ? listCourseStudents(c.id) : Promise.resolve([]),
    ])
    assignments.value = a
    students.value = s
    if (auth.role === 'student') {
      const allSubs = await listMySubmissions()
      mySubmissions.value = allSubs as MySubmission[]
    }
  } catch (e) { console.error('加载课程详情失败', e) }
  finally { detailLoading.value = false }
}

const publishedAssignments = computed(() => assignments.value.filter(a => a.status === 'published'))
const completedCount = computed(() => publishedAssignments.value.filter(a => mySubmissions.value.some(s => s.assignment_id === a.id && s.status === 'done')).length)
const myAvgScore = computed(() => {
  const done = mySubmissions.value.filter(s => s.status === 'done')
  if (!done.length) return 0
  return Math.round(done.reduce((sum, s) => sum + s.score, 0) / done.length)
})
const assignmentProgress = computed(() => {
  return publishedAssignments.value.map(a => {
    const sub = mySubmissions.value.find(s => s.assignment_id === a.id && s.status === 'done')
    return { ...a, submitted: !!sub, score: sub?.score ?? null }
  })
})
const progressPercent = computed(() => {
  if (!publishedAssignments.value.length) return 0
  return Math.round((completedCount.value / publishedAssignments.value.length) * 100)
})

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
        <div v-for="c in courses" :key="c.id" class="course-item" :class="{ active: selectedCourse?.id === c.id }" @click="selectCourse(c)">
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

          <!-- 统计卡片：左色条 + 大数据数字 -->
          <div class="stats-grid">
            <div class="stat-card" style="--bar-color: var(--galaxy-accent)">
              <span class="stat-num">{{ assignments.length }}</span>
              <span class="stat-label">作业总数</span>
            </div>
            <div v-if="auth.role === 'teacher'" class="stat-card" style="--bar-color: var(--galaxy-cyan)">
              <span class="stat-num">{{ students.length }}</span>
              <span class="stat-label">选课学生</span>
            </div>
            <div v-if="auth.role === 'student'" class="stat-card" style="--bar-color: var(--galaxy-cyan)">
              <span class="stat-num">{{ completedCount }}<span class="stat-sub">/{{ publishedAssignments.length }}</span></span>
              <span class="stat-label">已完成</span>
            </div>
            <div v-if="auth.role === 'student' && mySubmissions.length" class="stat-card" style="--bar-color: var(--galaxy-purple)">
              <span class="stat-num">{{ myAvgScore }}</span>
              <span class="stat-label">平均分</span>
            </div>
            <div class="stat-card" style="--bar-color: var(--galaxy-success)">
              <span class="stat-num">{{ publishedAssignments.length }}</span>
              <span class="stat-label">已发布</span>
            </div>
          </div>

          <!-- 学生：进度条 -->
          <div v-if="auth.role === 'student' && publishedAssignments.length" class="progress-section">
            <div class="progress-header">
              <span>完成进度</span>
              <span class="progress-num">{{ progressPercent }}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>
          </div>

          <!-- 学生：作业进度列表 -->
          <div v-if="auth.role === 'student'" class="section">
            <h3>作业进度</h3>
            <div v-if="assignmentProgress.length === 0" class="section-empty">暂无已发布作业</div>
            <div v-for="a in assignmentProgress" :key="a.id" class="assignment-row">
              <div class="assign-info">
                <span class="assign-title">{{ a.title }}</span>
                <el-tag v-if="a.submitted" type="success" size="small">{{ a.score }}分</el-tag>
                <el-tag v-else type="warning" size="small">未提交</el-tag>
              </div>
              <el-button v-if="!a.submitted" size="small" type="primary" @click="router.push(`/submit?assignment=${a.id}`)">去做</el-button>
              <el-button v-else size="small" @click="router.push('/my-submissions')">查看</el-button>
            </div>
          </div>

          <!-- 教师：作业管理 + 学情入口 -->
          <div v-if="auth.role === 'teacher' && assignments.length" class="section">
            <div class="section-header">
              <h3>课程作业</h3>
              <div class="section-actions">
                <el-button size="small" @click="router.push('/learning-report')">学情看板</el-button>
                <el-button size="small" type="primary" @click="router.push('/assignment-generate')">AI命题</el-button>
              </div>
            </div>
            <div v-if="assignments.length === 0" class="section-empty">暂无作业</div>
            <div v-for="a in assignments" :key="a.id" class="assignment-row">
              <div class="assign-info">
                <span class="assign-title">{{ a.title }}</span>
                <el-tag :type="a.status === 'published' ? 'success' : 'info'" size="small">{{ a.status === 'published' ? '已发布' : '草稿' }}</el-tag>
              </div>
            </div>
          </div>

          <!-- 教师：选课学生 -->
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
.desc { color: var(--galaxy-text-secondary); font-size: var(--fs-caption); margin: 0 0 24px; }
.empty { text-align: center; padding: 60px 0; }
.empty-text { color: var(--galaxy-text-secondary); margin-bottom: 16px; }

.layout { display: grid; grid-template-columns: 240px 1fr; gap: 16px; }
.course-list { display: flex; flex-direction: column; gap: 8px; }
.course-item { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: var(--radius-md); padding: 14px 16px; cursor: pointer; transition: all 0.15s; }
.course-item:hover { border-color: var(--galaxy-accent); background: var(--galaxy-card-hover); }
.course-item.active { border-color: var(--galaxy-accent); background: var(--galaxy-accent-soft); }
.course-item h4 { margin: 0 0 4px; font-size: 14px; color: var(--galaxy-text); }
.course-code { font-size: 12px; color: var(--galaxy-text-tertiary); font-family: 'JetBrains Mono'; }

.course-detail { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: var(--radius-lg); padding: 24px; min-height: 400px; }
.detail-header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.course-code-tag { font-size: 12px; color: var(--galaxy-text-tertiary); background: var(--galaxy-bg); padding: 4px 10px; border-radius: 4px; font-family: 'JetBrains Mono'; }

/* 统计卡片：左色条 + 大数据 */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 24px; }
.stat-card {
  background: var(--galaxy-bg);
  border: 1px solid var(--galaxy-border);
  border-left: 3px solid var(--bar-color, var(--galaxy-accent));
  border-radius: var(--radius-sm);
  padding: 16px 20px;
  transition: all 0.15s;
}
.stat-card:hover { border-color: var(--galaxy-border); border-left-color: var(--bar-color); box-shadow: var(--shadow-md); transform: translateY(-1px); }
.stat-num { font-family: 'Space Grotesk'; font-size: var(--fs-data); font-weight: 700; color: var(--galaxy-text); display: block; line-height: 1.1; }
.stat-sub { font-size: 20px; color: var(--galaxy-text-tertiary); font-weight: 500; }
.stat-label { font-size: var(--fs-small); color: var(--galaxy-text-tertiary); margin-top: 4px; display: block; }

/* 进度条 */
.progress-section { margin-bottom: 24px; }
.progress-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: var(--fs-caption); color: var(--galaxy-text-secondary); }
.progress-num { font-family: 'Space Grotesk'; font-weight: 700; color: var(--galaxy-accent); }
.progress-track { height: 8px; background: var(--galaxy-bg); border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--galaxy-accent), var(--galaxy-cyan)); border-radius: 4px; transition: width 0.5s; box-shadow: 0 0 8px rgba(91, 127, 255, 0.3); }

.section { margin-bottom: 24px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.section-actions { display: flex; gap: 8px; }
.section-empty { color: var(--galaxy-text-tertiary); font-size: 14px; padding: 16px 0; }
.assignment-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--galaxy-border-soft); }
.assign-info { display: flex; align-items: center; gap: 8px; }
.assign-title { font-size: 14px; color: var(--galaxy-text); }

@media (max-width: 768px) {
  .layout { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
