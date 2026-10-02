import request from '@/utils/request'

export async function submit(assignment_id: number, code: string, lang: string) {
  const res = await request.post('/submissions', { assignment_id, code, lang })
  return res.data
}

export async function getEvaluation(submission_id: number) {
  const res = await request.get(`/submissions/${submission_id}/evaluation`)
  return res.data
}

export async function listMySubmissions() {
  const res = await request.get('/submissions/mine')
  return res.data
}
