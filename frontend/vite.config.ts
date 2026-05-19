import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],

    resolve: {
        alias: {
            // 设置 @ 符号指向 src 目录
            // 这样你写代码时可以用 import ... from '@/components/Manhattan.vue'
            '@': path.resolve(__dirname, './src'),
        },
    },

    server: {
        port: 3000,
        open: true, // 启动后自动打开浏览器
        proxy: {
            // 跨域代理配置
            // 当请求以 /api 开头时，转发到后端的 8000 端口
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
        },
    },

    build: {
        // 针对 GWAS 数据分析平台的优化
        outDir: 'dist',
        assetsDir: 'static',
        sourcemap: false, // 生产环境关闭 sourcemap 以减小体积
        chunkSizeWarningLimit: 2000, // ECharts 库较大，调高警告阈值
        rollupOptions: {
            output: {
                // 静态资源分包策略：将大型第三方库单独打包，提高加载速度
                manualChunks: {
                    'vue-vendor': ['vue', 'vue-router', 'pinia'],
                    'echarts-vendor': ['echarts'],
                    'lucide-vendor': ['lucide-vue-next'],
                },
            },
        },
    },
})