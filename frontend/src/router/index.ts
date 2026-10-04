import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('@/views/Login.vue') },
    {
      path: '/',
      component: () => import('@/layout/DefaultLayout.vue'),
      children: [
        { path: '', redirect: '/dashboard' },
        // 通用（所有登录用户）
        { path: 'dashboard', name: 'dashboard', component: () => import('@/views/Dashboard.vue') },
        { path: 'appeal', name: 'appeal', component: () => import('@/views/Appeal.vue'), meta: { roles: ['student', 'teacher', 'assistant'] } },
        // 学生专属
        { path: 'my-submissions', name: 'my-submissions', component: () => import('@/views/student/MySubmissions.vue'), meta: { roles: ['student'] } },
        { path: 'enroll', name: 'enroll', component: () => import('@/views/student/CourseEnroll.vue'), meta: { roles: ['student'] } },
        { path: 'my-grades', name: 'my-grades', component: () => import('@/views/student/MyGrades.vue'), meta: { roles: ['student'] } },
        { path: 'submit', name: 'submit', component: () => import('@/views/student/Submit.vue'), meta: { roles: ['student'] } },
        { path: 'diagnose', name: 'diagnose', component: () => import('@/views/student/Diagnose.vue'), meta: { roles: ['student'] } },
        { path: 'variant', name: 'variant', component: () => import('@/views/student/Variant.vue'), meta: { roles: ['student'] } },
        { path: 'assignments', name: 'assignments', component: () => import('@/views/AssignmentList.vue') },
        // 教师/助教专属
        { path: 'learning-report', name: 'learning-report', component: () => import('@/views/teacher/LearningDashboard.vue'), meta: { roles: ['teacher', 'assistant'] } },
        { path: 'assignment-generate', name: 'assignment-generate', component: () => import('@/views/teacher/AssignmentGenerate.vue'), meta: { roles: ['teacher'] } },
        { path: 'cheating', name: 'cheating', component: () => import('@/views/CheatingReport.vue'), meta: { roles: ['teacher'] } },
        { path: 'gradebook', name: 'gradebook', component: () => import('@/views/Gradebook.vue'), meta: { roles: ['teacher'] } },
        { path: 'assignment-detail', name: 'assignment-detail', component: () => import('@/views/teacher/AssignmentDetail.vue'), meta: { roles: ['teacher'] } },
        { path: 'code-review', name: 'code-review', component: () => import('@/views/teacher/CodeReview.vue'), meta: { roles: ['teacher'] } },
        { path: 'student-report', name: 'student-report', component: () => import('@/views/teacher/StudentReport.vue'), meta: { roles: ['teacher'] } },
        // 管理员/教师
        { path: 'admin', name: 'admin', component: () => import('@/views/admin/Courses.vue'), meta: { roles: ['teacher', 'admin'] } },
      ]
    }
  ]
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.name === 'login') return
  if (!token) return { name: 'login' }
  // 角色权限校验
  const allowedRoles = to.meta?.roles as string[] | undefined
  if (allowedRoles && allowedRoles.length > 0) {
    const auth = useAuthStore()
    if (!allowedRoles.includes(auth.role)) {
      return { name: 'dashboard' }
    }
  }
})

export default router
