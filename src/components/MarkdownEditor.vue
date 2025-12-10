<template>
  <div class="markdown-editor">
    <div v-if="showToolbar && editorCreated" class="toolbar-container mb-2">
      <Toolbar
        :editor="editorRef"
        :mode="editorConfig.mode"
        ref="toolbarRef"
      />
    </div>
    <div class="editor-container" :style="{ height: height }" :class="{ 'border border-gray-200 rounded': bordered }">
      <Editor
        v-model="localContent"
        :defaultConfig="editorConfig"
        :mode="editorConfig.mode"
        @onCreated="handleEditorCreated"
        @onDestroyed="handleEditorDestroyed"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'

// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  height: {
    type: String,
    default: '400px'
  },
  bordered: {
    type: Boolean,
    default: true
  },
  showToolbar: {
    type: Boolean,
    default: true
  },
  placeholder: {
    type: String,
    default: '记录内容（支持Markdown语法）'
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'onCreated', 'onDestroyed'])

// 本地状态
const localContent = ref(props.modelValue)
const editorRef = ref(null)
const toolbarRef = ref(null)
const editorCreated = ref(false)

// 编辑器配置
const editorConfig = ref({
  placeholder: props.placeholder,
  autoFocus: false,
  mode: 'markdown',
  MENU_CONF: {
    uploadImage: {
      server: 'http://localhost:8000/api/notes/upload/image',
      allowPasteImage: true,
      allowDropImage: true,
      maxFileSize: 10 * 1024 * 1024, // 10MB
      accept: ['image/jpg', 'image/jpeg', 'image/png', 'image/gif', 'image/webp'],
      showLinkImage: false,
      onBeforeUpload: function(file) {
        console.log('onBeforeUpload被调用', file.name)
        return true
      },
      customUpload: async function(file, insertFn) {
        try {
          const formData = new FormData()
          formData.append('file', file)
          
          const response = await fetch('http://localhost:8000/api/notes/upload/image', {
            method: 'POST',
            body: formData
          })
          
          if (!response.ok) {
            throw new Error('上传失败')
          }
          
          const data = await response.json()
          // 后端返回格式为 {url, filename}，直接使用
          insertFn(data.url, file.name, data.url)
        } catch (error) {
          console.error('图片上传失败:', error)
          // 创建临时URL以便在编辑器中显示
          const tempUrl = URL.createObjectURL(file)
          insertFn(tempUrl, file.name, tempUrl)
        }
      }
    }
  }
})

// 监听props变化
watch(() => props.modelValue, (newVal) => {
  if (newVal !== localContent.value) {
    localContent.value = newVal
  }
}, { immediate: true })

// 监听本地内容变化
watch(() => localContent.value, (newVal) => {
  emit('update:modelValue', newVal)
})

// 编辑器创建完成
const handleEditorCreated = (editor) => {
  editorRef.value = editor
  editorCreated.value = true
  emit('onCreated', editor)
}

// 编辑器销毁
const handleEditorDestroyed = () => {
  editorRef.value = null
  editorCreated.value = false
  emit('onDestroyed')
}

// 点击空白处关闭下拉框 - 最终优化版
const handleClickOutside = (event) => {
  // 只在编辑器已创建时处理
  if (!editorRef.value) return
  
  // 检查点击目标是否在编辑器内部
  const editorElement = document.querySelector('.markdown-editor')
  if (editorElement && editorElement.contains(event.target)) {
    return // 点击在编辑器内部，不处理
  }
  
  // 查找所有打开的面板
  const allPanels = document.querySelectorAll('.w-e-panel-container')
  const visiblePanels = Array.from(allPanels).filter(panel => 
    panel.offsetParent !== null // 检查元素是否可见
  )
  
  // 如果有可见面板，关闭它们
  visiblePanels.forEach(panel => {
    // 使用CSS类控制显示/隐藏，而不是直接操作style
    panel.style.display = 'none'
  })
  
  // 移除所有激活的工具栏按钮
  const activeButtons = document.querySelectorAll('.w-e-active')
  activeButtons.forEach(button => {
    button.classList.remove('w-e-active')
  })
}

// 组件挂载时添加点击事件监听
onMounted(() => {
  // 使用冒泡阶段监听，避免影响其他事件
  document.addEventListener('click', handleClickOutside)
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  if (editorRef.value) {
    editorRef.value.destroy()
  }
})

// 设置内容
const setContent = (content) => {
  if (editorRef.value) {
    editorRef.value.setMarkdown(content)
    localContent.value = content
  }
}

// 获取内容
const getContent = () => {
  return editorRef.value ? editorRef.value.getMarkdown() : localContent.value
}

// 暴露方法
defineExpose({
  editorRef,
  setContent,
  getContent
})

// 组件卸载时销毁编辑器已合并到上面的onUnmounted钩子中
</script>

<style scoped>
.markdown-editor {
  width: 100%;
}

.toolbar-container {
  border: 1px solid #e8e8e8;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
}

.editor-container {
  overflow: auto;
}
</style>