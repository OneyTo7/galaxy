import request from '@/utils/request'

export async function listCourses() {
  const res = await request.get('/courses')
  return res.data
}

export async function createCourse(name: string, code: string) {
  const res = await request.post('/courses', { name, code })
  return res.data
}

export async function listClasses(courseId: number) {
  const res = await request.get(`/courses/${courseId}/classes`)
  return res.data
}

export async function createClass(courseId: number, name: string) {
  const res = await request.post(`/courses/${courseId}/classes`, { name })
  return res.data
}

export async function listEnrollments(classId: number) {
  const res = await request.get(`/classes/${classId}/enrollments`)
  return res.data
}

export async function enroll(classId: number) {
  const res = await request.post(`/classes/${classId}/enrollments`)
  return res.data
}
