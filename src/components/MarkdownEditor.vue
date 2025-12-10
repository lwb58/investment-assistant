<template>
  <div class="markdown-editor">
    <div style="border: 1px solid #ccc">
      <Toolbar
        style="border-bottom: 1px solid #ccc"
        :editor="editorRef"
        :defaultConfig="toolbarConfig"
        :mode="mode"
      />
      <Editor
        style="height: 300px; overflow-y: hidden;"
        v-model="localValue"
        :defaultConfig="editorConfig"
        :mode="mode"
        @onCreated="handleCreated"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, watch, onBeforeUnmount } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'
import apiService from '../api/apiService'

// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入内容...'
  },
  height: {
    type: String,
    default: '300px'
  }
})

// Emits
const emit = defineEmits(['update:modelValue'])

// 编辑器实例，必须用 shallowRef
const editorRef = shallowRef()

// 本地内容
const localValue = ref(props.modelValue || '')

// 工具栏配置
const toolbarConfig = {
  // 配置工具栏，可根据需求调整
  excludeKeys: ['fullScreen', 'codeBlock', 'splitScreen']
}

// 编辑器配置
const editorConfig = {
  placeholder: props.placeholder,
  // 允许粘贴图片
  pasteIgnoreImg: false,
  // 图片上传和粘贴配置
  MENU_CONF: {
    // 工具栏上传图片配置
    uploadImage: {
      // 自定义上传方法
      customUpload: async (file, insertFn) => {
        // 调用后端上传接口
        const url = await uploadImageToBackend(file)
        // 插入图片
        insertFn(url, file.name, url)
      }
    },
    // 粘贴图片配置
    pasteImage: {
      // 自定义粘贴处理
      customUpload: async (file, insertFn) => {
        // 调用后端上传接口
        const url = await uploadImageToBackend(file)
        // 插入图片
        insertFn(url, file.name, url)
      }
    }
  }
}

// 调用后端上传图片接口
const uploadImageToBackend = async (file) => {
  try {
    const data = await apiService.uploadImage(file)
    return data.url
  } catch (error) {
    console.error('上传图片失败:', error)
    return null
  }
}

// 编辑器模式
const mode = 'default' // 或 'simple'

// 监听props变化
watch(() => props.modelValue, (newVal) => {
  if (newVal !== localValue.value) {
    localValue.value = newVal
  }
}, { immediate: true })

// 监听本地内容变化
watch(() => localValue.value, (newVal) => {
  emit('update:modelValue', newVal)
})

// 编辑器创建完成
const handleCreated = (editor) => {
  editorRef.value = editor // 记录 editor 实例，重要！
}

// 组件销毁时，也及时销毁编辑器
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})

// 暴露方法
defineExpose({
  getEditor: () => editorRef.value,
  setContent: (content) => {
    localValue.value = content
  },
  getContent: () => {
    return localValue.value
  }
})
</script>

<style scoped>
.markdown-editor {
  width: 100%;
  margin: 0 auto;
}
</style>