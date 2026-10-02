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
      <div class="brand">
        <h1 class="brand-name">智学</h1>
        <p class="brand-tagline">AI 认知诊断实验教学平台</p>
        <p class="brand-desc">看见学生怎么错，对症下药</p>
      </div>
      <div class="features">
        <div class="feature">
          <span class="feature-num">01</span>
          <span>AI 命题：一句话生成题面、用例、评分细则</span>
        </div>
        <div class="feature">
          <span class="feature-num">02</span>
          <span>误区诊断：结构化归因，证据 + 知识点</span>
        </div>
        <div class="feature">
          <span class="feature-num">03</span>
          <span>变式练习：换情境出题，对症练习</span>
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
}

.login-left {
  background: linear-gradient(135deg, #1B2838 0%, #2B3D5C 50%, #1B2838 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 64px;
  color: #fff;
}

.brand-name {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 56px;
  font-weight: 700;
  color: #5B7FFF;
  margin: 0;
  line-height: 1;
}

.brand-tagline {
  font-size: 18px;
  color: #B0BEC5;
  margin: 12px 0 4px;
}

.brand-desc {
  font-size: 15px;
  color: #78909C;
  margin: 0 0 48px;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 15px;
  color: #CFD8DC;
}

.feature-num {
  font-family: 'Space Grotesk';
  font-size: 13px;
  font-weight: 700;
  color: #5B7FFF;
  background: rgba(91, 127, 255, 0.15);
  padding: 4px 10px;
  border-radius: 4px;
}

.login-right {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--galaxy-bg);
}

.login-card {
  width: 400px;
  background: var(--galaxy-card);
  border: 1px solid var(--galaxy-border);
  border-radius: 12px;
  padding: 40px;
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
