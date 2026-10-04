<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { listMyCourses, listCourseAssignments, listCourseStudents } from '@/api/organization'
import { listMySubmissions } from '@/api/submission'

interface Course { id: number; name: string; code: string; teacher_id: number; created_at: string }
interface CourseAssign { id: number; title: string; status: string; lang: string; submitted?: boolean; score?: number | null }
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
  <div class="page">
    <div class="page-header">
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><Monitor /></el-icon></span>
        <div>
          <h1>我的课程</h1>
          <p class="page-desc">{{ auth.role === 'teacher' ? '管理你的课程、作业与班级学情。' : '查看你选的课程，做作业、看诊断、查成绩。' }}</p>
        </div>
      </div>
      <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/admin')">
        <el-icon style="margin-right: 4px"><Plus /></el-icon>创建课程
      </el-button>
    </div>

    <div v-if="!loading && courses.length === 0" class="empty-state-v2">
      <div class="empty-ico"><el-icon><FolderOpened /></el-icon></div>
      <p>{{ auth.role === 'teacher' ? '暂无课程，去创建一门吧' : '暂未选课' }}</p>
      <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/admin')">创建课程</el-button>
      <el-button v-else type="primary" @click="router.push('/enroll')">去选课</el-button>
    </div>

    <div v-else class="split-layout">
      <aside class="sidebar-col">
        <div class="side-title">
          <el-icon><Collection /></el-icon>
          <span>课程列表</span>
        </div>
        <div v-for="c in courses" :key="c.id" class="course-card" :class="{ active: selectedCourse?.id === c.id }" @click="selectCourse(c)">
          <div class="course-ico"><el-icon><Reading /></el-icon></div>
          <div class="course-meta">
            <h4>{{ c.name }}</h4>
            <span class="code">{{ c.code }}</span>
          </div>
          <span class="active-bar" />
        </div>
      </aside>

      <main class="main-col" v-loading="detailLoading">
        <template v-if="selectedCourse">
          <div class="detail-head">
            <div>
              <h2>{{ selectedCourse.name }}</h2>
              <span class="code-tag">{{ selectedCourse.code }}</span>
            </div>
            <el-button size="small" @click="router.push(`/lessons?course=${selectedCourse.id}`)">
              <el-icon style="margin-right:4px"><Reading /></el-icon>查看讲义
            </el-button>
          </div>

          <div class="stat-grid">
            <div class="stat-card-v2 rise-in" style="--enter-idx:0">
              <div class="stat-ico blue"><el-icon><Document /></el-icon></div>
              <div>
                <span class="stat-num-v2">{{ assignments.length }}</span>
                <span class="stat-label-v2">作业总数</span>
              </div>
            </div>
            <div v-if="auth.role === 'teacher'" class="stat-card-v2 rise-in" style="--enter-idx:1">
              <div class="stat-ico violet"><el-icon><User /></el-icon></div>
              <div>
                <span class="stat-num-v2">{{ students.length }}</span>
                <span class="stat-label-v2">选课学生</span>
              </div>
            </div>
            <div v-if="auth.role === 'student'" class="stat-card-v2 rise-in" style="--enter-idx:1">
              <div class="stat-ico green"><el-icon><CircleCheck /></el-icon></div>
              <div>
                <span class="stat-num-v2">{{ completedCount }}<span class="sub">/{{ publishedAssignments.length }}</span></span>
                <span class="stat-label-v2">已完成</span>
              </div>
            </div>
            <div v-if="auth.role === 'student' && mySubmissions.length" class="stat-card-v2 rise-in" style="--enter-idx:2">
              <div class="stat-ico amber"><el-icon><Trophy /></el-icon></div>
              <div>
                <span class="stat-num-v2">{{ myAvgScore }}</span>
                <span class="stat-label-v2">平均分</span>
              </div>
            </div>
            <div class="stat-card-v2 rise-in" style="--enter-idx:3">
              <div class="stat-ico blue"><el-icon><Promotion /></el-icon></div>
              <div>
                <span class="stat-num-v2">{{ publishedAssignments.length }}</span>
                <span class="stat-label-v2">已发布</span>
              </div>
            </div>
          </div>

          <div v-if="auth.role === 'student' && publishedAssignments.length" class="progress-panel rise-in" style="--enter-idx:4">
            <div class="progress-head">
              <span class="progress-label"><el-icon><DataLine /></el-icon> 完成进度</span>
              <span class="progress-num">{{ progressPercent }}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>
          </div>

          <div class="panel assign-panel rise-in" style="--enter-idx:5">
            <div class="section-title">
              <span class="title-ico"><el-icon><List /></el-icon></span>
              {{ auth.role === 'student' ? '作业进度' : '课程作业' }}
              <el-button v-if="auth.role === 'teacher'" size="small" type="primary" style="margin-left: auto" @click="router.push('/assignment-generate')">
                <el-icon style="margin-right: 4px"><MagicStick /></el-icon>AI 命题
              </el-button>
            </div>
            <div v-if="assignmentProgress.length === 0 && auth.role === 'student'" class="empty-inline">暂无已发布作业</div>
            <div v-if="assignments.length === 0 && auth.role === 'teacher'" class="empty-inline">暂无作业</div>
            <div v-for="a in (auth.role === 'student' ? assignmentProgress : assignments)" :key="a.id" class="assign-row">
              <div class="assign-info">
                <span class="assign-lang">{{ a.lang }}</span>
                <span class="assign-title">{{ a.title }}</span>
                <el-tag v-if="auth.role === 'student' && a.submitted" type="success" size="small">{{ a.score }}分</el-tag>
                <el-tag v-else-if="auth.role === 'student'" type="warning" size="small">未提交</el-tag>
                <el-tag v-else :type="a.status === 'published' ? 'success' : 'info'" size="small">{{ a.status === 'published' ? '已发布' : '草稿' }}</el-tag>
              </div>
              <el-button v-if="auth.role === 'student' && !a.submitted" size="small" type="primary" @click="router.push(`/submit?assignment=${a.id}`)">去做</el-button>
              <el-button v-if="auth.role === 'student' && a.submitted" size="small" @click="router.push('/my-submissions')">查看</el-button>
            </div>
          </div>

          <div v-if="auth.role === 'teacher' && students.length" class="panel rise-in" style="--enter-idx:6">
            <div class="section-title">
              <span class="title-ico"><el-icon><User /></el-icon></span>
              选课学生
            </div>
            <el-table :data="students.map(([id, cls]) => ({ student_id: id, class_name: cls }))" border size="small">
              <el-table-column prop="student_id" label="学生 ID" width="100" />
              <el-table-column prop="class_name" label="班级" />
            </el-table>
          </div>
        </template>
        <div v-else class="empty-state-v2">
          <div class="empty-ico"><el-icon><Loading /></el-icon></div>
          <p>加载中...</p>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.split-layout { display: grid; grid-template-columns: 260px 1fr; gap: 22px; align-items: start; }

.sidebar-col { position: sticky; top: 28px; }
.side-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; font-weight: 600; color: var(--text-secondary);
  letter-spacing: 0.06em; padding: 0 4px 12px;
}
.side-title .el-icon { font-size: 14px; color: var(--primary); }

.course-card {
  position: relative;
  display: flex; align-items: center; gap: 12px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all var(--duration) var(--ease);
}
.course-card:hover { border-color: var(--primary); box-shadow: var(--shadow-1); transform: translateY(-1px); }
.course-card.active { border-color: var(--primary); background: var(--bg-hover); }
.course-ico {
  width: 36px; height: 36px; border-radius: 10px;
  background: rgba(79, 124, 255, 0.10); color: var(--primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 17px; flex-shrink: 0;
}
.course-card.active .course-ico { background: var(--grad-primary); color: #fff; }
.course-meta h4 { margin: 0 0 2px; font-size: 14px; font-weight: 600; color: var(--ink); }
.code { font-size: 11px; color: var(--text-placeholder); font-family: 'SF Mono', monospace; }
.active-bar {
  position: absolute; left: 0; top: 50%; transform: translateY(-50%) scaleY(0);
  width: 3px; height: 28px; border-radius: 0 3px 3px 0;
  background: var(--primary); transition: transform 0.25s var(--ease);
}
.course-card.active .active-bar { transform: translateY(-50%) scaleY(1); }

.main-col { min-width: 0; }
.detail-head { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
.detail-head h2 { margin: 0 0 4px; }
.code-tag { font-size: 11px; color: var(--ink-2); background: var(--bg-hover); padding: 3px 10px; border-radius: var(--radius-sm); font-family: 'SF Mono', monospace; }

.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 18px; }

.progress-panel {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 16px 18px;
  box-shadow: var(--shadow-1); margin-bottom: 18px;
}
.progress-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 13px; color: var(--ink-2); }
.progress-label { display: flex; align-items: center; gap: 6px; font-weight: 500; }
.progress-label .el-icon { color: var(--primary); }
.progress-num { font-weight: 700; color: var(--primary); font-size: 16px; }
.progress-track { height: 8px; background: var(--bg-sunken); border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--grad-primary); border-radius: 4px; transition: width 0.6s var(--ease); }

.assign-panel { padding: 18px 20px; }
.empty-inline { color: var(--text-placeholder); font-size: 13px; padding: 18px 0; text-align: center; }
.assign-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 0; border-bottom: 1px solid var(--border);
}
.assign-row:last-child { border-bottom: none; }
.assign-info { display: flex; align-items: center; gap: 10px; }
.assign-lang {
  font-size: 10px; font-weight: 600; color: var(--primary);
  background: rgba(79, 124, 255, 0.10); padding: 2px 7px; border-radius: 4px;
  font-family: 'SF Mono', monospace; text-transform: uppercase;
}
.assign-title { font-size: 14px; color: var(--ink); font-weight: 500; }

@media (max-width: 900px) {
  .split-layout { grid-template-columns: 1fr; }
  .sidebar-col { position: static; }
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
