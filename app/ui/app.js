function app() {
    return {
        activeTab: 'inicio',
        tabs: [
            { id: 'inicio', label: 'Inicio' },
            { id: 'transcripcion', label: 'Apuntes' },
            { id: 'formato', label: 'Formato' },
            { id: 'publicar', label: 'Publicar' }
        ],
        ytUrl: '',
        localFile: null,
        loading: false,
        videoInfo: null,
        estimation: '',
        transcribing: false,
        progress: 0,
        statusText: '',
        transcriptionText: '',
        formatting: false,
        codeChanged: false,
        articlesHtml: '',
        previousArticlesHtml: '',
        showingPrevious: false,
        transcriptionHtml: '',
        previewHtml: '',
        claseNum: 1,
        courseSlug: 'IA',
        taughtBy: '',
        reviewedBy: '',
        showConfig: false,
        configTab: 'wp',
        config: {
            wp_url: '',
            wp_user: '',
            wp_app_password: '',
            default_taught_by: '',
            default_reviewed_by: '',
            default_super_label: 'CAPACITACIÓN MODELADO 3D + IA + ENTORNOS INMERSIVOS',
            model_name: 'qwen2.5:0.5b',
            show_credits: true
        },
        promptText: '',
        systemStatus: {},
        publishing: false,
        publishUrl: '',
        sessions: [],

        editors: {},

        async init() {
            await this.loadConfig();
            await this.loadPrompt();
            await this.loadSystemStatus();
            try {
                this.sessions = JSON.parse(localStorage.getItem('zorroazul_sessions') || '[]');
            } catch(e) { this.sessions = []; }
            this.$watch('configTab', () => this.initEditors());
            this.$watch('activeTab', (val) => { if (val === 'formato') this.initEditors(); });
            this.$watch('showConfig', (val) => { if (val) this.initEditors(); });
        },

        async loadConfig() {
            try {
                const resp = await fetch('/api/config');
                const data = await resp.json();
                this.config = { ...this.config, ...data };
                this.taughtBy = this.config.default_taught_by;
                this.reviewedBy = this.config.default_reviewed_by;
            } catch (e) {}
        },

        async loadSystemStatus() {
            try {
                const resp = await fetch('/api/system-check');
                this.systemStatus = await resp.json();
            } catch (e) {}
        },

        async loadPrompt() {
            try {
                const resp = await fetch('/api/prompt');
                const data = await resp.json();
                this.promptText = data.prompt;
            } catch (e) {}
        },

        async saveConfig() {
            try {
                await fetch('/api/config', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.config)
                });
                await fetch('/api/prompt', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: this.promptText })
                });
                alert("Configuración guardada correctamente");
                this.showConfig = false;
            } catch (e) {
                alert("Error al guardar configuración");
            }
        },

        async savePrompt() {
            try {
                await fetch('/api/prompt', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: this.promptText })
                });
            } catch (e) {}
        },

        async analyzeVideo() {
            if (!this.ytUrl) {
                if (this.localFile) {
                    alert("Cargaste un video local, pero necesitás pegar el link de YouTube de referencia para generar los botones de tiempo [▶ Ir al video].");
                }
                return;
            }
            this.loading = true;
            try {
                const resp = await fetch('/api/youtube-info', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: this.ytUrl })
                });
                if (!resp.ok) {
                    const err = await resp.json();
                    throw new Error(err.detail || "Video no encontrado");
                }
                this.videoInfo = await resp.json();

                const estResp = await fetch('/api/estimate-time', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ duration: this.videoInfo.duration })
                });
                const estData = await estResp.json();
                const minutes = Math.ceil(estData.estimated_seconds / 60);
                this.estimation = `~${minutes} minutos`;
            } catch (e) {
                alert(e.message);
            } finally {
                this.loading = false;
            }
        },

        async startTranscription() {
            if (!this.videoInfo) return;
            this.activeTab = 'transcripcion';
            this.transcribing = true;
            this.progress = 0;
            this.statusText = 'Iniciando...';
            this.transcriptionText = '';

            let localFileName = null;
            if (this.localFile) {
                this.statusText = 'Subiendo video local...';
                const formData = new FormData();
                formData.append('file', this.localFile);
                const uploadResp = await fetch('/api/upload-video', {
                    method: 'POST',
                    body: formData
                });
                const uploadData = await uploadResp.json();
                localFileName = uploadData.filename;
            }

            const response = await fetch('/api/transcribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    video_id: this.videoInfo.video_id,
                    local_file: localFileName
                })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            if (data.status) this.statusText = data.status.toUpperCase();
                            if (data.progress !== undefined) this.progress = data.progress;
                            if (data.transcription) {
                                this.transcriptionText = data.transcription;
                                this.transcribing = false;
                            }
                            if (data.status === 'error') {
                                alert(data.detail);
                                this.transcribing = false;
                            }
                        } catch (e) {}
                    }
                }
            }
        },

        estimateFormatTime() {
            if (!this.transcriptionText) return '';
            const words = this.transcriptionText.split(/\s+/).filter(w => w).length;
            if (words === 0) return '';
            const chunks = Math.ceil(words / 2500);
            const mins = Math.max(1, chunks * 2);
            return `~${mins} min · ${words.toLocaleString()} palabras`;
        },

        async formatWithGemma() {
            this.formatting = true;
            this.progress = 0;
            this.statusText = 'Iniciando formateo...';

            try {
                const resp = await fetch('/api/format', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        transcription: this.transcriptionText,
                        model_name: this.config.model_name
                    })
                });

                const reader = resp.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                const processLine = async (line) => {
                    if (!line.startsWith('data: ')) return false;
                    try {
                        const data = JSON.parse(line.substring(6));
                        if (data.status === 'error') {
                            alert(data.detail);
                            this.formatting = false;
                            return true;
                        }
                        if (data.status === 'completado') {
                            // Guardar versión anterior antes de sobreescribir
                            if (this.articlesHtml) {
                                this.previousArticlesHtml = this.articlesHtml;
                                this.showingPrevious = false;
                            }
                            this.articlesHtml = data.articles_html;
                            this.generateTranscriptionHtml();
                            this.saveSession();
                            this.activeTab = 'formato';
                            await this.renderPreview();
                            this.initEditors();
                            this.formatting = false;
                            return true;
                        }
                        if (data.status) this.statusText = data.status.toUpperCase();
                        if (data.progress !== undefined) this.progress = data.progress;
                    } catch (e) {}
                    return false;
                };

                outer: while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (await processLine(line)) break outer;
                    }
                }

                if (buffer) await processLine(buffer);

            } catch (e) {
                alert("Error al formatear: " + e.message);
                this.formatting = false;
            }
        },

        downloadTxt() {
            const blob = new Blob([this.transcriptionText], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.courseSlug}_Clase${this.claseNum}_transcripcion.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        },

        // ── Historial de sesiones ──────────────────────────────

        saveSession() {
            const session = {
                id: Date.now(),
                videoTitle: this.videoInfo?.title || 'Sin título',
                videoId: this.videoInfo?.video_id || '',
                claseNum: parseInt(this.claseNum) || 1,
                courseSlug: this.courseSlug,
                articlesHtml: this.articlesHtml,
                createdAt: new Date().toISOString()
            };
            this.sessions.unshift(session);
            if (this.sessions.length > 30) this.sessions = this.sessions.slice(0, 30);
            try {
                localStorage.setItem('zorroazul_sessions', JSON.stringify(this.sessions));
            } catch(e) {
                // Quota exceeded: quitar la más vieja e intentar de nuevo
                this.sessions.pop();
                try { localStorage.setItem('zorroazul_sessions', JSON.stringify(this.sessions)); } catch(_) {}
            }
        },

        deleteSession(id) {
            this.sessions = this.sessions.filter(s => s.id !== id);
            try { localStorage.setItem('zorroazul_sessions', JSON.stringify(this.sessions)); } catch(_) {}
        },

        loadSession(session) {
            if (this.articlesHtml && this.articlesHtml !== session.articlesHtml) {
                this.previousArticlesHtml = this.articlesHtml;
            }
            this.articlesHtml = session.articlesHtml;
            this.claseNum = session.claseNum;
            this.courseSlug = session.courseSlug;
            this.showingPrevious = false;
            this.codeChanged = false;
            this.activeTab = 'formato';
            this.$nextTick(async () => {
                await this.renderPreview();
                this.initEditors();
            });
        },

        // ── Versión anterior ───────────────────────────────────

        togglePreviousVersion() {
            if (!this.previousArticlesHtml) return;
            const temp = this.articlesHtml;
            this.articlesHtml = this.previousArticlesHtml;
            this.previousArticlesHtml = temp;
            this.showingPrevious = !this.showingPrevious;
            this.codeChanged = false;
            this.$nextTick(async () => {
                await this.renderPreview();
                this.initEditors();
            });
        },

        // ── Editor y preview ───────────────────────────────────

        async applyCodeChanges() {
            if (this.editors.articles) {
                this.articlesHtml = this.editors.articles.getValue();
            }
            await this.renderPreview();
            this.codeChanged = false;
        },

        async renderPreview() {
            let content = this.articlesHtml;
            if (this.editors.articles) content = this.editors.articles.getValue();

            try {
                const resp = await fetch('/api/render-preview', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        articles_html: content,
                        metadata: {
                            tab_title: `Clase ${this.claseNum} — El Zorro Azul`,
                            super_label: `${this.config.default_super_label} · CLASE ${this.claseNum}`,
                            main_title: this.videoInfo?.title || '',
                            taught_by: this.taughtBy,
                            reviewed_by: this.reviewedBy,
                            video_id: this.videoInfo?.video_id
                        }
                    })
                });
                const data = await resp.json();
                this.previewHtml = data.html;
            } catch (e) {}
        },

        initEditors() {
            this.$nextTick(() => {
                if (this.activeTab === 'formato') {
                    const el = document.getElementById('editor-container');
                    const val = this.articlesHtml;
                    if (el && !this.editors.articles) {
                        this.editors.articles = CodeMirror(el, {
                            value: val,
                            mode: 'htmlmixed',
                            lineNumbers: true,
                            lineWrapping: true
                        });
                        this.editors.articles.on('change', () => { this.codeChanged = true; });
                    } else if (this.editors.articles) {
                        this.editors.articles.setValue(val);
                        this.editors.articles.refresh();
                        this.codeChanged = false;
                    }
                }
            });
        },

        generateTranscriptionHtml() {
            const lines = this.transcriptionText.split('\n');
            let html = '<article class="bg-white/70 backdrop-blur-xl border border-black/10 shadow-xl rounded-sm p-6 md:p-10 border-l-4 border-l-zorro-blue transition-all hover:bg-white/90">';
            html += '<h2 class="glitch-target font-headline text-xl md:text-2xl font-bold text-primary uppercase tracking-wide mb-6">Transcripción Completa</h2>';
            html += '<div class="space-y-2 text-primary/80 font-medium leading-relaxed">';

            lines.forEach(line => {
                if (!line.trim()) return;
                const match = line.match(/^\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(.*)/);
                if (match) {
                    const time = match[1];
                    const text = match[2];
                    html += `<p class="clickable-line cursor-pointer hover:bg-black/5 p-2 rounded-lg transition-all group">[[YT:${time}]] <span class="group-hover:text-zorro-blue transition-colors">${text}</span></p>`;
                } else {
                    html += `<p class="text-black/40 text-sm px-2">${line}</p>`;
                }
            });

            html += '</div></article>';
            this.transcriptionHtml = html;
        },

        // ── Publicar / Descargar ───────────────────────────────

        async saveLocal() {
            const filename = `${this.courseSlug}_Clase${this.claseNum}.html`;
            const htmlToSave = await this.renderHtmlForType();
            const blob = new Blob([htmlToSave], { type: 'text/html' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        },

        async publishToWordpress() {
            this.publishing = true;
            try {
                const filename = `${this.courseSlug}_Clase${this.claseNum}.html`;
                const htmlToPublish = await this.renderHtmlForType();
                const videoUrl = this.videoInfo?.video_id
                    ? `https://www.youtube.com/watch?v=${this.videoInfo.video_id}`
                    : null;

                const resp = await fetch('/api/publish-wordpress', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        html: htmlToPublish,
                        filename: filename,
                        clase_num: this.claseNum,
                        video_url: videoUrl,
                        wp_config: {
                            url: this.config.wp_url,
                            user: this.config.wp_user,
                            app_password: this.config.wp_app_password
                        }
                    })
                });

                if (!resp.ok) {
                    const err = await resp.json();
                    throw new Error(err.detail || "Error al publicar");
                }

                const data = await resp.json();
                this.publishUrl = data.url;

                let msg = `¡Publicado con éxito!\nURL: ${data.url}`;
                if (data.redirect?.status === 'ok') {
                    msg += `\n\nRedirección creada:\nelzorroazul.studio/video-clase-${this.claseNum} → YouTube`;
                } else if (data.redirect?.status === 'error') {
                    msg += `\n\n⚠ La página se subió, pero no se pudo crear la redirección.`;
                }
                alert(msg);
            } catch (e) {
                alert("Error al publicar en WordPress: " + e.message);
            } finally {
                this.publishing = false;
            }
        },

        async renderHtmlForType() {
            let content = this.articlesHtml;
            if (this.editors.articles) content = this.editors.articles.getValue();
            const resp = await fetch('/api/render-preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    articles_html: content,
                    metadata: {
                        tab_title: `Clase ${this.claseNum} — El Zorro Azul`,
                        super_label: `${this.config.default_super_label} · CLASE ${this.claseNum}`,
                        main_title: this.videoInfo?.title || '',
                        taught_by: this.taughtBy,
                        reviewed_by: this.reviewedBy,
                        show_credits: this.config.show_credits,
                        video_id: this.videoInfo?.video_id
                    }
                })
            });
            const data = await resp.json();
            return data.html;
        },

        formatDuration(seconds) {
            const m = Math.floor(seconds / 60);
            const s = seconds % 60;
            return `${m}:${s.toString().padStart(2, '0')}`;
        }
    };
}
