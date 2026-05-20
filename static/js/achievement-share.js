/**
 * Achievement Share Modal Component
 * Provides UI for students to quickly access sharing options
 * Triggered by "Share" buttons on achievement cards
 */

class AchievementShareModal {
    constructor() {
        this.modal = null;
        this.currentAchievementId = null;
        this.init();
    }

    /**
     * Initialize modal and event listeners
     */
    init() {
        // Modal HTML template
        const modalHTML = `
            <div id="achievement-share-modal" class="share-modal" style="display: none;">
                <div class="share-modal-overlay"></div>
                <div class="share-modal-content">
                    <div class="share-modal-header">
                        <h2>Share Your Achievement</h2>
                        <button class="close-btn" aria-label="Close modal">&times;</button>
                    </div>

                    <div class="share-modal-body">
                        <p class="share-intro">Choose how you'd like to share this achievement:</p>

                        <div class="share-options">
                            <button class="share-option" id="share-export-card" data-action="export">
                                <span class="option-icon">🎫</span>
                                <span class="option-text">
                                    <strong>Export Card</strong>
                                    <span class="option-desc">Generate PNG/PDF for social media</span>
                                </span>
                            </button>

                            <button class="share-option" id="share-verify-link" data-action="verify">
                                <span class="option-icon">🔗</span>
                                <span class="option-text">
                                    <strong>Verify Link</strong>
                                    <span class="option-desc">Share public verification page</span>
                                </span>
                            </button>

                            <button class="share-option" id="share-linkedin" data-action="linkedin">
                                <span class="option-icon">in</span>
                                <span class="option-text">
                                    <strong>LinkedIn</strong>
                                    <span class="option-desc">Post achievement on LinkedIn</span>
                                </span>
                            </button>

                            <button class="share-option" id="share-twitter" data-action="twitter">
                                <span class="option-icon">𝕏</span>
                                <span class="option-text">
                                    <strong>Twitter/X</strong>
                                    <span class="option-desc">Tweet your achievement</span>
                                </span>
                            </button>

                            <button class="share-option" id="share-copy" data-action="copy">
                                <span class="option-icon">📋</span>
                                <span class="option-text">
                                    <strong>Copy Link</strong>
                                    <span class="option-desc">Copy verification URL</span>
                                </span>
                            </button>
                        </div>

                        <div class="share-modal-footer">
                            <p class="share-info">
                                <strong>💡 Tip:</strong> Export cards include a QR code that others can scan to verify your achievement!
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Inject modal into page
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = modalHTML;
        document.body.appendChild(tempDiv.firstElementChild);

        this.modal = document.getElementById('achievement-share-modal');
        this.attachEventListeners();
    }

    /**
     * Attach event listeners to modal buttons
     */
    attachEventListeners() {
        // Close button
        document.querySelector('.share-modal .close-btn').addEventListener('click', () => this.close());

        // Overlay click to close
        document.querySelector('.share-modal-overlay').addEventListener('click', () => this.close());

        // Share options
        document.getElementById('share-export-card').addEventListener('click', () => this.handleExport());
        document.getElementById('share-verify-link').addEventListener('click', () => this.handleVerifyLink());
        document.getElementById('share-linkedin').addEventListener('click', () => this.handleLinkedIn());
        document.getElementById('share-twitter').addEventListener('click', () => this.handleTwitter());
        document.getElementById('share-copy').addEventListener('click', () => this.handleCopy());
    }

    /**
     * Open modal with achievement ID
     */
    open(achievementId) {
        this.currentAchievementId = achievementId;
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close modal
     */
    close() {
        this.modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        this.currentAchievementId = null;
    }

    /**
     * Handle export card action
     */
    handleExport() {
        if (!this.currentAchievementId) return;
        window.open(`/export-achievement/${this.currentAchievementId}`, '_blank', 'width=900,height=1000');
        this.close();
    }

    /**
     * Handle verify link action (copy + notify)
     */
    handleVerifyLink() {
        if (!this.currentAchievementId) return;
        const link = `${window.location.origin}/verify-achievement/${this.currentAchievementId}`;
        this.copyToClipboard(link);
        this.showNotification('Verification link copied! Share it anywhere.');
        this.close();
    }

    /**
     * Handle LinkedIn share
     */
    handleLinkedIn() {
        if (!this.currentAchievementId) return;
        const link = `${window.location.origin}/verify-achievement/${this.currentAchievementId}`;
        const url = encodeURIComponent(link);
        const title = encodeURIComponent('I just earned an achievement! 🎖️');
        window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank');
        this.close();
    }

    /**
     * Handle Twitter share
     */
    handleTwitter() {
        if (!this.currentAchievementId) return;
        const link = `${window.location.origin}/verify-achievement/${this.currentAchievementId}`;
        const url = encodeURIComponent(link);
        const text = encodeURIComponent('Just verified my achievement! Check it out: 🎖️');
        window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
        this.close();
    }

    /**
     * Handle copy to clipboard
     */
    handleCopy() {
        if (!this.currentAchievementId) return;
        const link = `${window.location.origin}/verify-achievement/${this.currentAchievementId}`;
        this.copyToClipboard(link);
        this.showNotification('Link copied to clipboard!');
        this.close();
    }

    /**
     * Utility: Copy to clipboard
     */
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).catch(err => {
            console.error('Failed to copy:', err);
        });
    }

    /**
     * Utility: Show toast notification
     */
    showNotification(message) {
        const toast = document.createElement('div');
        toast.className = 'share-notification';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

/**
 * Initialize when DOM is ready
 */
let achievementShareModal;
document.addEventListener('DOMContentLoaded', () => {
    achievementShareModal = new AchievementShareModal();
});

/**
 * Global helper function for achievement cards
 */
window.shareAchievement = function(achievementId) {
    if (achievementShareModal) {
        achievementShareModal.open(achievementId);
    }
};
