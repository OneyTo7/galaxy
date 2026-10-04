import request from '@/utils/request'
import type {
  KnowledgePointOut,
  KnowledgeTagOut,
  MasteryMatrixOut,
  MasteryEventOut,
  StudentMasteryOut,
} from '@/types/api'

export async function getKnowledgePoints() {
  const res = await request.get('/knowledge-points')
  return res.data as KnowledgePointOut[]
}

export async function getAssignmentTags(assignmentId: number) {
  const res = await request.get(`/assignments/${assignmentId}/knowledge-points`)
  return res.data as KnowledgeTagOut[]
}

export async function updateAssignmentTags(
  assignmentId: number,
  items: { code: string; weight: number }[],
) {
  const res = await request.put(`/assignments/${assignmentId}/knowledge-points`, { items })
  return res.data as KnowledgeTagOut[]
}

export async function getMasteryMatrix(courseId: number) {
  const res = await request.get(`/courses/${courseId}/mastery-matrix`)
  return res.data as MasteryMatrixOut
}

export async function getStudentMastery(courseId: number, studentId: number) {
  const res = await request.get(`/students/${studentId}/mastery`, {
    params: { course_id: courseId },
  })
  return res.data as StudentMasteryOut
}

export async function getStudentMasteryEvents(courseId: number, studentId: number) {
  const res = await request.get(`/students/${studentId}/mastery/events`, {
    params: { course_id: courseId },
  })
  return res.data as MasteryEventOut[]
}

export async function getMyMastery(courseId: number) {
  const res = await request.get('/mastery/me', { params: { course_id: courseId } })
  return res.data as StudentMasteryOut
}
