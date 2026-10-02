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
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 60px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: var(--galaxy-blur);
  -webkit-backdrop-filter: var(--galaxy-blur);
  border-bottom: 1px solid var(--galaxy-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.topbar-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.logo {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: var(--galaxy-accent);
  letter-spacing: -0.02em;
}

.logo-sub {
  font-size: 12px;
  color: var(--galaxy-text-secondary);
}

.topbar-nav {
  display: flex;
  gap: 4px;
}

.topbar-nav a {
  text-decoration: none;
  color: var(--galaxy-text-secondary);
  font-size: 14px;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 8px;
  transition: all 0.15s;
}

.topbar-nav a:hover {
  background: var(--galaxy-accent-soft);
  color: var(--galaxy-accent);
}

.topbar-nav a.active {
  background: var(--galaxy-accent-soft);
  color: var(--galaxy-accent);
  font-weight: 600;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-tag {
  font-size: 12px;
  color: var(--galaxy-accent);
  background: var(--galaxy-accent-soft);
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
}

.content {
  padding: 40px 24px;
  max-width: 1100px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
</style>
