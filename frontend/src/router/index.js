import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('../components/AppLayout.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/DashboardView.vue') },
      { path: 'calendar', name: 'Calendar', component: () => import('../views/CalendarView.vue') },
      { path: 'schedules/new', name: 'ScheduleNew', component: () => import('../views/ScheduleFormView.vue') },
      { path: 'schedules/:id', name: 'ScheduleDetail', component: () => import('../views/ScheduleDetailView.vue') },
      { path: 'schedules/:id/edit', name: 'ScheduleEdit', component: () => import('../views/ScheduleFormView.vue') },
      { path: 'categories', name: 'Categories', component: () => import('../views/CategoriesView.vue') },
      { path: 'statistics', name: 'Statistics', component: () => import('../views/StatisticsView.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (!token && !to.meta.guest) {
    next('/login')
  } else if (token && to.meta.guest) {
    next('/')
  } else {
    next()
  }
})

export default router
