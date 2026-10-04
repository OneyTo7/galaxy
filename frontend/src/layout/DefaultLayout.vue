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

const displayName = computed(() => {
  const name = (auth as any).displayName || (auth as any).username || ''
  return name ? String(name).slice(0, 1).toUpperCase() : '学'
})

const navItems = computed(() => {
  if (auth.role === 'student') return [
    { to: '/dashboard', label: '我的课程', icon: 'Monitor' },
    { to: '/lessons', label: '课程讲义', icon: 'Reading' },
    { to: '/enroll', label: '选课', icon: 'Collection' },
    { to: '/my-submissions', label: '我的提交', icon: 'Document' },
    { to: '/my-grades', label: '我的成绩', icon: 'Trophy' },
    { to: '/diagnose', label: '误区诊断', icon: 'Aim' },
    { to: '/variant', label: '变式练习', icon: 'MagicStick' },
    { to: '/appeal', label: '申诉', icon: 'ChatDotSquare' },
  ]
  if (auth.role === 'teacher') return [
    { to: '/dashboard', label: '我的课程', icon: 'Monitor' },
    { to: '/lessons', label: '课程讲义', icon: 'Reading' },
    { to: '/assignment-generate', label: 'AI 命题', icon: 'MagicStick' },
    { to: '/admin', label: '课程管理', icon: 'School' },
    { to: '/learning-report', label: '学情看板', icon: 'DataAnalysis' },
    { to: '/appeal', label: '申诉', icon: 'ChatDotSquare' },
    { to: '/cheating', label: '反作弊', icon: 'Warning' },
    { to: '/gradebook', label: '成绩册', icon: 'Notebook' },
  ]
  if (auth.role === 'assistant') return [
    { to: '/dashboard', label: '我的课程', icon: 'Monitor' },
    { to: '/learning-report', label: '学情看板', icon: 'DataAnalysis' },
    { to: '/appeal', label: '申诉初审', icon: 'ChatDotSquare' },
  ]
  if (auth.role === 'admin') return [
    { to: '/dashboard', label: '全校学情', icon: 'DataAnalysis' },
    { to: '/admin', label: '用户管理', icon: 'School' },
    { to: '/gradebook', label: '课程审核', icon: 'Notebook' },
    { to: '/audit', label: '审计日志', icon: 'List' },
  ]
  return [{ to: '/dashboard', label: '首页', icon: 'Monitor' }]
})

const groupLabel = computed(() =>
  auth.role === 'teacher' || auth.role === 'assistant' || auth.role === 'admin' ? '教学工作台' : '学习空间'
)

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="side-brand">
        <div class="brand-mark">
          <el-icon><Opportunity /></el-icon>
        </div>
        <div class="brand-text">
          <span class="brand-name">智学</span>
          <span class="brand-sub">AI 认知诊断平台</span>
        </div>
      </div>

      <div class="side-group">{{ groupLabel }}</div>

      <nav class="side-nav">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="side-item"
          :class="{ active: route.path === item.to }"
        >
          <el-icon class="item-ico"><component :is="item.icon" /></el-icon>
          <span class="item-label">{{ item.label }}</span>
          <span class="item-bar" />
        </router-link>
      </nav>

      <div class="side-footer">
        <div class="user-chip">
          <span class="avatar">{{ displayName }}</span>
          <div class="user-meta">
            <span class="role-tag">{{ roleLabel }}</span>
          </div>
        </div>
        <button class="logout-btn" @click="logout">
          <el-icon><SwitchButton /></el-icon>
          <span>退出登录</span>
        </button>
      </div>
    </aside>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 232px 1fr;
  min-height: 100vh;
}

/* ---------- 侧栏 ---------- */
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, var(--side-bg) 0%, var(--side-bg-2) 100%);
  border-right: 1px solid var(--side-border);
  padding: 20px 14px 16px;
  z-index: 100;
}

.side-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 2px 8px 18px;
  border-bottom: 1px solid var(--side-border);
  margin-bottom: 14px;
}
.brand-mark {
  width: 38px; height: 38px;
  border-radius: 11px;
  background: var(--grad-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 19px;
  box-shadow: 0 4px 14px rgba(79, 124, 255, 0.4);
  flex-shrink: 0;
}
.brand-text { display: flex; flex-direction: column; line-height: 1.2; }
.brand-name { font-size: 17px; font-weight: 700; color: #fff; letter-spacing: 0.02em; }
.brand-sub { font-size: 11px; color: var(--side-text); margin-top: 2px; }

.side-group {
  font-size: 11px;
  color: #6B7BA8;
  letter-spacing: 0.12em;
  padding: 4px 10px 8px;
}

.side-nav { display: flex; flex-direction: column; gap: 2px; flex: 1; overflow-y: auto; }

.side-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 10px 12px;
  border-radius: 10px;
  color: var(--side-text);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background var(--duration) var(--ease), color var(--duration) var(--ease), transform var(--duration) var(--ease);
}
.side-item:hover {
  background: var(--side-hover);
  color: var(--side-text-active);
  transform: translateX(2px);
}
.side-item.active {
  background: var(--side-active);
  color: var(--side-text-active);
}
.item-ico { font-size: 17px; flex-shrink: 0; }
.item-bar {
  position: absolute;
  left: -14px;
  top: 50%;
  transform: translateY(-50%) scaleY(0);
  width: 3px; height: 22px;
  border-radius: 0 3px 3px 0;
  background: var(--primary);
  transition: transform 0.25s var(--ease);
}
.side-item.active .item-bar { transform: translateY(-50%) scaleY(1); }

/* ---------- 侧栏用户区 ---------- */
.side-footer {
  border-top: 1px solid var(--side-border);
  padding-top: 12px;
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.user-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 10px;
  background: rgba(122, 146, 255, 0.07);
}
.avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: var(--grad-primary);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.user-meta { display: flex; flex-direction: column; }
.role-tag {
  font-size: 12px;
  color: #fff;
  font-weight: 600;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: var(--side-text);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--duration) var(--ease);
}
.logout-btn:hover { background: rgba(239, 68, 68, 0.14); color: #FDA4AF; }
.logout-btn:active { transform: scale(0.97); }

/* ---------- 内容区 ---------- */
.content {
  min-width: 0;
  padding: 28px 32px 48px;
  background:
    radial-gradient(900px 420px at 85% -10%, rgba(96, 165, 250, 0.07), transparent 60%),
    radial-gradient(700px 380px at -10% 0%, rgba(79, 124, 255, 0.05), transparent 55%),
    var(--bg-page);
}

@media (max-width: 900px) {
  .app-shell { grid-template-columns: 1fr; }
  .sidebar {
    position: sticky;
    top: 0;
    height: auto;
    flex-direction: row;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    overflow-x: auto;
  }
  .side-brand { border: none; margin: 0; padding: 0 8px 0 0; }
  .brand-text { display: none; }
  .side-group { display: none; }
  .side-nav { flex-direction: row; gap: 4px; overflow-x: auto; }
  .side-item { padding: 8px 12px; white-space: nowrap; }
  .item-bar { display: none; }
  .side-footer { border: none; margin: 0; padding: 0; flex-direction: row; align-items: center; }
  .user-chip { background: transparent; padding: 0; }
  .user-meta { display: none; }
  .logout-btn { width: auto; padding: 8px; }
  .logout-btn span { display: none; }
  .content { padding: 18px 16px 40px; }
}
</style>
