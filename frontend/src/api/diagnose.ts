import request from '@/utils/request'

export async function diagnose(submission_id: number) {
  const res = await request.post(`/submissions/${submission_id}/diagnose`)
  return res.data
}

export async function getDiagnosis(submission_id: number) {
  const res = await request.get(`/submissions/${submission_id}/diagnosis`)
  return res.data
}
