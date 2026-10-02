import request from '@/utils/request'

export async function createAppeal(submission_id: number, reason: string) {
  const res = await request.post(`/submissions/${submission_id}/appeals`, { reason })
  return res.data
}

export async function listPendingAppeals() {
  const res = await request.get('/appeals')
  return res.data
}

export async function myAppeals() {
  const res = await request.get('/appeals/mine')
  return res.data
}

export async function reviewAppeal(appeal_id: number, approved: boolean, comment: string, new_score: number | null) {
  const res = await request.post(`/appeals/${appeal_id}/review`, { approved, comment, new_score })
  return res.data
}
