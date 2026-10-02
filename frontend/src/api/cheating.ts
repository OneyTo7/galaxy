import request from '@/utils/request'

export async function checkCheating(submission_id: number) {
  const res = await request.post(`/submissions/${submission_id}/cheating-check`)
  return res.data
}

export async function getCheatingReports(submission_id: number) {
  const res = await request.get(`/submissions/${submission_id}/cheating-reports`)
  return res.data
}
