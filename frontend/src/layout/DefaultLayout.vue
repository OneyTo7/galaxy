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
      <div class="topbar-inner">
        <div class="brand">
          <span class="logo">智学</span>
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
  background: rgba(15, 25, 35, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--galaxy-border);
}

.topbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 56px;
}

.brand { flex-shrink: 0; }
.logo {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: var(--galaxy-accent);
  letter-spacing: -0.03em;
  text-shadow: 0 0 16px rgba(91, 127, 255, 0.3);
}

.nav { display: flex; gap: 2px; flex: 1; justify-content: center; }
.nav a {
  text-decoration: none;
  color: var(--galaxy-text-secondary);
  font-size: var(--fs-caption);
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 20px;
  transition: all 0.15s;
}
.nav a:hover { background: var(--galaxy-accent-soft); color: var(--galaxy-accent); }
.nav a.active { background: var(--galaxy-accent); color: #fff; font-weight: 600; box-shadow: 0 0 12px rgba(91, 127, 255, 0.3); }

.user-area { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.role-pill {
  font-size: var(--fs-small);
  color: var(--galaxy-accent);
  background: var(--galaxy-accent-soft);
  padding: 3px 12px;
  border-radius: 20px;
  font-weight: 600;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
  width: 100%;
}

@media (max-width: 768px) {
  .topbar-inner { padding: 0 16px; }
  .nav { overflow-x: auto; justify-content: flex-start; }
  .content { padding: 20px 16px; }
}
</style>
