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
    { to: '/dashboard', label: '首页' },
    { to: '/assignments', label: '作业列表' },
    { to: '/my-submissions', label: '我的提交' },
    { to: '/submit', label: '提交作业' },
    { to: '/diagnose', label: '误区诊断' },
    { to: '/variant', label: '变式练习' },
    { to: '/appeal', label: '申诉' },
  ]
  if (auth.role === 'teacher') return [
    { to: '/dashboard', label: '首页' },
    { to: '/assignments', label: '我的作业' },
    { to: '/assignment-generate', label: 'AI命题' },
    { to: '/learning-report', label: '学情看板' },
    { to: '/appeal', label: '申诉' },
    { to: '/cheating', label: '反作弊' },
    { to: '/gradebook', label: '成绩册' },
  ]
  if (auth.role === 'admin') return [
    { to: '/dashboard', label: '首页' },
    { to: '/admin', label: '管理' },
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
      <div class="topbar-left">
        <span class="logo">智学</span>
        <span class="logo-sub">AI 认知诊断实验教学平台</span>
      </div>
      <nav class="topbar-nav">
        <router-link v-for="item in navItems" :key="item.to" :to="item.to" :class="{ active: route.path === item.to }">{{ item.label }}</router-link>
      </nav>
      <div class="topbar-right">
        <span class="role-tag">{{ roleLabel }}</span>
        <el-button text @click="logout">退出</el-button>
      </div>
    </header>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: var(--galaxy-bg);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
  background: var(--galaxy-card);
  border-bottom: 1px solid var(--galaxy-border);
}

.topbar-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.logo {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: var(--galaxy-accent);
}

.logo-sub {
  font-size: 13px;
  color: var(--galaxy-text-secondary);
}

.topbar-nav {
  display: flex;
  gap: 24px;
}

.topbar-nav a {
  text-decoration: none;
  color: var(--galaxy-text-secondary);
  font-size: 14px;
  font-weight: 500;
  padding: 8px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.topbar-nav a.active {
  color: var(--galaxy-accent);
  border-bottom-color: var(--galaxy-accent);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-tag {
  font-size: 12px;
  color: var(--galaxy-accent);
  background: rgba(91, 127, 255, 0.1);
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: 500;
}

.content {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
}
</style>
