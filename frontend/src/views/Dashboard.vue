<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="dashboard">
    <div class="hero">
      <h1>欢迎回来</h1>
      <p class="hero-sub">当前角色：{{ auth.role }}。在这里看见学生怎么错、对症下药。</p>
    </div>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">提交数</div>
        <div class="stat-value">—</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">平均分</div>
        <div class="stat-value">—</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">误区类型</div>
        <div class="stat-value">—</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">知识点覆盖</div>
        <div class="stat-value">—</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hero {
  margin-bottom: 32px;
}

.hero h1 {
  font-size: 32px;
  margin: 0 0 8px;
}

.hero-sub {
  color: var(--galaxy-text-secondary);
  font-size: 15px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: var(--galaxy-card);
  border: 1px solid var(--galaxy-border);
  border-radius: 8px;
  padding: 24px;
}

.stat-label {
  font-size: 13px;
  color: var(--galaxy-text-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: var(--galaxy-text);
}
</style>
