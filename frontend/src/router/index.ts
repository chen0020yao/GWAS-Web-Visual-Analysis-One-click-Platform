import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layout/MainLayout.vue'
import { useUserStore } from '@/store/user'
import { useProjectStore } from '@/store/project'
import LoginView from '@/views/login/index.vue'
import RegisterView from '@/views/register/index.vue'

const routes: RouteRecordRaw[] = [
    {
        path: '/login',
        name: 'Login',
        component: LoginView, // 改为直接引用
        meta: { title: '登录 - GWAS Platform' }
    },
    {
        path: '/register',
        name: 'Register',
        component: RegisterView, // 改为直接引用
        meta: { title: '申请开通 - GWAS Platform' }
    },
    {
        path: '/',
        component: MainLayout,
        redirect: '/dashboard',
        children: [
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('@/views/dashboard/index.vue'),
                meta: { title: '仪表盘', icon: '🏠' }
            },
            // --- Project 核心流转路径 ---
            {
                path: 'project/upload',
                name: 'Upload',
                component: () => import('@/views/project/upload.vue'),
                meta: { title: '数据上传', step: 'IDLE' }
            },
            {
                path: 'project/clean',
                name: 'Clean',
                component: () => import('@/views/project/clean.vue'),
                meta: { title: '数据清洗', requiresStep: 'UPLOADED' }
            },
            {
                path: 'project/pca',
                name: 'PCA',
                component: () => import('@/views/project/pca.vue'),
                meta: { title: '群体结构分析', requiresStep: 'QC_DONE' }
            },
            {
                path: 'project/gwas',
                name: 'GWAS',
                component: () => import('@/views/project/gwas.vue'),
                meta: { title: '关联分析', requiresStep: 'QC_DONE' }
            },
            {
                path: 'project/visualize',
                name: 'Visualize',
                component: () => import('@/views/project/visualize.vue'),
                meta: { title: '结果可视化', requiresStep: 'ANALYSIS_DONE' }
            },
            // --- Analysis 后续深度分析 ---
            {
                path: 'analysis/snp',
                name: 'SNPDetail',
                component: () => import('@/views/analysis/snp.vue'),
                meta: { title: 'SNP 注释详情', requiresStep: 'ANALYSIS_DONE' }
            },
            {
                path: 'analysis/enrichment',
                name: 'Enrichment',
                component: () => import('@/views/analysis/enrichment.vue'),
                meta: { title: '通路富集分析', requiresStep: 'ANALYSIS_DONE' }
            },
            // --- 用户与历史 ---
            {
                path: 'history',
                name: 'History',
                component: () => import('@/views/history/index.vue'),
                meta: { title: '历史记录', requiresAuth: true }
            },
            {
                path: 'profile',
                name: 'Profile',
                component: () => import('@/views/profile/index.vue'),
                meta: { title: '个人中心', requiresAuth: true }
            }
        ]
    },
    // 404 页面处理
    {
        path: '/:pathMatch(.*)*',
        redirect: '/dashboard'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior() {
        return { top: 0 }
    }
})

/**
 * 全局路由守卫
 */
router.beforeEach((to, from, next) => {
    const userStore = useUserStore()
    const projectStore = useProjectStore()

    // 设置页面标题
    document.title = (to.meta.title as string) || 'GWAS Platform'

    // 白名单页面直接放行
    const whiteList = ['/login', '/register']
    if (whiteList.includes(to.path)) {
        return next()
    }

    // ⭐【关键修复位置】⭐
    // 检查是否有 Token：不仅查 Pinia 状态，还要查本地存储
    const hasToken = userStore.token || localStorage.getItem('token')

    if (!hasToken) {
        // 如果完全没 Token，才去登录页
        return next({
            path: '/login',
            query: { redirect: to.fullPath }
        })
    }

    // 3. 项目进度逻辑锁 (只有登录后的页面才走这里)
    if (to.meta.requiresStep) {
        const required = to.meta.requiresStep as string
        const current = projectStore.step || 'IDLE' // 确保有默认值
        const stepWeight: Record<string, number> = {
            'IDLE': 0, 'UPLOADED': 1, 'QC_DONE': 2, 'ANALYSIS_DONE': 3
        }

        if (stepWeight[current] < stepWeight[required]) {
            return next({ name: 'Upload' })
        }
    }

    next()
})
export default router