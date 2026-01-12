document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    function isMobile() {
        return window.innerWidth <= 768;
    }

    function updateAria() {
        if (!sidebar) return;
        const isOpen = !isMobile() || sidebar.classList.contains('show');
        sidebar.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
        if (sidebarToggle) {
            sidebarToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        }
    }

    function toggleSidebar() {
        if (!sidebar || !sidebarOverlay) return;
        
        sidebar.classList.toggle('show');
        sidebarOverlay.classList.toggle('show');
        updateAria();
        
        // サイドバーが開いているときはスクロールを防止
        if (sidebar.classList.contains('show')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }

    function closeSidebar() {
        if (!sidebar || !sidebarOverlay) return;
        
        sidebar.classList.remove('show');
        sidebarOverlay.classList.remove('show');
        document.body.style.overflow = '';
        updateAria();
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleSidebar();
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // サイドバー内のリンクをクリックしたら（モバイルの場合）閉じる
    if (sidebar) {
        const navLinks = sidebar.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    // 少し遅延させてクリックエフェクトが見えるようにしてもいいが、即座に閉じる
                    closeSidebar();
                }
            });
        });
    }

    // 画面サイズ変更時にリセット
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeSidebar();
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('show')) {
            closeSidebar();
        }
    });

    function setupDraftForms() {
        const forms = document.querySelectorAll('.js-draft-form[data-draft-key][data-draft-enabled="true"]');
        if (!forms.length) return;

        function isSavableField(field) {
            if (!field.name || field.disabled) return false;
            const type = field.type;
            return !['file', 'password', 'hidden', 'submit', 'button'].includes(type);
        }

        function showDraftNotice(form, storageKey, savedAt) {
            const notice = document.createElement('div');
            notice.className = 'alert alert-info draft-alert';
            const savedText = savedAt ? `（保存: ${new Date(savedAt).toLocaleString()}）` : '';
            notice.innerHTML = `
                <div>下書きを復元しました ${savedText}</div>
                <button type="button" class="btn btn-sm btn-outline-secondary">下書きを破棄</button>
            `;
            const clearButton = notice.querySelector('button');
            clearButton.addEventListener('click', function() {
                try {
                    localStorage.removeItem(storageKey);
                } catch (err) {
                    // Ignore localStorage errors
                }
                notice.remove();
            });
            form.prepend(notice);
        }

        forms.forEach(form => {
            const draftKey = form.dataset.draftKey;
            if (!draftKey) return;
            const storageKey = `memoscribe:draft:${draftKey}`;
            const fields = Array.from(form.elements).filter(isSavableField);

            try {
                const saved = localStorage.getItem(storageKey);
                if (saved) {
                    const draft = JSON.parse(saved);
                    const values = draft.values || {};
                    fields.forEach(field => {
                        if (!(field.name in values)) return;
                        if (field.type === 'checkbox') {
                            field.checked = Boolean(values[field.name]);
                        } else if (field.type === 'radio') {
                            field.checked = field.value === values[field.name];
                        } else {
                            field.value = values[field.name];
                        }
                    });
                    if (Object.keys(values).length) {
                        showDraftNotice(form, storageKey, draft.savedAt);
                    }
                }
            } catch (err) {
                // Ignore malformed drafts
            }

            let saveTimer;
            function scheduleSave() {
                clearTimeout(saveTimer);
                saveTimer = setTimeout(function() {
                    const values = {};
                    fields.forEach(field => {
                        if (field.type === 'checkbox') {
                            values[field.name] = field.checked;
                        } else if (field.type === 'radio') {
                            if (field.checked) {
                                values[field.name] = field.value;
                            }
                        } else {
                            values[field.name] = field.value;
                        }
                    });
                    try {
                        localStorage.setItem(storageKey, JSON.stringify({ values: values, savedAt: new Date().toISOString() }));
                    } catch (err) {
                        // Ignore localStorage errors
                    }
                }, 500);
            }

            fields.forEach(field => {
                field.addEventListener('input', scheduleSave);
                field.addEventListener('change', scheduleSave);
            });

            form.addEventListener('submit', function() {
                try {
                    localStorage.removeItem(storageKey);
                } catch (err) {
                    // Ignore localStorage errors
                }
            });
        });
    }

    function setupSuggestionChips() {
        document.addEventListener('click', function(e) {
            const chip = e.target.closest('[data-fill-target]');
            if (!chip) return;
            const targetId = chip.getAttribute('data-fill-target');
            const target = document.getElementById(targetId);
            if (!target) return;
            const value = chip.getAttribute('data-fill-value') || chip.textContent.trim();
            target.value = value;
            target.focus();
            target.dispatchEvent(new Event('input', { bubbles: true }));
        });
    }

    function setupDocumentStatusPolling() {
        const table = document.querySelector('[data-doc-status-list]');
        if (!table) return;
        const statusUrl = table.getAttribute('data-status-url');
        if (!statusUrl) return;

        const statusMap = {
            pending: { label: '待機中', className: 'bg-secondary' },
            processing: { label: '処理中', className: 'bg-warning' },
            completed: { label: '完了', className: 'bg-success' },
            failed: { label: '失敗', className: 'bg-danger' },
        };

        function hasPending(rows) {
            return rows.some(row => ['pending', 'processing'].includes(row.dataset.status));
        }

        function updateBadge(badge, status) {
            const map = statusMap[status] || statusMap.pending;
            badge.className = `badge ${map.className}`;
            badge.textContent = map.label;
        }

        function poll() {
            const rows = Array.from(table.querySelectorAll('[data-doc-id]'));
            if (!rows.length) return;
            const ids = rows.map(row => row.dataset.docId).join(',');
            fetch(`${statusUrl}?ids=${encodeURIComponent(ids)}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.json())
                .then(data => {
                    const docs = data.documents || [];
                    docs.forEach(doc => {
                        const row = table.querySelector(`[data-doc-id="${doc.id}"]`);
                        if (!row) return;
                        row.dataset.status = doc.status;
                        const badge = row.querySelector('[data-doc-status]');
                        if (badge) updateBadge(badge, doc.status);
                    });

                    if (hasPending(rows)) {
                        setTimeout(poll, 5000);
                    }
                })
                .catch(function() {
                    setTimeout(poll, 8000);
                });
        }

        const rows = Array.from(table.querySelectorAll('[data-doc-id]'));
        if (hasPending(rows)) {
            poll();
        }
    }

    setupDraftForms();
    setupSuggestionChips();
    setupDocumentStatusPolling();
    updateAria();
});
