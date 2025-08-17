// static/js/auto_save.js
class AutoSave {
    constructor(formId, interval = 30000) {
        this.form = document.getElementById(formId);
        this.interval = interval;
        this.lastSave = Date.now();
        this.init();
    }

    init() {
        if (!this.form) return;

        // Auto-save on form changes
        this.form.addEventListener('input', () => {
            this.scheduleAutoSave();
        });

        // Save before page unload
        window.addEventListener('beforeunload', () => {
            this.saveForm();
        });

        this.startAutoSave();
    }

    scheduleAutoSave() {
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.saveForm();
        }, 5000); // Save 5 seconds after last change
    }

    startAutoSave() {
        setInterval(() => {
            if (this.hasChanges()) {
                this.saveForm();
            }
        }, this.interval);
    }

    hasChanges() {
        return Date.now() - this.lastSave > this.interval;
    }

    async saveForm() {
        const formData = new FormData(this.form);
        formData.append('auto_save', 'true');

        try {
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            if (response.ok) {
                this.showSaveIndicator('Guardado automáticamente');
                this.lastSave = Date.now();
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }

    showSaveIndicator(message) {
        const indicator = document.getElementById('auto-save-indicator');
        if (indicator) {
            indicator.textContent = message;
            indicator.style.opacity = '1';
            setTimeout(() => {
                indicator.style.opacity = '0';
            }, 2000);
        }
    }
}

// Initialize auto-save for forms
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('presurgeryForm')) {
        new AutoSave('presurgeryForm');
    }
    if (document.getElementById('postsurgeryForm')) {
        new AutoSave('postsurgeryForm');
    }
});