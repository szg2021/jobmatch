import { createRouter, createWebHistory } from 'vue-router'
// ... existing imports ...
import RecommendationConfig from '@/views/admin/RecommendationConfig.vue'
import RecommendationResults from '@/views/recommendation/RecommendationResults.vue'
import Dashboard from '@/views/Dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  
  // Recommendation routes
  {
    path: '/recommendations',
    name: 'RecommendationResults',
    component: RecommendationResults,
    meta: { requiresAuth: true }
  },
  
  // Admin routes
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: AdminDashboard
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: AdminUsers
      },
      {
        path: 'jobs',
        name: 'AdminJobs',
        component: AdminJobs
      },
      {
        path: 'recommendation-config',
        name: 'RecommendationConfig',
        component: RecommendationConfig
      },
      // ... other admin routes ...
    ]
  },
  
  // ... other routes ...
]

// ... remaining code ... 