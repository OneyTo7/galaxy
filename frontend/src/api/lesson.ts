import request from '@/utils/request'

export interface LessonListItem {
  id: number
  course_id: number
  title: string
  sort_order: number
  assignment_id: number | null
}

export interface LessonOut extends LessonListItem {
  content: string
  created_at: string
}

export async function listLessons(courseId: number) {
  const res = await request.get(`/courses/${courseId}/lessons`)
  return res.data as LessonListItem[]
}

export async function getLesson(lessonId: number) {
  const res = await request.get(`/lessons/${lessonId}`)
  return res.data as LessonOut
}
