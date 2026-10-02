import request from '@/utils/request'

export async function generateGradebook(assignment_id: number) {
  const res = await request.post(`/assignments/${assignment_id}/gradebook`)
  return res.data
}

export async function getGradebook(assignment_id: number) {
  const res = await request.get(`/assignments/${assignment_id}/gradebook`)
  return res.data
}
