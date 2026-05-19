import { createApp } from 'vue'
import { createPinia } from 'pinia'
// 1. 引入持久化插件
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import App from './App.vue'
import router from './router'
import './assets/styles/variables.css'

const app = createApp(App)
const pinia = createPinia()

// 2. 将插件安装到 pinia 实例中
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.mount('#app')