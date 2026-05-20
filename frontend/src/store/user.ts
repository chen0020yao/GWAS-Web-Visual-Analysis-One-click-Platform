import { defineStore } from 'pinia'
import { loginAPI } from '@/api/user'
import router from '@/router'

export const useUserStore = defineStore('user', {
    state: () => ({
        token: localStorage.getItem('token') || '',
        userInfo: null as any
    }),

    getters: {
        isLoggedIn: (state) => !!state.token,
        nickname: (state) => state.userInfo?.nickname || '科研用户',
        initials: (state) => (state.userInfo?.nickname || '研')[0]
    },

    actions: {
        async login(loginForm: any) {
            try {
                const res: any = await loginAPI(loginForm)

                // 打印出来看看，如果你在控制台看到 {access_token: "..."}，就稳了
                console.log('登录接口原始返回:', res)

                // 适配 FastAPI 返回的字段名
                const token = res.access_token
                const nickname = res.nickname

                if (token) {
                    this.token = token
                    localStorage.setItem('token', token)

                    this.userInfo = {
                        nickname: nickname || '科研用户',
                        username: loginForm.username
                    }

                    // 核心动作：跳转
                    console.log('Token 获取成功，准备跳转 Dashboard...')
                    await router.push('/dashboard')
                    return true
                } else {
                    throw new Error('未识别到有效的 Token 字段')
                }
            } catch (error: any) {
                // 如果还弹出“未知系统错误”，说明还是拦截器没改对
                alert('登录遇到障碍: ' + (error.message || '未知错误'))
                throw error
            }
        },

        async fetchUserInfo() {
            if (!this.token) return
            try {
                const { getUserInfoAPI } = await import('@/api/user')
                const info: any = await getUserInfoAPI()
                this.userInfo = {
                    nickname: info.nickname,
                    email: info.email,
                    avatar: info.avatar,
                    id: info.id,
                }
            } catch (_) {
                // token 过期或用户不存在，清除登录态
                this.token = ''
                this.userInfo = null
                localStorage.removeItem('token')
            }
        },

        logout() {
            this.token = ''
            this.userInfo = null
            localStorage.removeItem('token')
            router.push('/login')
        }
    }
})