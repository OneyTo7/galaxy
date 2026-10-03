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
    <div class="brand-side">
      <div class="brand-content">
        <h1 class="brand-name">智学</h1>
        <p class="brand-tagline">AI 认知诊断实验教学平台</p>
        <p class="brand-desc">不只是判对错，更看见学生怎么错、卡在哪个点，并给出针对性练习。</p>
        <div class="features">
          <div class="feature">
            <h4>AI 命题</h4>
            <p>一句话生成题面、用例、评分细则与参考实现</p>
          </div>
          <div class="feature">
            <h4>误区诊断</h4>
            <p>结构化归因，输出误区类型、证据与对应知识点</p>
          </div>
          <div class="feature">
            <h4>变式练习</h4>
            <p>换情境出题，针对同一知识点对症练习</p>
          </div>
          <div class="feature">
            <h4>学情看板</h4>
            <p>误区分布与知识点薄弱可视化，教学有据可依</p>
          </div>
        </div>
      </div>
    </div>

    <div class="form-side">
      <div class="login-card">
        <h2>{{ isRegister ? '注册账号' : '登录' }}</h2>
        <p class="hint">{{ isRegister ? '选择角色，创建你的账号' : '输入账号密码开始使用' }}</p>
        <el-form :model="form" label-position="top" style="margin-top: var(--space-lg)">
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
        <p class="toggle" @click="isRegister = !isRegister">
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

.brand-side {
  background: linear-gradient(160deg, #F0F4FF 0%, #E8EDFF 50%, #F0F4FF 100%);
  display: flex;
  align-items: center;
  padding: var(--space-xl);
}

.brand-content { max-width: 460px; }

.brand-name { font-size: 48px; font-weight: 700; color: var(--primary); margin: 0; letter-spacing: -0.03em; }
.brand-tagline { font-size: var(--fs-h2); font-weight: 500; color: var(--text-primary); margin: var(--space-sm) 0 var(--space-xs); }
.brand-desc { font-size: var(--fs-body); color: var(--text-secondary); margin: 0 0 var(--space-xl); line-height: 1.6; }

.features { display: flex; flex-direction: column; gap: var(--space-md); }
.feature h4 { font-size: var(--fs-h3); font-weight: 500; color: var(--text-primary); margin: 0 0 4px; }
.feature p { font-size: var(--fs-body); color: var(--text-secondary); margin: 0; }

.form-side {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
  padding: var(--space-lg);
}

.login-card {
  width: 380px;
  max-width: 100%;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-xl) var(--space-lg);
  box-shadow: var(--shadow-card);
}

.login-card h2 { font-size: var(--fs-h1); font-weight: 600; margin: 0; }
.hint { font-size: var(--fs-body); color: var(--text-secondary); margin: 4px 0 0; }

.toggle {
  text-align: center;
  color: var(--primary);
  font-size: var(--fs-body);
  cursor: pointer;
  margin: var(--space-md) 0 0;
  transition: color var(--duration) var(--ease);
}
.toggle:hover { color: var(--primary-hover); }

@media (max-width: 768px) {
  .login-page { grid-template-columns: 1fr; }
  .brand-side { display: none; }
}
</style>
