import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { login as loginApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const role = ref<string>(localStorage.getItem('role') || '')
  const isLoggedIn = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const res = await loginApi(username, password)
    let decodedRole = ''
    try {
      const payload = JSON.parse(atob(res.access_token.split('.')[1]))
      decodedRole = payload.role || ''
    } catch {
      throw new Error('登录响应异常：Token 无法解析，请联系管理员')
    }
    if (!decodedRole) {
      throw new Error('登录响应异常：Token 缺少角色信息')
    }
    token.value = res.access_token
    role.value = decodedRole
    localStorage.setItem('token', token.value)
    localStorage.setItem('role', role.value)
  }

  function logout() {
    token.value = ''
    role.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('role')
  }

  return { token, role, isLoggedIn, login, logout }
})
