import request from '@/utils/request'

export async function listAssignments() {
  const res = await request.get('/assignments')
  return res.data
}

export async function listPublished() {
  const res = await request.get('/assignments/published')
  return res.data
}

export async function publishAssignment(id: number) {
  const res = await request.put(`/assignments/${id}`, { status: 'published' })
  return res.data
}

export async function deleteAssignment(id: number) {
  const res = await request.delete(`/assignments/${id}`)
  return res.data
}

export async function getAssignment(id: number) {
  const res = await request.get(`/assignments/${id}`)
  return res.data
}

export async function generateAssignment(course_id: number | null, prompt: string) {
  const res = await request.post('/assignments/generate', { course_id, prompt })
  return res.data
}
