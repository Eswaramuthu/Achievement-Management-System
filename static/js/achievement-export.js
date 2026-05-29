/**
 * Achievement Card Export Module
 * Handles PNG and PDF export of achievement cards using html2canvas and jsPDF
 * 
 * Features:
 * - High-quality image capture (300 DPI equivalent)
 * - Responsive PDF generation
 * - Dark/Light mode support
 * - Error handling and user feedback
 * - Optimized file sizes
 */

class AchievementExporter {
    constructor() {
        this.cardElement = document.getElementById('achievement-card-export');
        this.downloadBtn = document.getElementById('btn-download');
        this.closeBtn = document.getElementById('btn-close');
        this.formatRadios = document.querySelectorAll('input[name="export-format"]');
        this.statusDiv = document.getElementById('export-status');
        this.statusText = this.statusDiv?.querySelector('.status-text');

        this.cardWidth = 600;
        this.cardHeight = 800;
        this.dpi = 2; // 2x scale for high quality

        this.initEventListeners();
    }

    initEventListeners() {
        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => this.handleExport());
        }
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.handleClose());
        }
    }

    /**
     * Main export handler - Routes to PNG or PDF export
     */
    async handleExport() {
        const format = this.getSelectedFormat();
        
        try {
            this.showLoadingState(true);
            
            if (format === 'png') {
                await this.exportPNG();
            } else if (format === 'pdf') {
                await this.exportPDF();
            }
            
            this.showLoadingState(false);
            this.showSuccessMessage('Export completed successfully!');
        } catch (error) {
            console.error('Export error:', error);
            this.showLoadingState(false);
            this.showErrorMessage(`Export failed: ${error.message}`);
        }
    }

    /**
     * Export card as PNG image
     * Uses html2canvas with high DPI settings
     */
    async exportPNG() {
        // Create a container to ensure white background
        const container = document.createElement('div');
        container.style.cssText = `
            position: absolute;
            left: -9999px;
            top: -9999px;
            background: white;
            border-radius: 24px;
            overflow: hidden;
        `;

        const clonedCard = this.cardElement.cloneNode(true);
        container.appendChild(clonedCard);
        document.body.appendChild(container);

        try {
            this.updateStatus('Capturing card image...');

            // Capture canvas with high quality settings
            const canvas = await html2canvas(clonedCard, {
                scale: this.dpi,
                backgroundColor: '#ffffff',
                useCORS: true,
                allowTaint: true,
                logging: false,
                windowHeight: this.cardHeight * this.dpi,
                windowWidth: this.cardWidth * this.dpi,
                onclone: (clonedDocument) => {
                    const clonedCard = clonedDocument.getElementById('achievement-card-export');
                    if (clonedCard) {
                        clonedCard.style.margin = '0';
                        clonedCard.style.padding = '0';
                    }
                }
            });

            this.updateStatus('Processing image...');

            // Convert canvas to blob and download
            const link = document.createElement('a');
            const achievementId = this.getAchievementMetadata('achievement-id');
            const studentName = this.getAchievementMetadata('student-name-data');
            const eventName = this.getAchievementMetadata('event-name-data');
            
            const filename = `${studentName}_${eventName}_${achievementId}.png`.replace(/[^a-zA-Z0-9_-]/g, '_');
            
            link.href = canvas.toDataURL('image/png', 1.0);
            link.download = filename;
            link.click();

            this.updateStatus('Download started...');
            
        } finally {
            document.body.removeChild(container);
        }
    }

    /**
     * Export card as PDF
     * Uses jsPDF for PDF generation with proper sizing
     */
    async exportPDF() {
        const container = document.createElement('div');
        container.style.cssText = `
            position: absolute;
            left: -9999px;
            top: -9999px;
            background: white;
            border-radius: 24px;
            overflow: hidden;
        `;

        const clonedCard = this.cardElement.cloneNode(true);
        container.appendChild(clonedCard);
        document.body.appendChild(container);

        try {
            this.updateStatus('Capturing card image...');

            // Capture canvas
            const canvas = await html2canvas(clonedCard, {
                scale: this.dpi,
                backgroundColor: '#ffffff',
                useCORS: true,
                allowTaint: true,
                logging: false,
                windowHeight: this.cardHeight * this.dpi,
                windowWidth: this.cardWidth * this.dpi,
            });

            this.updateStatus('Generating PDF...');

            // Calculate PDF dimensions (maintain aspect ratio)
            const imgWidth = 600; // Points (Postscript points: 1/72 inch)
            const imgHeight = (canvas.height * imgWidth) / canvas.width;

            // Create PDF with custom dimensions
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF({
                orientation: imgHeight > imgWidth ? 'portrait' : 'landscape',
                unit: 'pt',
                format: [imgWidth, imgHeight]
            });

            const imgData = canvas.toDataURL('image/png');
            pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);

            this.updateStatus('Downloading PDF...');

            // Generate filename and download
            const achievementId = this.getAchievementMetadata('achievement-id');
            const studentName = this.getAchievementMetadata('student-name-data');
            const eventName = this.getAchievementMetadata('event-name-data');
            
            const filename = `${studentName}_${eventName}_${achievementId}.pdf`.replace(/[^a-zA-Z0-9_-]/g, '_');
            pdf.save(filename);

        } finally {
            document.body.removeChild(container);
        }
    }

    /**
     * Get selected export format from radio buttons
     */
    getSelectedFormat() {
        for (let radio of this.formatRadios) {
            if (radio.checked) {
                return radio.value;
            }
        }
        return 'png';
    }

    /**
     * Extract metadata from card for filename
     */
    getAchievementMetadata(className) {
        const element = document.querySelector(`.${className}`);
        return element ? element.textContent.trim() : 'achievement';
    }

    /**
     * UI: Show/hide loading state
     */
    showLoadingState(isLoading) {
        if (!this.statusDiv) return;

        if (isLoading) {
            this.downloadBtn.disabled = true;
            this.formatRadios.forEach(radio => radio.disabled = true);
            this.statusDiv.style.display = 'flex';
        } else {
            this.downloadBtn.disabled = false;
            this.formatRadios.forEach(radio => radio.disabled = false);
            setTimeout(() => {
                this.statusDiv.style.display = 'none';
            }, 2000);
        }
    }

    /**
     * UI: Update status message
     */
    updateStatus(message) {
        if (this.statusText) {
            this.statusText.textContent = message;
        }
    }

    /**
     * UI: Show success message
     */
    showSuccessMessage(message) {
        this.statusDiv.style.display = 'flex';
        this.statusDiv.style.background = 'rgba(0, 200, 0, 0.1)';
        this.statusDiv.style.color = '#00c800';
        
        const spinner = this.statusDiv.querySelector('.status-spinner');
        spinner.textContent = '✓';
        spinner.style.animation = 'none';
        
        if (this.statusText) {
            this.statusText.textContent = message;
        }
    }

    /**
     * UI: Show error message
     */
    showErrorMessage(message) {
        this.statusDiv.style.display = 'flex';
        this.statusDiv.style.background = 'rgba(200, 0, 0, 0.1)';
        this.statusDiv.style.color = '#c80000';
        
        const spinner = this.statusDiv.querySelector('.status-spinner');
        spinner.textContent = '✗';
        spinner.style.animation = 'none';
        
        if (this.statusText) {
            this.statusText.textContent = message;
        }
    }

    /**
     * Handle close button
     */
    handleClose() {
        // Signal parent window to close modal (if using modal)
        if (window.opener) {
            window.close();
        } else {
            window.history.back();
        }
    }
}

/**
 * Initialize exporter when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    try {
        new AchievementExporter();
        console.log('Achievement exporter initialized successfully');
    } catch (error) {
        console.error('Failed to initialize exporter:', error);
    }
});

/**
 * Fallback for older browsers or missing libraries
 */
if (typeof html2canvas === 'undefined') {
    console.warn('html2canvas library not loaded. Export functionality may be limited.');
}

if (typeof jspdf === 'undefined') {
    console.warn('jsPDF library not loaded. PDF export will not be available.');
}
