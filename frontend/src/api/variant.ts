import request from '@/utils/request'

export async function generateVariant(submission_id: number) {
  const res = await request.post(`/submissions/${submission_id}/variant`)
  return res.data
}

export async function getVariants(submission_id: number) {
  const res = await request.get(`/submissions/${submission_id}/variants`)
  return res.data
}
