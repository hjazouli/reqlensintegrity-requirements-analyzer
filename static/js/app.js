// Global state
let sessionId = 'session_' + Date.now();
let currentFileLoaded = false;
let comparisonFileLoaded = false;
let analysisData = null;

// File upload handler
async function handleFileUpload(input, type) {
    const file = input.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    formData.append('session_id', sessionId);

    showLoading();

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            const statusEl = document.getElementById(type + 'Status');
            statusEl.className = 'upload-status success';
            statusEl.innerHTML = `<i class="fas fa-check-circle"></i> ${data.filename} - ${data.message}`;

            if (type === 'current') {
                currentFileLoaded = true;
            } else {
                comparisonFileLoaded = true;
            }

            // Enable analyze button if current file is loaded
            if (currentFileLoaded) {
                document.getElementById('analyzeBtn').disabled = false;
            }

            showToast('success', `File loaded: ${data.filename}`);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        const statusEl = document.getElementById(type + 'Status');
        statusEl.className = 'upload-status error';
        statusEl.innerHTML = `<i class="fas fa-times-circle"></i> Error: ${error.message}`;
        showToast('error', error.message);
    } finally {
        hideLoading();
    }
}

// Perform analysis
async function performAnalysis() {
    if (!currentFileLoaded) {
        showToast('warning', 'Please load a requirements file first');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId })
        });

        const data = await response.json();

        if (data.success) {
            analysisData = data;

            // Show tabs
            document.getElementById('tabsSection').style.display = 'flex';
            document.getElementById('tabContent').style.display = 'block';

            // Load overview
            await loadOverview();

            // Load changes if available
            if (data.changes && data.changes.length > 0) {
                loadChanges(data.changes);
                await loadImpact();
            }

            showToast('success', 'Analysis complete!');
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        showToast('error', error.message);
    } finally {
        hideLoading();
    }
}

// Load overview visualizations
async function loadOverview() {
    try {
        const response = await fetch('/visualizations/overview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId })
        });

        const data = await response.json();

        if (data.success) {
            // Display metrics
            const metricsHtml = `
                <div class="metric-card">
                    <div class="metric-value">${data.metrics.total.toLocaleString()}</div>
                    <div class="metric-label">Total Requirements</div>
                </div>
                <div class="metric-card success">
                    <div class="metric-value">${data.metrics.with_tests}</div>
                    <div class="metric-label">With Test Cases</div>
                </div>
                <div class="metric-card warning">
                    <div class="metric-value">${data.metrics.with_comments}</div>
                    <div class="metric-label">With Comments</div>
                </div>
                <div class="metric-card info">
                    <div class="metric-value">${data.metrics.with_dependencies}</div>
                    <div class="metric-label">With Dependencies</div>
                </div>
            `;
            document.getElementById('metricsGrid').innerHTML = metricsHtml;

            // Display charts
            if (data.charts.category) {
                Plotly.newPlot('categoryChart', JSON.parse(data.charts.category).data,
                    JSON.parse(data.charts.category).layout, { responsive: true });
            }
            if (data.charts.state) {
                Plotly.newPlot('stateChart', JSON.parse(data.charts.state).data,
                    JSON.parse(data.charts.state).layout, { responsive: true });
            }
            if (data.charts.section) {
                Plotly.newPlot('sectionChart', JSON.parse(data.charts.section).data,
                    JSON.parse(data.charts.section).layout, { responsive: true });
            }
        }
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

// Load changes table
function loadChanges(changes) {
    if (!changes || changes.length === 0) {
        document.getElementById('changesTable').innerHTML = `
            <div style="text-align: center; padding: 3rem; color: #666;">
                <i class="fas fa-info-circle" style="font-size: 3rem; margin-bottom: 1rem; display: block;"></i>
                <p>No changes detected. Load a comparison file to see changes.</p>
            </div>
        `;
        return;
    }

    let tableHtml = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Type</th>
                    <th>Section</th>
                    <th>Category</th>
                    <th>Impact</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
    `;

    changes.forEach(change => {
        const impactClass = `impact-${change.impact_level.toLowerCase()}`;
        const badgeClass = `badge-${change.type.toLowerCase()}`;
        const description = truncateText(change.text, 100);

        tableHtml += `
            <tr>
                <td><strong>${change.id}</strong></td>
                <td><span class="badge ${badgeClass}">${change.type}</span></td>
                <td>${change.section}</td>
                <td>${change.category}</td>
                <td><span class="${impactClass}">${change.impact_level}</span></td>
                <td>${description}</td>
            </tr>
        `;
    });

    tableHtml += `
            </tbody>
        </table>
    `;

    document.getElementById('changesTable').innerHTML = tableHtml;
}

// Load impact analysis
async function loadImpact() {
    try {
        const response = await fetch('/visualizations/impact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId })
        });

        const data = await response.json();

        if (data.success) {
            // Display impact metrics
            const metricsHtml = `
                <div class="metric-card" style="background: linear-gradient(135deg, #E63946 0%, #c52a36 100%);">
                    <div class="metric-value">${data.metrics.high}</div>
                    <div class="metric-label">High Impact</div>
                </div>
                <div class="metric-card" style="background: linear-gradient(135deg, #F77F00 0%, #d67200 100%);">
                    <div class="metric-value">${data.metrics.medium}</div>
                    <div class="metric-label">Medium Impact</div>
                </div>
                <div class="metric-card" style="background: linear-gradient(135deg, #06A77D 0%, #048a65 100%);">
                    <div class="metric-value">${data.metrics.low}</div>
                    <div class="metric-label">Low Impact</div>
                </div>
            `;
            document.getElementById('impactMetrics').innerHTML = metricsHtml;

            // Display impact chart
            Plotly.newPlot('impactChart', JSON.parse(data.chart).data,
                JSON.parse(data.chart).layout, { responsive: true });

            // Display affected items
            const affectedHtml = `
                <div style="margin-top: 2rem;">
                    <h3 style="font-size: 1.3rem; margin-bottom: 1rem;">
                        <i class="fas fa-layer-group"></i> Affected Categories
                    </h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${data.metrics.categories_affected.map(cat =>
                `<span class="badge" style="background: rgba(46, 134, 171, 0.1); color: var(--primary);">${cat}</span>`
            ).join('')}
                    </div>
                </div>
            `;
            document.getElementById('affectedItems').innerHTML = affectedHtml;
        }
    } catch (error) {
        console.error('Error loading impact:', error);
    }
}

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.closest('.tab').classList.add('active');

    // Update tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.getElementById(tabName + '-tab').classList.add('active');
}

// Export data
async function exportData() {
    if (!analysisData) {
        showToast('warning', 'Please analyze requirements first');
        return;
    }

    const exportType = analysisData.changes && analysisData.changes.length > 0
        ? confirm('Export changes only?\n\nOK = Changes only\nCancel = All requirements')
            ? 'changes'
            : 'all'
        : 'all';

    showLoading();

    try {
        const response = await fetch('/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                type: exportType
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `requirements_${exportType}_${Date.now()}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showToast('success', 'Export complete!');
        } else {
            throw new Error('Export failed');
        }
    } catch (error) {
        showToast('error', error.message);
    } finally {
        hideLoading();
    }
}

// Utility functions
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showToast(type, message) {
    const icon = type === 'success' ? 'fa-check-circle' :
        type === 'error' ? 'fa-times-circle' :
            'fa-exclamation-circle';

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <div>${message}</div>
    `;

    document.getElementById('toastContainer').appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function truncateText(text, maxLength) {
    if (!text || text === 'NaN' || text === 'nan') return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Drag and drop support
document.addEventListener('DOMContentLoaded', function () {
    const uploadLabels = document.querySelectorAll('.upload-label');

    uploadLabels.forEach(label => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            label.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            label.addEventListener(eventName, () => {
                label.style.borderColor = 'var(--primary-dark)';
                label.style.background = 'rgba(46, 134, 171, 0.15)';
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            label.addEventListener(eventName, () => {
                label.style.borderColor = 'var(--primary)';
                label.style.background = 'rgba(46, 134, 171, 0.05)';
            });
        });

        label.addEventListener('drop', function (e) {
            const input = this.querySelector('input[type="file"]');
            if (e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                const type = input.id === 'currentFile' ? 'current' : 'comparison';
                handleFileUpload(input, type);
            }
        });
    });
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}
