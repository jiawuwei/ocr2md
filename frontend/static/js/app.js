const { createApp } = Vue

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
            abortController: null
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
                this.abortController = new AbortController()

                const formData = new FormData()
                formData.append('file', this.selectedFile)
                console.log('Selected model before conversion:', this.selectedModel)
                formData.append('model_id', this.selectedModel)
                if (this.pages) {
                    formData.append('pages', this.pages)
                }
                
                // 打印整个 FormData 内容
                console.log('FormData contents:')
                for (let pair of formData.entries()) {
                    console.log(pair[0] + ': ' + pair[1])
                }

                const response = await fetch('/api/convert', {
                    method: 'POST',
                    body: formData,
                    signal: this.abortController.signal
                })

                console.log('Response status:', response.status)
                if (!response.ok) {
                    const error = await response.json()
                    console.error('Error response:', error)
                    throw new Error(error.detail || 'Conversion failed')
                }

                const blob = await response.blob()
                if (blob.size === 0) {
                    throw new Error('Conversion failed: empty result')
                }

                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `${this.selectedFile.name.split('.')[0]}_converted.md`
                document.body.appendChild(a)
                a.click()
                window.URL.revokeObjectURL(url)
                document.body.removeChild(a)
                
                this.convertSuccess = true
                this.showValidation = false
                // Clear success message after 5 seconds
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
    }
}).mount('#app') 