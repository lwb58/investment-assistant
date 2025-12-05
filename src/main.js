import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

// 导入Element Plus组件库和样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

// 导入Markdown编辑器
import VMdEditor from '@kangc/v-md-editor'
import '@kangc/v-md-editor/lib/style/base-editor.css'
import vuepressTheme from '@kangc/v-md-editor/lib/theme/vuepress.js'
import '@kangc/v-md-editor/lib/theme/style/vuepress.css'

// 导入代码高亮
import Prism from 'prismjs'
// 导入中文语言包
import '@kangc/v-md-editor/lib/lang/zh-CN'

// 配置Markdown编辑器
VMdEditor.use(vuepressTheme, {
  Prism
})

const app = createApp(App)

// 使用Element Plus并配置中文语言
app.use(ElementPlus, {
  locale: zhCn
})
// 使用Markdown编辑器
app.use(VMdEditor)
app.use(router)

app.mount('#app')