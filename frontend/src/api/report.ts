import request from '@/utils/request'

export async function getAssignmentReport(assignment_id: number) {
  const res = await request.get(`/assignments/${assignment_id}/learning-report`)
  return res.data
}

export async function getCourseReport(course_id: number) {
  const res = await request.get(`/courses/${course_id}/learning-report`)
  return res.data
}

export async function getClassReport(class_id: number) {
  const res = await request.get(`/classes/${class_id}/learning-report`)
  return res.data
}
