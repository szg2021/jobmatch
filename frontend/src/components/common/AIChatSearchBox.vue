<template>
  <div class="ai-chat-search-box">
    <div class="search-header">
      <div class="search-title">
        <el-icon><ChatDotRound /></el-icon>
        <span>AI智能搜索</span>
      </div>
      <el-tooltip content="使用自然语言描述您的需求，AI将理解您的意图并提供智能匹配">
        <el-icon class="help-icon"><QuestionFilled /></el-icon>
      </el-tooltip>
    </div>
    
    <!-- 聊天历史区域 -->
    <div v-if="chatHistory.length > 0" class="chat-history" ref="chatHistoryRef">
      <div v-for="(message, index) in chatHistory" :key="index" 
           :class="['chat-message', message.role === 'user' ? 'user-message' : 'ai-message']">
        <div class="message-avatar">
          <el-avatar :icon="message.role === 'user' ? User : Service" :size="28" />
        </div>
        <div class="message-content">
          <div class="message-text">{{ message.content }}</div>
          <div v-if="message.role === 'assistant' && message.suggestions?.length" class="message-suggestions">
            <el-button 
              v-for="(suggestion, idx) in message.suggestions" 
              :key="idx"
              type="info"
              size="small"
              plain
              @click="applySuggestion(suggestion)"
            >
              {{ suggestion }}
            </el-button>
          </div>
        </div>
      </div>
      
      <div v-if="isThinking" class="thinking-indicator">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="search-input-area">
      <el-input
        v-model="searchQuery"
        :placeholder="placeholder"
        :disabled="isThinking"
        type="textarea"
        :rows="Math.min(3, searchQuery.split('\n').length)"
        resize="none"
        @keydown.enter.prevent="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button 
            :icon="isThinking ? Loading : Position" 
            :disabled="isThinking || !searchQuery.trim()" 
            @click="handleSearch">
            {{ buttonText }}
          </el-button>
        </template>
      </el-input>
      
      <div class="search-examples" v-if="showExamples && !chatHistory.length">
        <div class="examples-title">示例：</div>
        <div class="example-chips">
          <el-button 
            v-for="(example, index) in searchExamples" 
            :key="index"
            type="info"
            size="small"
            plain
            @click="applyExample(example)"
          >
            {{ example }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue';
import { 
  Search, 
  ChatDotRound, 
  QuestionFilled, 
  User, 
  Service, 
  Position,
  Loading
} from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { logger } from '@/utils/logger';
import loadingState from '@/utils/loadingState';

// 消息类型定义
interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  suggestions?: string[];
  timestamp?: number;
}

// 组件属性
interface Props {
  placeholder?: string;
  buttonText?: string;
  showExamples?: boolean;
  searchExamples?: string[];
  context?: string;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请用自然语言描述您需要什么样的职位或人才...',
  buttonText: '搜索',
  showExamples: true,
  searchExamples: () => [
    '我需要一名有5年经验的前端开发工程师',
    '查找熟悉React和TypeScript的全栈开发者',
    '帮我找精通数据分析和Python的人才',
    '有哪些远程工作机会？'
  ],
  context: ''
});

const emit = defineEmits<{
  (e: 'search', query: string, parsedCriteria: any): void;
  (e: 'chat-update', history: ChatMessage[]): void;
}>();

// 状态管理
const searchQuery = ref('');
const chatHistory = ref<ChatMessage[]>([]);
const isThinking = ref(false);
const chatHistoryRef = ref<HTMLElement | null>(null);

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight;
    }
  });
};

// AI处理搜索查询
const processWithAI = async (query: string): Promise<{ response: string; criteria: any; suggestions: string[] }> => {
  // 这里是模拟的AI处理，实际项目中应该调用后端API
  logger.info('AI处理搜索查询', query);
  
  // 模拟处理延迟
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // 简单的意图识别模拟
  let response = '';
  let criteria: any = {};
  let suggestions: string[] = [];
  
  if (query.includes('前端') || query.includes('frontend') || query.includes('web')) {
    response = '我找到了一些前端开发相关的职位，您对React还是Vue更感兴趣？';
    criteria = { 
      jobType: '技术',
      skills: ['JavaScript', 'HTML', 'CSS'] 
    };
    suggestions = ['我更熟悉React', '我偏好Vue', '两者都可以'];
  } else if (query.includes('后端') || query.includes('backend') || query.includes('服务端')) {
    response = '后端开发职位有多种语言方向，您更倾向于哪种技术栈？';
    criteria = { 
      jobType: '技术',
      skills: ['后端开发'] 
    };
    suggestions = ['Java开发', 'Python开发', 'Node.js开发'];
  } else if (query.includes('产品经理') || query.includes('product manager')) {
    response = '我找到了一些产品经理职位，您更喜欢哪个行业？';
    criteria = { 
      jobTitle: '产品经理'
    };
    suggestions = ['互联网', '金融科技', '电商行业'];
  } else if (query.includes('远程') || query.includes('remote')) {
    response = '我找到了一些远程工作机会，您想看哪个领域的？';
    criteria = { 
      workMode: '远程'
    };
    suggestions = ['开发类', '设计类', '市场营销类', '全部'];
  } else {
    response = `我会根据"${query}"为您匹配最适合的职位。您有什么特定的技能或要求吗？`;
    criteria = { 
      keywords: query
    };
    suggestions = ['添加薪资要求', '指定工作城市', '查看全部匹配结果'];
  }
  
  return { response, criteria, suggestions };
};

// 处理搜索
const handleSearch = async () => {
  const query = searchQuery.value.trim();
  if (!query || isThinking.value) return;

  // 记录用户输入
  chatHistory.value.push({
    role: 'user',
    content: query,
    timestamp: Date.now()
  });
  
  // 清空输入框
  searchQuery.value = '';
  
  // 滚动到底部
  scrollToBottom();
  
  // 设置思考状态
  isThinking.value = true;
  
  try {
    // 使用AI处理查询
    const { response, criteria, suggestions } = await loadingState.withLoadingSafe(
      'aiSearch',
      () => processWithAI(query),
      { response: '抱歉，我暂时无法处理您的请求，请稍后再试。', criteria: {}, suggestions: [] },
      { enabled: true, duration: 5000 }
    );
    
    // 添加AI回复
    chatHistory.value.push({
      role: 'assistant',
      content: response,
      suggestions,
      timestamp: Date.now()
    });
    
    // 发出搜索事件
    emit('search', query, criteria);
    emit('chat-update', chatHistory.value);
    
  } catch (error) {
    logger.error('AI搜索处理出错', error);
    ElMessage.error('搜索处理失败，请重试');
    
    // 添加错误回复
    chatHistory.value.push({
      role: 'assistant',
      content: '抱歉，处理您的请求时出现了问题，请重试。',
      timestamp: Date.now()
    });
  } finally {
    isThinking.value = false;
    scrollToBottom();
  }
};

// 应用搜索示例
const applyExample = (example: string) => {
  searchQuery.value = example;
};

// 应用AI建议
const applySuggestion = (suggestion: string) => {
  // 记录用户选择
  chatHistory.value.push({
    role: 'user',
    content: suggestion,
    timestamp: Date.now()
  });
  
  // 滚动到底部
  scrollToBottom();
  
  // 设置思考状态
  isThinking.value = true;
  
  // 模拟AI处理延迟
  setTimeout(() => {
    let response = '';
    let criteria: any = {};
    
    // 根据选择生成不同的回复和条件
    if (suggestion.includes('React')) {
      response = '好的，我将为您筛选擅长React的前端开发者职位';
      criteria = { skills: ['React', 'JavaScript'] };
    } else if (suggestion.includes('Vue')) {
      response = '了解，正在查找Vue相关的职位';
      criteria = { skills: ['Vue.js', 'JavaScript'] };
    } else if (suggestion.includes('Java')) {
      response = '正在筛选Java后端开发职位';
      criteria = { skills: ['Java', 'Spring Boot'] };
    } else if (suggestion.includes('Python')) {
      response = '好的，这里是Python开发相关的职位';
      criteria = { skills: ['Python', 'Django'] };
    } else if (suggestion.includes('互联网')) {
      response = '为您找到互联网行业的产品经理职位';
      criteria = { industry: '互联网', jobTitle: '产品经理' };
    } else if (suggestion.includes('远程')) {
      response = '以下是可远程工作的职位';
      criteria = { workMode: '远程' };
    } else {
      response = `根据您的选择"${suggestion}"，为您筛选了以下职位`;
      criteria = { keywords: suggestion };
    }
    
    // 添加AI回复
    chatHistory.value.push({
      role: 'assistant',
      content: response,
      timestamp: Date.now()
    });
    
    // 发出搜索事件
    emit('search', suggestion, criteria);
    emit('chat-update', chatHistory.value);
    
    // 关闭思考状态
    isThinking.value = false;
    
    // 滚动到底部
    scrollToBottom();
  }, 800);
};

// 设置初始系统消息
onMounted(() => {
  if (props.context) {
    chatHistory.value.push({
      role: 'system',
      content: props.context,
      timestamp: Date.now()
    });
  }
});
</script>

<style scoped>
.ai-chat-search-box {
  background-color: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  max-width: 100%;
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.search-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409EFF;
  font-weight: 600;
}

.help-icon {
  color: #909399;
  cursor: pointer;
}

.help-icon:hover {
  color: #409EFF;
}

.chat-history {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 16px;
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-message {
  display: flex;
  margin-bottom: 8px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  margin: 0 8px;
}

.message-content {
  max-width: 80%;
}

.user-message .message-content {
  background-color: #ecf5ff;
  border-radius: 12px 2px 12px 12px;
  padding: 8px 12px;
  color: #409EFF;
}

.ai-message .message-content {
  background-color: #f5f7fa;
  border-radius: 2px 12px 12px 12px;
  padding: 8px 12px;
  color: #606266;
}

.message-text {
  word-break: break-word;
  line-height: 1.5;
}

.message-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.thinking-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #c0c4cc;
  margin: 0 4px;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.search-input-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.search-examples {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.examples-title {
  font-size: 13px;
  color: #909399;
}

.example-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style> 