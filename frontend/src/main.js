import { createApp }        from 'vue'
import { createPinia }      from 'pinia'
import App                  from './App.vue'
import router               from './router'
import { iniciarKeepAlive } from './api/keepAlive.js'


const app   = createApp(App)
const pinia = createPinia()

app.use(pinia)   // ← Pinia primero
app.use(router)  // ← Router después
app.mount('#app')

iniciarKeepAlive()