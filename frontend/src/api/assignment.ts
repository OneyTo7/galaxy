import request from '@/utils/request'

export async function listAssignments() {
  const res = await request.get('/assignments')
  return res.data
}

export async function getAssignment(id: number) {
  const res = await request.get(`/assignments/${id}`)
  return res.data
}
