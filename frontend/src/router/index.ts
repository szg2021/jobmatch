import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store/user';
import { ElMessage } from 'element-plus';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/Login.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/Register.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/dashboard/Layout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'profile',
          name: 'profile',
          component: () => import('../views/dashboard/Profile.vue')
        },
        {
          path: 'jobs',
          name: 'jobs',
          component: () => import('../views/dashboard/Jobs.vue')
        },
        {
          path: 'jobs-market',
          name: 'jobs-market',
          component: () => import('../views/dashboard/JobsMarket.vue')
        },
        {
          path: 'talents-market',
          name: 'talents-market',
          component: () => import('../views/dashboard/TalentsMarket.vue')
        },
        {
          path: 'digital-employees',
          name: 'digital-employees',
          component: () => import('../views/dashboard/DigitalEmployees.vue')
        },
        {
          path: 'resume',
          name: 'resume',
          component: () => import('../views/dashboard/Resume.vue')
        },
        {
          path: 'job-recommendations',
          name: 'job-recommendations',
          component: () => import('../views/dashboard/JobRecommendations.vue')
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFound.vue')
    }
  ]
});

// 全局前置守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  const isLoggedIn = userStore.isLoggedIn;
  
  // 特定页面允许游客访问
  const publicDashboardPages = ['jobs-market', 'digital-employees'];
  const isPublicDashboardPage = publicDashboardPages.includes(to.name as string);
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    // 如果是公开的仪表盘页面，允许访问
    if (isPublicDashboardPage) {
      next();
    } else {
      ElMessage.warning('请先登录');
      next({ name: 'login', query: { redirect: to.fullPath } });
    }
  } else if (to.meta.requiresGuest && isLoggedIn) {
    next({ name: 'home' });
  } else {
    next();
  }
});

export default router; 