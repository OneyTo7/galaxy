<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const roleLabel = computed(() => {
  const m: Record<string, string> = { student: '学生', teacher: '教师', admin: '管理员', assistant: '助教' }
  return m[auth.role] || auth.role
})

const navItems = computed(() => {
  if (auth.role === 'student') return [
    { to: '/dashboard', label: '我的课程' },
    { to: '/my-submissions', label: '我的提交' },
    { to: '/diagnose', label: '误区诊断' },
    { to: '/variant', label: '变式练习' },
    { to: '/appeal', label: '申诉' },
  ]
  if (auth.role === 'teacher') return [
    { to: '/dashboard', label: '我的课程' },
    { to: '/assignment-generate', label: 'AI命题' },
    { to: '/admin', label: '课程管理' },
    { to: '/learning-report', label: '学情看板' },
    { to: '/appeal', label: '申诉' },
    { to: '/cheating', label: '反作弊' },
    { to: '/gradebook', label: '成绩册' },
  ]
  if (auth.role === 'assistant') return [
    { to: '/dashboard', label: '我的课程' },
    { to: '/learning-report', label: '学情看板' },
    { to: '/appeal', label: '申诉初审' },
  ]
  if (auth.role === 'admin') return [
    { to: '/dashboard', label: '全校学情' },
    { to: '/admin', label: '用户管理' },
    { to: '/gradebook', label: '课程审核' },
    { to: '/audit', label: '审计日志' },
  ]
  return [{ to: '/dashboard', label: '首页' }]
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-layout">
    <header class="topbar">
      <div class="topbar-inner">
        <div class="brand">
          <span class="logo">智学</span>
          <span class="logo-sub">AI 认知诊断实验教学平台</span>
        </div>
        <nav class="nav">
          <router-link v-for="item in navItems" :key="item.to" :to="item.to" :class="{ active: route.path === item.to }">
            {{ item.label }}
          </router-link>
        </nav>
        <div class="user-area">
          <span class="role-pill">{{ roleLabel }}</span>
          <el-button text size="small" @click="logout">退出</el-button>
        </div>
      </div>
    </header>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-layout { min-height: 100vh; }

.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  height: 60px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}

.topbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
  height: 100%;
}

.brand { display: flex; align-items: baseline; gap: 8px; flex-shrink: 0; }
.logo { font-size: 20px; font-weight: 700; color: var(--primary); letter-spacing: -0.02em; }
.logo-sub { font-size: var(--fs-caption); color: var(--text-secondary); }

.nav { display: flex; gap: 4px; flex: 1; justify-content: center; }
.nav a {
  text-decoration: none;
  color: var(--text-secondary);
  font-size: var(--fs-body);
  font-weight: 500;
  padding: 8px 16px;
  border-bottom: 2px solid transparent;
  transition: all var(--duration) var(--ease);
}
.nav a:hover { color: var(--primary); }
.nav a.active { color: var(--primary); border-bottom-color: var(--primary); }

.user-area { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.role-pill {
  font-size: var(--fs-caption);
  color: var(--primary);
  background: rgba(79, 124, 255, 0.1);
  padding: 3px 12px;
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-lg);
  width: 100%;
}

@media (max-width: 768px) {
  .topbar-inner { padding: 0 var(--space-md); }
  .nav { overflow-x: auto; }
  .logo-sub { display: none; }
  .content { padding: var(--space-md); }
}
</style>
