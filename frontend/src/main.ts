import { createApp } from 'vue';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import * as ElementPlusIconsVue from '@element-plus/icons-vue';
import zhCn from 'element-plus/es/locale/lang/zh-cn';

import App from './App.vue';
import router from './router';

import './assets/main.css';

// 创建Vue应用实例
const app = createApp(App);

// 注册所有的 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

// 使用Pinia状态管理
app.use(createPinia());

// 使用Vue Router
app.use(router);

// 使用Element Plus UI库
app.use(ElementPlus, {
  locale: zhCn
});

// 挂载应用
app.mount('#app'); 