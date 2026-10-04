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
  <div class="login-shell">
    <!-- 品牌侧 -->
    <section class="brand-side">
      <div class="brand-inner">
        <div class="brand-row">
          <div class="brand-mark">
            <el-icon><Opportunity /></el-icon>
          </div>
          <div class="brand-name-block">
            <span class="brand-name">智学</span>
            <span class="brand-sub">AI 认知诊断实验教学平台</span>
          </div>
        </div>

        <div class="brand-hero">
          <h1 class="hero-title">不只是判对错<br/>更看见学生<span class="hero-emph">怎么错</span></h1>
          <p class="hero-desc">从 AI 命题到沙箱评测、误区诊断、变式练习，再到班级学情看板，一条链路看见每个学生的认知成长。</p>
        </div>

        <div class="feature-grid">
          <div class="feature-cell rise-in" style="--enter-idx:0">
            <div class="feature-ico blue"><el-icon><MagicStick /></el-icon></div>
            <div class="feature-body">
              <h4>AI 命题</h4>
              <p>一句话生成题面、测试用例、评分细则与参考实现</p>
            </div>
          </div>
          <div class="feature-cell rise-in" style="--enter-idx:1">
            <div class="feature-ico violet"><el-icon><Aim /></el-icon></div>
            <div class="feature-body">
              <h4>误区诊断</h4>
              <p>结构化归因，输出误区类型、证据与对应知识点</p>
            </div>
          </div>
          <div class="feature-cell rise-in" style="--enter-idx:2">
            <div class="feature-ico green"><el-icon><Refresh /></el-icon></div>
            <div class="feature-body">
              <h4>变式练习</h4>
              <p>换情境出题，针对同一知识点对症练习并闭环克服</p>
            </div>
          </div>
          <div class="feature-cell rise-in" style="--enter-idx:3">
            <div class="feature-ico amber"><el-icon><DataAnalysis /></el-icon></div>
            <div class="feature-body">
              <h4>学情看板</h4>
              <p>知识点掌握度热力图，教学有据可依</p>
            </div>
          </div>
        </div>
      </div>
      <div class="brand-foot">校园方向 · 参赛作品</div>
    </section>

    <!-- 登录侧 -->
    <section class="form-side">
      <div class="login-card rise-in" style="--enter-idx:1">
        <div class="card-head">
          <h2>{{ isRegister ? '注册账号' : '欢迎回来' }}</h2>
          <p class="hint">{{ isRegister ? '选择角色，创建你的账号' : '登录以进入教学/学习工作台' }}</p>
        </div>
        <el-form :model="form" label-position="top" style="margin-top: 8px">
          <el-form-item label="用户名">
            <el-input v-model="form.username" placeholder="请输入用户名">
              <template #prefix><el-icon><User /></el-icon></template>
            </el-input>
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password @keyup.enter="handleSubmit">
              <template #prefix><el-icon><Lock /></el-icon></template>
            </el-input>
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
            <el-button type="primary" :loading="loading" @click="handleSubmit" style="width: 100%; height: 42px; font-size: 15px">
              {{ isRegister ? '注册' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>
        <p class="toggle" @click="isRegister = !isRegister">
          {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
        </p>

        <div class="demo-hint">
          <div class="demo-label">演示账号</div>
          <div class="demo-row" @click="form.username = 'teacher1'; form.password = '123456'">
            <el-icon><Avatar /></el-icon>
            <span>teacher1 / 123456（教师）</span>
          </div>
          <div class="demo-row" @click="form.username = 'studentA'; form.password = '123456'">
            <el-icon><Avatar /></el-icon>
            <span>studentA / 123456（学生）</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.login-shell {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  min-height: 100vh;
}

/* ---------- 品牌侧 ---------- */
.brand-side {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 56px 64px 40px;
  background:
    radial-gradient(700px 380px at 90% 8%, rgba(96, 165, 250, 0.28), transparent 60%),
    radial-gradient(560px 320px at 8% 96%, rgba(79, 124, 255, 0.22), transparent 55%),
    var(--grad-deep);
  color: #E6ECFF;
  overflow: hidden;
}
.brand-side::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle at 1px 1px, rgba(166, 177, 212, 0.10) 1px, transparent 0);
  background-size: 32px 32px;
  pointer-events: none;
  opacity: 0.5;
}

.brand-inner { position: relative; z-index: 1; max-width: 540px; }
.brand-row { display: flex; align-items: center; gap: 14px; margin-bottom: 56px; }
.brand-mark {
  width: 52px; height: 52px;
  border-radius: 14px;
  background: var(--grad-primary);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 26px;
  box-shadow: 0 10px 30px rgba(79, 124, 255, 0.45);
}
.brand-name-block { display: flex; flex-direction: column; line-height: 1.2; }
.brand-name { font-size: 24px; font-weight: 700; color: #fff; letter-spacing: 0.02em; }
.brand-sub { font-size: 12px; color: #A6B1D4; margin-top: 3px; }

.brand-hero { margin-bottom: 48px; }
.hero-title {
  font-size: 40px; font-weight: 700; line-height: 1.18; letter-spacing: -0.02em;
  color: #fff; margin: 0 0 20px;
}
.hero-emph {
  background: linear-gradient(120deg, #8AB0FF, #60A5FA);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-desc { font-size: 15px; line-height: 1.7; color: #B8C2E4; max-width: 460px; margin: 0; }

.feature-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.feature-cell {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 18px;
  border-radius: 14px;
  background: rgba(122, 146, 255, 0.07);
  border: 1px solid rgba(148, 166, 214, 0.16);
  backdrop-filter: blur(8px);
  transition: transform var(--duration) var(--ease), background var(--duration) var(--ease);
}
.feature-cell:hover { transform: translateY(-2px); background: rgba(122, 146, 255, 0.12); }
.feature-ico {
  width: 38px; height: 38px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.feature-ico.blue { background: rgba(79, 124, 255, 0.22); color: #8AB0FF; }
.feature-ico.violet { background: rgba(139, 124, 246, 0.22); color: #B0A4FF; }
.feature-ico.green { background: rgba(18, 183, 106, 0.22); color: #6EE7B7; }
.feature-ico.amber { background: rgba(245, 158, 11, 0.22); color: #FCD34D; }
.feature-body h4 { margin: 0 0 4px; font-size: 14px; font-weight: 600; color: #fff; }
.feature-body p { margin: 0; font-size: 12px; line-height: 1.55; color: #A6B1D4; }

.brand-foot {
  position: relative; z-index: 1;
  font-size: 12px; color: #6B7BA8; letter-spacing: 0.06em;
}

/* ---------- 登录侧 ---------- */
.form-side {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background:
    radial-gradient(600px 360px at 50% 0%, rgba(79, 124, 255, 0.05), transparent 60%),
    var(--bg-page);
}

.login-card {
  width: 400px;
  max-width: 100%;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 36px 32px 28px;
  box-shadow: var(--shadow-2);
}

.card-head h2 { margin: 0 0 4px; font-size: 24px; font-weight: 700; color: var(--ink); }
.hint { margin: 0; font-size: 13px; color: var(--text-secondary); }

.toggle {
  text-align: center;
  color: var(--primary);
  font-size: 13px;
  cursor: pointer;
  margin: 14px 0 18px;
  transition: color var(--duration) var(--ease);
}
.toggle:hover { color: var(--primary-hover); }

.demo-hint {
  border-top: 1px dashed var(--border);
  padding-top: 14px;
  margin-top: 4px;
}
.demo-label { font-size: 11px; color: var(--text-placeholder); letter-spacing: 0.1em; margin-bottom: 8px; }
.demo-row {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 10px; border-radius: 8px;
  font-size: 12px; color: var(--ink-2);
  cursor: pointer;
  transition: background var(--duration) var(--ease);
}
.demo-row:hover { background: var(--bg-hover); color: var(--primary); }
.demo-row .el-icon { font-size: 14px; color: var(--primary); }

@media (max-width: 900px) {
  .login-shell { grid-template-columns: 1fr; }
  .brand-side { display: none; }
  .form-side { padding: 24px 16px; }
}
</style>
