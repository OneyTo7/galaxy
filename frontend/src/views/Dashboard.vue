<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const roleLabel = computed(() => {
  const m: Record<string, string> = { student: '同学', teacher: '老师', admin: '管理员' }
  return m[auth.role] || auth.role
})

const studentActions = [
  { icon: '📝', title: '去做作业', desc: '查看可提交的作业', to: '/assignments' },
  { icon: '🔍', title: '误区诊断', desc: '看 AI 分析你的代码误区', to: '/diagnose' },
  { icon: '🎯', title: '变式练习', desc: '换情境练同类题', to: '/variant' },
  { icon: '📋', title: '我的提交', desc: '查看提交记录与成绩', to: '/my-submissions' },
]

const teacherActions = [
  { icon: '✨', title: 'AI 命题', desc: '一句话生成完整作业', to: '/assignment-generate' },
  { icon: '📊', title: '学情看板', desc: '看班级误区分布与薄弱点', to: '/learning-report' },
  { icon: '🛡️', title: '反作弊', desc: 'AI 代写检测', to: '/cheating' },
  { icon: '📈', title: '成绩册', desc: '生成成绩册', to: '/gradebook' },
]
</script>

<template>
  <div class="dashboard">
    <div class="welcome">
      <h1>你好，{{ roleLabel }}</h1>
      <p class="welcome-desc">在这里{{ auth.role === 'student' ? '做作业、看诊断、练变式' : '命题、看学情、管教学' }}。</p>
    </div>

    <div class="actions-grid">
      <div
        v-for="a in (auth.role === 'student' ? studentActions : teacherActions)"
        :key="a.to"
        class="action-card"
        @click="router.push(a.to)"
      >
        <span class="action-icon">{{ a.icon }}</span>
        <div class="action-text">
          <h3>{{ a.title }}</h3>
          <p>{{ a.desc }}</p>
        </div>
        <span class="action-arrow">→</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard { max-width: 1000px; }

.welcome { margin-bottom: 40px; }
.welcome h1 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 36px;
  margin: 0 0 8px;
}
.welcome-desc {
  color: var(--galaxy-text-secondary);
  font-size: 16px;
  margin: 0;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--galaxy-card);
  border: 1px solid var(--galaxy-border);
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-card:hover {
  border-color: var(--galaxy-accent);
  box-shadow: 0 4px 12px rgba(91, 127, 255, 0.1);
  transform: translateY(-1px);
}

.action-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.action-text h3 {
  margin: 0 0 4px;
  font-size: 17px;
}

.action-text p {
  margin: 0;
  color: var(--galaxy-text-secondary);
  font-size: 14px;
}

.action-arrow {
  color: var(--galaxy-text-secondary);
  font-size: 20px;
  transition: transform 0.2s;
}

.action-card:hover .action-arrow {
  color: var(--galaxy-accent);
  transform: translateX(4px);
}
</style>
