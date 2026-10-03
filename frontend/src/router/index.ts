import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('@/views/Login.vue') },
    {
      path: '/',
      component: () => import('@/layout/DefaultLayout.vue'),
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', name: 'dashboard', component: () => import('@/views/Dashboard.vue') },
        { path: 'assignments', name: 'assignments', component: () => import('@/views/AssignmentList.vue') },
        { path: 'my-submissions', name: 'my-submissions', component: () => import('@/views/student/MySubmissions.vue') },
        { path: 'enroll', name: 'enroll', component: () => import('@/views/student/CourseEnroll.vue') },
        { path: 'my-grades', name: 'my-grades', component: () => import('@/views/student/MyGrades.vue') },
        { path: 'submit', name: 'submit', component: () => import('@/views/student/Submit.vue') },
        { path: 'diagnose', name: 'diagnose', component: () => import('@/views/student/Diagnose.vue') },
        { path: 'variant', name: 'variant', component: () => import('@/views/student/Variant.vue') },
        { path: 'learning-report', name: 'learning-report', component: () => import('@/views/teacher/LearningDashboard.vue') },
        { path: 'assignment-generate', name: 'assignment-generate', component: () => import('@/views/teacher/AssignmentGenerate.vue') },
        { path: 'appeal', name: 'appeal', component: () => import('@/views/Appeal.vue') },
        { path: 'cheating', name: 'cheating', component: () => import('@/views/CheatingReport.vue') },
        { path: 'gradebook', name: 'gradebook', component: () => import('@/views/Gradebook.vue') },
        { path: 'assignment-detail', name: 'assignment-detail', component: () => import('@/views/teacher/AssignmentDetail.vue') },
        { path: 'code-review', name: 'code-review', component: () => import('@/views/teacher/CodeReview.vue') },
        { path: 'admin', name: 'admin', component: () => import('@/views/admin/Courses.vue') }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'login' && !token) {
    return { name: 'login' }
  }
})

export default router
