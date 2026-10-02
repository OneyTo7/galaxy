import request from '@/utils/request'

export async function login(username: string, password: string) {
  const res = await request.post('/auth/login', { username, password })
  return res.data
}

export async function register(data: {
  username: string
  password: string
  role: string
  display_name?: string
}) {
  const res = await request.post('/auth/register', data)
  return res.data
}

export async function getMe() {
  const res = await request.get('/auth/me')
  return res.data
}
