<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listLessons, getLesson, type LessonListItem, type LessonOut } from '@/api/lesson'
import { listMyCourses } from '@/api/organization'

const route = useRoute()
const router = useRouter()
const lessons = ref<LessonListItem[]>([])
const currentLesson = ref<LessonOut | null>(null)
const selectedId = ref<number | null>(null)
const loading = ref(false)
const courses = ref<{ id: number; name: string; code: string }[]>([])
const selectedCourseId = ref<number | null>(null)

async function loadCourses() {
  try {
    // 教师看自己的课程，学生看已选课程（都有 listMyCourses 端点）
    courses.value = await listMyCourses()
    // 优先用 query 参数的 course
    const qId = Number(route.query.course)
    if (qId && courses.value.some(c => c.id === qId)) {
      selectedCourseId.value = qId
    } else if (courses.value.length > 0) {
      selectedCourseId.value = courses.value[0].id
    }
  } catch (e) { console.error('加载课程列表失败', e) }
}

watch(selectedCourseId, (val) => {
  if (val) loadLessons()
})

async function loadLessons() {
  if (!selectedCourseId.value) return
  loading.value = true
  lessons.value = []
  currentLesson.value = null
  selectedId.value = null
  try {
    lessons.value = await listLessons(selectedCourseId.value)
    if (lessons.value.length > 0) {
      selectLesson(lessons.value[0].id)
    }
  } catch (e) { console.error('加载章节失败', e) }
  finally { loading.value = false }
}

async function selectLesson(id: number) {
  selectedId.value = id
  currentLesson.value = null
  try {
    currentLesson.value = await getLesson(id)
  } catch (e) { console.error('加载章节内容失败', e) }
}

// 简易 Markdown → HTML（不引入新依赖）
function renderMarkdown(md: string): string {
  if (!md) return ''
  let html = md
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="md-code-block"><code>$2</code></pre>')
    .replace(/^### (.+)$/gm, '<h4 class="md-h4">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 class="md-h3">$1</h3>')
    .replace(/^# (.+)$/gm, '<h2 class="md-h2">$1</h2>')
    .replace(/`([^`]+)`/g, '<code class="md-inline-code">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>')
    .split('\n\n')
    .map(block => {
      if (block.startsWith('<')) return block
      return `<p class="md-p">${block.replace(/\n/g, '<br/>')}</p>`
    })
    .join('\n')
  return html
}

const renderedContent = computed(() => renderMarkdown(currentLesson.value?.content || ''))

onMounted(loadCourses)
</script>

<template>
  <div class="page" v-loading="loading">
    <div class="page-header">
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><Reading /></el-icon></span>
        <div>
          <h1>课程讲义</h1>
          <p class="page-desc">先看课本理解概念，再做对应练习题。</p>
        </div>
      </div>
      <el-select
        v-model="selectedCourseId"
        placeholder="选择课程"
        style="width: 280px"
      >
        <el-option
          v-for="c in courses"
          :key="c.id"
          :label="c.name"
          :value="c.id"
        />
      </el-select>
    </div>

    <div v-if="courses.length === 0 && !loading" class="empty-state-v2">
      <div class="empty-ico"><el-icon><Document /></el-icon></div>
      <p>暂无课程</p>
    </div>

    <div v-else-if="lessons.length === 0 && !loading" class="empty-state-v2">
      <div class="empty-ico"><el-icon><Document /></el-icon></div>
      <p>该课程暂无章节内容</p>
    </div>

    <div v-else class="split-layout">
      <!-- 左侧章节目录 -->
      <aside class="sidebar-col">
        <div class="panel toc-panel">
          <div class="section-title"><span class="title-ico"><el-icon><Collection /></el-icon></span>章节目录</div>
          <div class="toc-list">
            <div
              v-for="l in lessons"
              :key="l.id"
              class="toc-item"
              :class="{ active: selectedId === l.id }"
              @click="selectLesson(l.id)"
            >
              <span class="toc-num">{{ l.sort_order }}</span>
              <span class="toc-title">{{ l.title }}</span>
              <el-icon v-if="l.assignment_id" class="toc-link-icon"><Promotion /></el-icon>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧内容 -->
      <main class="main-col">
        <div v-if="currentLesson" class="panel lesson-panel rise-in" :key="currentLesson.id">
          <div class="lesson-header">
            <h2>{{ currentLesson.title }}</h2>
            <el-button
              v-if="currentLesson.assignment_id"
              type="primary"
              size="small"
              @click="router.push(`/submit?assignment=${currentLesson.assignment_id}`)"
            >
              <el-icon style="margin-right:4px"><Promotion /></el-icon>去做练习
            </el-button>
          </div>
          <div class="lesson-content" v-html="renderedContent"></div>
        </div>
        <div v-else class="empty-state-v2">
          <div class="empty-ico"><el-icon><Loading /></el-icon></div>
          <p>加载中...</p>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.split-layout { display: grid; grid-template-columns: 280px 1fr; gap: 22px; align-items: start; }

.sidebar-col { position: sticky; top: 28px; }
.toc-panel { padding: 16px 14px; max-height: calc(100vh - 160px); overflow-y: auto; }
.toc-list { display: flex; flex-direction: column; gap: 2px; }
.toc-item {
  display: flex; align-items: center; gap: 8px;
  padding: 9px 12px; border-radius: var(--radius-md);
  cursor: pointer; transition: all var(--duration) var(--ease);
}
.toc-item:hover { background: var(--bg-hover); }
.toc-item.active { background: var(--bg-hover); border-left: 3px solid var(--primary); }
.toc-num {
  width: 22px; height: 22px; border-radius: 6px;
  background: var(--bg-sunken); color: var(--text-secondary);
  font-size: 11px; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.toc-item.active .toc-num { background: var(--grad-primary); color: #fff; }
.toc-title { font-size: 13px; color: var(--ink); flex: 1; }
.toc-item.active .toc-title { color: var(--primary); font-weight: 600; }
.toc-link-icon { font-size: 13px; color: var(--success); flex-shrink: 0; }

.main-col { min-width: 0; }
.lesson-panel { padding: 28px 32px; }
.lesson-header { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
.lesson-header h2 { margin: 0; }

/* Markdown 渲染样式 */
.lesson-content { font-size: 14px; line-height: 1.8; color: var(--ink-2); }
:deep(.md-h2) { font-size: 20px; font-weight: 700; color: var(--ink); margin: 24px 0 12px; }
:deep(.md-h3) { font-size: 16px; font-weight: 600; color: var(--ink); margin: 20px 0 10px; }
:deep(.md-h4) { font-size: 14px; font-weight: 600; color: var(--ink-2); margin: 16px 0 8px; }
:deep(.md-p) { margin: 0 0 14px; line-height: 1.75; }
:deep(.md-inline-code) {
  font-family: 'SF Mono', Menlo, Consolas, monospace; font-size: 13px;
  background: var(--bg-sunken); padding: 2px 6px; border-radius: 4px;
  color: var(--primary);
}
:deep(.md-code-block) {
  font-family: 'SF Mono', Menlo, Consolas, monospace; font-size: 13px;
  background: #1B2548; color: #C8D4F4;
  padding: 14px 18px; border-radius: 10px; overflow-x: auto;
  margin: 0 0 16px; line-height: 1.6;
}
:deep(.md-code-block code) { background: none; color: inherit; padding: 0; }
:deep(ul) { margin: 0 0 14px; padding-left: 22px; }
:deep(li) { margin: 4px 0; line-height: 1.7; }
:deep(strong) { color: var(--ink); font-weight: 600; }

@media (max-width: 900px) {
  .split-layout { grid-template-columns: 1fr; }
  .sidebar-col { position: static; max-height: none; }
}
</style>
