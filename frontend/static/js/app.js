const { createApp } = Vue

// 配置 marked
marked.setOptions({
    gfm: true, // GitHub 风格的 Markdown
    breaks: true, // 允许回车换行
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-'
})

createApp({
    data() {
        return {
            selectedFile: null,
            selectedModel: '',
            pages: '',
            models: [],
            error: null,
            isConverting: false,
            isDragging: false,
            convertSuccess: false,
            maxFileSize: 50 * 1024 * 1024, // 50MB
            validationErrors: {
                file: null,
                model: null,
                pages: null
            },
            showValidation: false,
            abortController: null,
            markdownContent: '',  // 添加 markdown 内容
            showExportMenu: false,
            copySuccess: false
        }
    },
    computed: {
        canConvert() {
            return this.selectedFile && 
                   this.selectedModel && 
                   !this.isConverting && 
                   this.selectedFile.size <= this.maxFileSize &&
                   !this.hasValidationErrors
        },
        hasValidationErrors() {
            return Object.values(this.validationErrors).some(error => error !== null)
        },
        fileError() {
            if (!this.showValidation) return null
            if (!this.selectedFile) return 'Please select a file'
            if (this.selectedFile.size > this.maxFileSize) {
                return 'File size exceeds 50MB limit'
            }
            return null
        },
        modelError() {
            if (!this.showValidation) return null
            if (!this.selectedModel) return 'Please select an AI model'
            return null
        },
        pageError() {
            if (!this.showValidation) return null
            if (!this.pages) return null
            // Validate page format
            if (this.pages.includes('-')) {
                const [start, end] = this.pages.split('-').map(Number)
                if (isNaN(start) || isNaN(end) || start < 1 || end < start) {
                    return 'Invalid page range format (e.g., use 1-5)'
                }
            } else {
                const pageList = this.pages.split(',').map(p => parseInt(p.trim()))
                if (pageList.some(isNaN) || pageList.some(p => p < 1)) {
                    return 'Invalid page format (e.g., use 1,2,3)'
                }
            }
            return null
        },
        markdownHtml() {
            if (!this.markdownContent) return ''
            try {
                return marked.parse(this.markdownContent)
            } catch (e) {
                console.error('Markdown parsing error:', e)
                return '<div class="text-red-500">Error parsing markdown content</div>'
            }
        }
    },
    methods: {
        async loadModels() {
            try {
                const response = await fetch('/api/models')
                if (!response.ok) {
                    const error = await response.json()
                    throw new Error(error.detail || 'Failed to load models')
                }
                const data = await response.json()
                if (!data || !data.vendors) {
                    throw new Error('Invalid model data format')
                }
                this.models = data.vendors
                if (this.models.length === 0) {
                    throw new Error('No AI models available')
                }
            } catch (error) {
                this.error = error.message
            }
        },
        handleFileSelect(event) {
            const file = event.target.files[0]
            if (file) {
                this.selectedFile = file
                this.convertSuccess = false
                if (this.showValidation) {
                    this.updateValidationErrors()
                }
            }
        },
        handleFileDrop(event) {
            this.isDragging = false
            const file = event.dataTransfer.files[0]
            if (file) {
                this.selectedFile = file
                this.convertSuccess = false
                if (this.showValidation) {
                    this.updateValidationErrors()
                }
            }
        },
        updateValidationErrors() {
            this.validationErrors = {
                file: this.fileError,
                model: this.modelError,
                pages: this.pageError
            }
            // 只显示第一个错误
            const firstError = Object.values(this.validationErrors).find(error => error !== null)
            this.error = firstError || null
        },
        validateBeforeConvert() {
            this.showValidation = true
            this.updateValidationErrors()
            if (this.hasValidationErrors) {
                throw new Error(this.error)
            }
        },
        async convertFile() {
            this.validateBeforeConvert()
            if (!this.canConvert) return

            try {
                this.isConverting = true
                this.error = null
                this.convertSuccess = false
                this.markdownContent = ''  // 清空之前的内容
                this.abortController = new AbortController()

                const formData = new FormData()
                formData.append('file', this.selectedFile)
                formData.append('model_id', this.selectedModel)
                if (this.pages) {
                    formData.append('pages', this.pages)
                }

                const response = await fetch('/api/convert', {
                    method: 'POST',
                    body: formData,
                    signal: this.abortController.signal
                })

                if (!response.ok) {
                    const error = await response.json()
                    throw new Error(error.detail || 'Conversion failed')
                }

                const blob = await response.blob()
                if (blob.size === 0) {
                    throw new Error('Conversion failed: empty result')
                }

                // 保存文件
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `${this.selectedFile.name.split('.')[0]}_converted.md`
                document.body.appendChild(a)
                a.click()
                window.URL.revokeObjectURL(url)
                document.body.removeChild(a)

                // 显示预览
                this.markdownContent = await blob.text()
                
                this.convertSuccess = true
                this.showValidation = false
                setTimeout(() => {
                    this.convertSuccess = false
                }, 5000)
            } catch (error) {
                if (error.name === 'AbortError') {
                    this.error = '转换已停止'
                } else {
                    this.error = error.message
                }
            } finally {
                this.isConverting = false
                this.abortController = null
            }
        },
        handleModelSelect(model) {
            this.selectedModel = model.model_id
            if (this.showValidation) {
                this.updateValidationErrors()
            }
        },
        stopConversion() {
            if (this.abortController) {
                this.abortController.abort()
            }
        },
        toggleExportMenu() {
            this.showExportMenu = !this.showExportMenu
            // 点击外部关闭菜单
            if (this.showExportMenu) {
                setTimeout(() => {
                    const closeMenu = (e) => {
                        if (!e.target.closest('.dropdown')) {
                            this.showExportMenu = false
                            document.removeEventListener('click', closeMenu)
                        }
                    }
                    document.addEventListener('click', closeMenu)
                }, 0)
            }
        },
        async copyMarkdown() {
            try {
                await navigator.clipboard.writeText(this.markdownContent)
                this.showExportMenu = false
                this.copySuccess = true
                this.error = null
                // 显示临时成功消息
                this.convertSuccess = true
                setTimeout(() => {
                    this.convertSuccess = false
                }, 2000)
            } catch (err) {
                this.error = '复制失败，请重试'
            }
        },
        downloadMarkdown() {
            const blob = new Blob([this.markdownContent], { type: 'text/markdown' })
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `${this.selectedFile.name.split('.')[0]}_converted.md`
            document.body.appendChild(a)
            a.click()
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)
            this.showExportMenu = false
        },
        async downloadWord() {
            try {
                // 将 Markdown 转换为 HTML
                const htmlContent = marked.parse(this.markdownContent);
                
                // 创建完整的 HTML 文档
                const fullHtml = `
                    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
                    <head>
                        <meta charset="utf-8">
                        <title>Exported Document</title>
                        <style>
                            body { font-family: Arial, sans-serif; }
                            pre { background-color: #f6f8fa; padding: 16px; white-space: pre-wrap; }
                            code { background-color: #f6f8fa; padding: 2px 4px; }
                            table { border-collapse: collapse; width: 100%; }
                            th, td { border: 1px solid #ddd; padding: 8px; }
                            img { max-width: 100%; }
                            blockquote { border-left: 4px solid #ddd; margin: 0; padding-left: 16px; }
                        </style>
                    </head>
                    <body>
                        ${htmlContent}
                    </body>
                    </html>
                `;

                // 创建 Blob
                const blob = new Blob([fullHtml], {
                    type: 'application/msword;charset=utf-8'
                });

                // 下载文件
                const fileName = `${this.selectedFile.name.split('.')[0]}_converted.doc`;
                saveAs(blob, fileName);
                
                this.showExportMenu = false;
                this.convertSuccess = true;
                setTimeout(() => {
                    this.convertSuccess = false;
                }, 2000);
            } catch (err) {
                console.error('Word export error:', err);
                this.error = '导出Word失败：' + err.message;
            }
        }
    },
    watch: {
        selectedModel() {
            if (this.showValidation) {
                this.updateValidationErrors()
            }
        },
        pages() {
            if (this.showValidation) {
                this.updateValidationErrors()
            }
        },
        selectedFile() {
            if (this.showValidation) {
                this.updateValidationErrors()
            }
        }
    },
    mounted() {
        this.loadModels()
        // 点击 ESC 关闭导出菜单
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.showExportMenu) {
                this.showExportMenu = false
            }
        })
    }
}).mount('#app') 