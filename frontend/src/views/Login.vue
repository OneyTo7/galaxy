<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { register } from '@/api/auth'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const router = useRouter()
const isRegister = ref(false)
const form = reactive({ username: '', password: '', role: 'student', display_name: '' })
const loading = ref(false)

async function handleSubmit() {
  loading.value = true
  try {
    if (isRegister.value) {
      await register({ username: form.username, password: form.password, role: form.role, display_name: form.display_name })
      ElMessage.success('注册成功，请登录')
      isRegister.value = false
    } else {
      await auth.login(form.username, form.password)
      router.push('/')
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-left">
      <div class="left-bg-grid"></div>
      <div class="left-glow-1"></div>
      <div class="left-glow-2"></div>

      <div class="left-content">
        <div class="brand">
          <h1 class="brand-name">智学</h1>
          <p class="brand-tagline">AI 认知诊断实验教学平台</p>
        </div>

        <p class="brand-desc">不只是判对错，更看见学生怎么错、卡在哪个点，并给出针对性练习。</p>

        <div class="features">
          <div class="feature">
            <span class="feature-icon">✨</span>
            <div>
              <h4>AI 命题</h4>
              <p>一句话生成题面、用例、评分细则与参考实现</p>
            </div>
          </div>
          <div class="feature">
            <span class="feature-icon">🔍</span>
            <div>
              <h4>误区诊断</h4>
              <p>结构化归因，输出误区类型、证据与对应知识点</p>
            </div>
          </div>
          <div class="feature">
            <span class="feature-icon">🎯</span>
            <div>
              <h4>变式练习</h4>
              <p>换情境出题，针对同一知识点对症练习</p>
            </div>
          </div>
          <div class="feature">
            <span class="feature-icon">📊</span>
            <div>
              <h4>学情看板</h4>
              <p>误区分布与知识点薄弱可视化，教学有据可依</p>
            </div>
          </div>
        </div>

        <div class="tech-stack">
          <span>FastAPI</span>
          <span>Vue 3</span>
          <span>LangChain</span>
          <span>移动云 MoMA</span>
        </div>
      </div>
    </div>

    <div class="login-right">
      <div class="login-card">
        <h2>{{ isRegister ? '注册账号' : '登录' }}</h2>
        <p class="login-hint">{{ isRegister ? '选择角色，创建你的账号' : '输入账号密码开始使用' }}</p>
        <el-form :model="form" label-position="top" style="margin-top: 24px">
          <el-form-item label="用户名">
            <el-input v-model="form.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password @keyup.enter="handleSubmit" />
          </el-form-item>
          <template v-if="isRegister">
            <el-form-item label="角色">
              <el-select v-model="form.role" style="width: 100%">
                <el-option label="学生" value="student" />
                <el-option label="教师" value="teacher" />
              </el-select>
            </el-form-item>
            <el-form-item label="姓名">
              <el-input v-model="form.display_name" placeholder="选填" />
            </el-form-item>
          </template>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="handleSubmit" style="width: 100%">
              {{ isRegister ? '注册' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>
        <p class="toggle-mode" @click="isRegister = !isRegister">
          {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: grid;
  grid-template-columns: 1fr 1fr;
  height: 100vh;
  overflow: hidden;
}

/* 左侧品牌区 */
.login-left {
  position: relative;
  background: linear-gradient(160deg, #1B2838 0%, #1E2F48 40%, #15202E 100%);
  display: flex;
  align-items: center;
  overflow: hidden;
}

.left-bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(91, 127, 255, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(91, 127, 255, 0.06) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, #000 30%, transparent 80%);
  -webkit-mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, #000 30%, transparent 80%);
}

.left-glow-1 {
  position: absolute;
  width: 600px;
  height: 600px;
  top: -200px;
  left: -100px;
  background: radial-gradient(circle, rgba(91, 127, 255, 0.18) 0%, transparent 60%);
  border-radius: 50%;
}

.left-glow-2 {
  position: absolute;
  width: 500px;
  height: 500px;
  bottom: -150px;
  right: -100px;
  background: radial-gradient(circle, rgba(232, 163, 69, 0.12) 0%, transparent 60%);
  border-radius: 50%;
}

.left-content {
  position: relative;
  z-index: 1;
  padding: 64px;
  color: #fff;
  max-width: 520px;
}

.brand-name {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 64px;
  font-weight: 700;
  color: #5B7FFF;
  margin: 0;
  line-height: 1;
  letter-spacing: -0.03em;
}

.brand-tagline {
  font-size: 20px;
  color: #B0C4DE;
  margin: 14px 0 0;
  font-weight: 500;
}

.brand-desc {
  font-size: 15px;
  color: #78909C;
  margin: 8px 0 48px;
  line-height: 1.6;
  max-width: 420px;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 40px;
}

.feature {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.feature-icon {
  font-size: 20px;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(91, 127, 255, 0.12);
  border-radius: 10px;
}

.feature h4 {
  font-size: 15px;
  font-weight: 600;
  color: #E0E6ED;
  margin: 0 0 4px;
}

.feature p {
  font-size: 13px;
  color: #78909C;
  margin: 0;
  line-height: 1.5;
}

.tech-stack {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tech-stack span {
  font-family: 'JetBrains Mono';
  font-size: 11px;
  color: #5B7FFF;
  background: rgba(91, 127, 255, 0.1);
  border: 1px solid rgba(91, 127, 255, 0.2);
  padding: 3px 10px;
  border-radius: 20px;
}

/* 右侧登录区 */
.login-right {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--galaxy-bg);
  background-image:
    radial-gradient(ellipse 600px 400px at 50% 20%, rgba(91, 127, 255, 0.08) 0%, transparent 60%);
  padding: 24px;
}

.login-card {
  width: 400px;
  max-width: 100%;
  background: var(--galaxy-card-solid);
  border: 1px solid var(--galaxy-border);
  border-radius: 16px;
  padding: 40px;
  box-shadow: var(--shadow-lg);
}

.login-card h2 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 28px;
  margin: 0;
}

.login-hint {
  color: var(--galaxy-text-secondary);
  font-size: 14px;
  margin: 4px 0 0;
}

.toggle-mode {
  text-align: center;
  color: var(--galaxy-accent);
  font-size: 14px;
  cursor: pointer;
  margin: 16px 0 0;
}
.toggle-mode:hover { text-decoration: underline; }

@media (max-width: 768px) {
  .login-page { grid-template-columns: 1fr; }
  .login-left { display: none; }
}
</style>
