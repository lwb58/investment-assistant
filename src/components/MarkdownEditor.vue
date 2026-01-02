<template>
  <div class="markdown-editor">
    <div class="markdown-editor__container">
      <Toolbar
        class="markdown-editor__toolbar"
        :editor="editorRef"
        :defaultConfig="toolbarConfig"
        :mode="mode"
      />
      <!-- 标签选择区域 -->
      <div class="tags-section">
        <el-tag
          v-for="tag in defaultTags"
          :key="tag"
          :type="editorTags.includes(tag) ? 'primary' : 'info'"
          size="small"
          @click="toggleTag(tag)"
          class="tag-option"
        >
          {{ tag }}
        </el-tag>
        <el-input
          v-model="newTag"
          placeholder="添加新标签"
          size="small"
          class="new-tag-input"
          @keyup.enter="addCustomTag"
        />
        <el-button
          type="success"
          size="small"
          @click="addCustomTag"
          :disabled="!newTag"
          class="add-tag-btn"
        >
          添加
        </el-button>
      </div>
      <div class="selected-tags" v-if="editorTags">
        <el-tag
          v-for="tag in editorTags.split(',')"
          :key="tag"
          type="primary"
          closable
          size="small"
          @close="removeTag(tag)"
          class="selected-tag"
        >
          {{ tag }}
        </el-tag>
      </div>

      <Editor
        class="markdown-editor__content"
        :style="{ height: height }"
        v-model="localValue"
        :defaultConfig="editorConfig"
        :mode="mode"
        @onCreated="handleCreated"
      />
    </div>
    <!-- 可选的操作按钮区域 -->
    <div v-if="showActionButtons" class="markdown-editor__actions">
      <slot name="action-buttons">
        <button 
          v-if="showCancelButton" 
          class="markdown-editor__button markdown-editor__button--cancel"
          @click="handleCancel"
        >
          {{ cancelButtonText }}
        </button>
        <button 
          v-if="showSaveButton" 
          class="markdown-editor__button markdown-editor__button--save"
          @click="handleSave"
        >
          {{ saveButtonText }}
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, watch, onBeforeUnmount, onMounted } from 'vue'
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
  },
  // 笔记相关属性
  title: {
    type: String,
    default: ''
  },
  stockCode: {
    type: String,
    default: ''
  },
  stockName: {
    type: String,
    default: ''
  },
  noteType: {
    type: String,
    default: 'note'
  },
  source: {
    type: String,
    default: ''
  },
  // 操作按钮相关配置
  showActionButtons: {
    type: Boolean,
    default: false
  },
  showCancelButton: {
    type: Boolean,
    default: true
  },
  showSaveButton: {
    type: Boolean,
    default: true
  },
  cancelButtonText: {
    type: String,
    default: '取消'
  },
  saveButtonText: {
    type: String,
    default: '保存'
  },
  tags: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'cancel', 'save'])

// 编辑器实例，必须用 shallowRef
const editorRef = shallowRef()

// 本地内容
const localValue = ref(props.modelValue || '')
// 标签相关
const editorTags = ref(props.tags || '')
const newTag = ref('')
// 从数据库加载的标签列表
const defaultTags = ref(['估值分析']) // 确保包含估值分析标签

// 监听tags属性变化
watch(() => props.tags, (newTags) => {
  editorTags.value = newTags || ''
}, { immediate: true })



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
      customUpload: (file, insertFn) => {
        // 使用Promise链式调用确保同步执行，避免异步导致的保存冲突
        Promise.resolve()
          .then(() => uploadImageToBackend(file))
          .then(url => {
            if (url) {
              insertFn(url, file.name, url)
            } else {
              console.error('图片上传失败，未插入图片')
            }
          })
          .catch(error => {
            console.error('图片上传错误:', error)
            // 显示上传失败提示
            if (typeof window !== 'undefined' && window.alert) {
              window.alert('图片上传失败，请检查网络连接后重试')
            }
          })
      }
    },
    // 粘贴图片配置
    pasteImage: {
      // 自定义粘贴处理
      customUpload: (file, insertFn) => {
        // 使用Promise链式调用确保同步执行，避免异步导致的保存冲突
        Promise.resolve()
          .then(() => uploadImageToBackend(file))
          .then(url => {
            if (url) {
              insertFn(url, file.name, url)
            } else {
              console.error('图片粘贴失败，未插入图片')
            }
          })
          .catch(error => {
            console.error('图片粘贴上传错误:', error)
            // 显示上传失败提示
            if (typeof window !== 'undefined' && window.alert) {
              window.alert('图片粘贴失败，请检查网络连接后重试')
            }
          })
      }
    }
  }
}

// 调用后端上传图片接口（同步处理）
const uploadImageToBackend = async (file) => {
  try {
    // 使用同步方式上传，确保图片完全上传后再返回
    const data = await apiService.uploadImage(file)
    return data.url
  } catch (error) {
    console.error('图片上传失败:', error)
    // 显示上传失败提示
    if (typeof window !== 'undefined' && window.alert) {
      window.alert('图片上传失败，请检查网络连接后重试')
    }
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

// 加载标签列表
const loadTags = async () => {
  try {
    const tags = await apiService.getTags()
    if (tags && Array.isArray(tags)) {
      // 确保包含估值分析标签
      const tagNames = tags.map(tag => tag.name)
      if (!tagNames.includes('估值分析')) {
        tagNames.unshift('估值分析')
      }
      defaultTags.value = tagNames
    }
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

// 组件挂载时加载标签
onMounted(() => {
  loadTags()
})

// 组件销毁时，也及时销毁编辑器
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})

// 处理取消按钮点击
const handleCancel = () => {
  emit('cancel')
}

// 切换标签选择
const toggleTag = (tag) => {
  let tagsArray = editorTags.value ? editorTags.value.split(',') : []
  const index = tagsArray.indexOf(tag)
  
  if (index > -1) {
    tagsArray.splice(index, 1)
  } else {
    tagsArray.push(tag)
  }
  
  editorTags.value = tagsArray.join(',')
}

// 添加自定义标签
const addCustomTag = async () => {
  if (!newTag.value.trim()) return
  
  let tagsArray = editorTags.value ? editorTags.value.split(',') : []
  const tag = newTag.value.trim()
  
  if (!tagsArray.includes(tag)) {
    tagsArray.push(tag)
    editorTags.value = tagsArray.join(',')
    
    // 保存新标签到数据库
    try {
      await apiService.createTag(tag)
      // 更新标签列表
      await loadTags()
    } catch (error) {
      console.error('保存标签失败:', error)
    }
  }
  
  newTag.value = ''
}

// 移除标签
const removeTag = (tag) => {
  let tagsArray = editorTags.value ? editorTags.value.split(',') : []
  const index = tagsArray.indexOf(tag)
  
  if (index > -1) {
    tagsArray.splice(index, 1)
    editorTags.value = tagsArray.join(',')
  }
}



// 处理保存按钮点击
const handleSave = () => {
  emit('save', {
    title: props.title,
    content: localValue.value,
    stockCode: props.stockCode,
    stockName: props.stockName,
    type: props.noteType,
    source: props.source,
    tags: editorTags.value
  })
}

// 暴露方法
defineExpose({
  getEditor: () => editorRef.value,
  setContent: (content) => {
    localValue.value = content
  },
  getContent: () => {
    return localValue.value
  },
  getTags: () => {
    return editorTags.value
  },
  setTags: (tags) => {
    editorTags.value = tags
  }
})
</script>

<style scoped>
/* Markdown Editor 组件样式 */
.markdown-editor {
  width: 100%;
  margin: 0 auto;
  position: relative;
}

.markdown-editor__container {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-small);
  overflow: hidden;
  transition: var(--transition-base);
}

.markdown-editor__container:focus-within {
  border-color: var(--border-color-hover);
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

.markdown-editor__toolbar {
  border-bottom: 1px solid var(--border-color);
  background-color: var(--bg-tertiary);
}

.markdown-editor__content {
  overflow-y: hidden;
}

/* 标签样式 */
.tags-section {
  display: flex;
  align-items: center;
  margin: 10px 0;
  flex-wrap: wrap;
  gap: 10px;
  padding: 0 10px;
}

.tag-option {
  cursor: pointer;
  margin-right: 5px;
  margin-bottom: 5px;
}

.new-tag-input {
  width: 150px;
  margin-right: 10px;
}

.add-tag-btn {
  white-space: nowrap;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 0 10px 10px;
}



.selected-tag {
  margin-right: 10px;
  margin-bottom: 10px;
}

/* 操作按钮样式 */
.markdown-editor__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.markdown-editor__button {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-small);
  cursor: pointer;
  font-size: 14px;
  transition: all var(--transition-base);
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.markdown-editor__button:hover {
  border-color: var(--border-color-hover);
}

.markdown-editor__button--cancel:hover {
  background-color: var(--bg-secondary);
}

.markdown-editor__button--save {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.markdown-editor__button--save:hover {
  background-color: var(--primary-color-hover);
  border-color: var(--primary-color-hover);
}
</style>