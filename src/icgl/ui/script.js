const API_BASE = "http://127.0.0.1:8000";
let activeAdrId = null;

// Initialize Mermaid
if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        securityLevel: 'loose',
        themeVariables: {
            primaryColor: '#6366f1',
            lineColor: '#6366f1',
            fontSize: '14px',
            fontFamily: 'Outfit'
        }
    });
}

// --- DOM Elements ---
const propForm = document.getElementById('propose-form');
const adrList = document.getElementById('adr-list');
const analysisDisplay = document.getElementById('analysis-display');
const analysisLoading = document.getElementById('analysis-loading');
const decisionActions = document.getElementById('decision-actions');
const overallConf = document.getElementById('overall-conf');

const WS_BASE = "ws://127.0.0.1:8000";
let statusSocket = null;

// Initialize WebSockets
function initWebSockets() {
    statusSocket = new WebSocket(`${WS_BASE}/ws/status`);
    statusSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'status_update') {
            updateDashboardStatus(data.status);
        }
    };
    statusSocket.onclose = () => {
        setTimeout(initWebSockets, 5000); // Auto-reconnect
    };
}

function updateDashboardStatus(status) {
    // Decision State Update
    document.getElementById('state-awaiting').innerText = status.waiting_for_human ? "YES" : "NO";
    document.getElementById('state-awaiting').className = status.waiting_for_human ? "val waiting" : "val";

    document.getElementById('state-alert').innerText = status.active_alert_level;
    document.getElementById('state-alert').className = status.active_alert_level === "CRITICAL" ? "val critical" : "val";

    // Awareness Metrics
    if (status.telemetry) {
        document.getElementById('stat-drifts').innerText = status.telemetry.drift_detection_count;
        document.getElementById('stat-failures').innerText = status.telemetry.agent_failure_count;
        document.getElementById('stat-latency').innerText = (status.telemetry.last_latency_ms || 0) + "ms";
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await checkHealth();
    refreshKB();
    initWebSockets();
});

// ... refreshMetrics remains for manual sync if needed, but WS handles live updates
async function refreshMetrics() {
    try {
        const res = await fetch(`${API_BASE}/status`);
        const status = await res.json();
        updateDashboardStatus(status);
    } catch (e) {
        console.error("Metric sync failed", e);
    }
}

async function checkHealth() {
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');
    try {
        const res = await fetch(`${API_BASE}/health`);
        const health = await res.json();
        if (health.api === "healthy" && health.engine_ready) {
            statusText.innerText = "SYSTEM READY";
            statusDot.className = "dot-idle";
        } else if (!health.engine_ready) {
            statusText.innerText = "ENGINE BOOTING...";
            statusDot.className = "pulse";
        } else {
            statusText.innerText = "DEGRADED: " + (health.db_error || "Unknown");
            statusDot.className = "dot-alert";
        }
    } catch (e) {
        statusText.innerText = "SERVER OFFLINE";
        statusDot.className = "dot-alert";
    }
}

async function refreshKB() {
    try {
        const res = await fetch(`${API_BASE}/kb/adrs`);
        const adrs = await res.json();

        adrList.innerHTML = adrs.map(adr => `
            <div class="adr-item" onclick="viewAnalysis('${adr.id}')">
                <h3>${adr.title}</h3>
                <span class="status ${adr.status}">${adr.status}</span>
                <p style="font-size: 0.7rem; color: #888; margin-top: 5px;">${new Date(adr.created_at).toLocaleString()}</p>
            </div>
        `).join('');
    } catch (e) {
        adrList.innerHTML = "<p>Error loading log.</p>";
    }
}

propForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        title: document.getElementById('prop-title').value,
        context: document.getElementById('prop-context').value,
        decision: document.getElementById('prop-decision').value
    };

    try {
        analysisLoading.classList.remove('hidden');
        analysisDisplay.innerHTML = "";
        decisionActions.classList.add('hidden');
        const mapSection = document.getElementById('consensus-map-section');
        const medSection = document.getElementById('mediation-section');
        if (mapSection) mapSection.classList.add('hidden');
        if (medSection) medSection.classList.add('hidden');

        const res = await fetch(`${API_BASE}/propose`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        activeAdrId = result.adr_id;

        // Start listening via WebSocket
        listenForAnalysis(activeAdrId);
    } catch (e) {
        alert("Proposal failed: " + e.message);
    }
});

function listenForAnalysis(adrId) {
    if (!adrId) return;
    const socket = new WebSocket(`${WS_BASE}/ws/analysis/${adrId}`);
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.synthesis) {
            renderAnalysis(data);
            analysisLoading.classList.add('hidden');
            socket.close();
        }
    };
}

function renderAnalysis(data) {
    overallConf.innerText = Math.round(data.synthesis.overall_confidence * 100) + "%";
    const mode = document.querySelector('input[name="mode"]:checked').value;

    // Render Mermaid Map if available
    const mapSection = document.getElementById('consensus-map-section');
    const mapContainer = document.getElementById('consensus-map');

    if (data.synthesis.mindmap) {
        mapSection.classList.remove('hidden');
        mapContainer.innerHTML = data.synthesis.mindmap;
        mapContainer.removeAttribute('data-processed');
        if (typeof mermaid !== 'undefined') {
            mermaid.run({
                nodes: [mapContainer]
            });
        }
    } else {
        if (mapSection) mapSection.classList.add('hidden');
    }

    // Mediation Rendering (Phase G)
    const medSection = document.getElementById('mediation-section');
    const medContent = document.getElementById('mediation-content');
    if (data.synthesis.mediation) {
        medSection.classList.remove('hidden');
        medContent.innerHTML = `
            <div class="mediation-text">
                <p>${data.synthesis.mediation.analysis.replace(/\n/g, '<br>')}</p>
                ${data.synthesis.mediation.concerns.length > 0 ? `
                    <div style="margin-top: 1rem; color: #f87171; font-size: 0.85rem;">
                        <strong>Residual Risks:</strong> ${data.synthesis.mediation.concerns.join(', ')}
                    </div>
                ` : ''}
            </div>
        `;
    } else {
        if (medSection) medSection.classList.add('hidden');
    }

    let html = `
        <div class="consensus-box" style="margin-bottom: 2rem;">
            <h2>✅ Consensus Recommendations</h2>
            <ul>${data.synthesis.consensus_recommendations.map(r => `<li>${r}</li>`).join('')}</ul>
        </div>
        
        <div class="concerns-box" style="margin-bottom: 2rem;">
            <h2 style="color: var(--accent-danger)">⚠️ Critical Concerns</h2>
            <ul>${data.synthesis.all_concerns.map(c => `<li>${c}</li>`).join('')}</ul>
        </div>

        <div class="historical-echo">
            <h2>📜 Historical Echo (S-11)</h2>
            ${(data.synthesis.semantic_matches && data.synthesis.semantic_matches.length > 0) ?
            data.synthesis.semantic_matches.map(m => `
                <div class="echo-item">
                    <span>${m.title}</span>
                    <span class="match-score">${m.score}% Match</span>
                </div>
            `).join('') : '<p>No matching historical ADRs found.</p>'}
        </div>

        <div class="sentinel-alerts">
            <h2>🚨 Sentinel Detailed Signals</h2>
            ${(data.synthesis.sentinel_alerts && data.synthesis.sentinel_alerts.length > 0) ?
            data.synthesis.sentinel_alerts.map(a => `
                <div class="alert-item">
                    <span class="severity-${a.severity}">[${a.id}] ${a.message}</span>
                    <span class="category">${a.category}</span>
                </div>
            `).join('') : '<p>No system alerts detected.</p>'}
        </div>

        <div class="agents-grid" style="margin-top: 2rem;">
            ${data.synthesis.agent_results.map(res => `
                <div class="agent-bubble">
                    <h4>${res.role} Agent Analysis</h4>
                    <p style="font-size:0.9rem;">${res.analysis}</p>
                    <div style="margin-top:10px; font-size: 0.8rem; color: var(--accent-primary);">
                        Confidence: ${Math.round(res.confidence * 100)}%
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    analysisDisplay.innerHTML = html;

    // Mode-Aware Decision Actions
    if (mode === 'decide' || mode === 'experiment') {
        const hasCritical = data.synthesis.sentinel_alerts && data.synthesis.sentinel_alerts.some(a => a.severity === 'CRITICAL');
        if (hasCritical) {
            decisionActions.innerHTML = `
                <hr>
                <div class="escalation-required">
                    🚨 CRITICAL RISK DETECTED. ESCALATION REQUIRED. SIGNATURE BLOCKED.
                </div>
            `;
            decisionActions.classList.remove('hidden');
        } else {
            decisionActions.classList.remove('hidden');
        }
    } else {
        decisionActions.classList.add('hidden');
    }
}

async function handleSign(action) {
    const rationale = document.getElementById('sign-rationale').value;
    if (!rationale) {
        alert("Sovereign rationale is required for the immutable log.");
        return;
    }

    if (!activeAdrId) {
        alert("No active ADR selected. Submit a proposal or open an existing ADR first.");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/sign/${activeAdrId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, rationale, human_id: 'user' })
        });

        if (!res.ok) {
            const detail = await res.text();
            alert(`Signing failed (${res.status}): ${detail}`);
            return;
        }

        alert(`Decision ${action} Finalized.`);
        refreshKB();
        decisionActions.classList.add('hidden');
        analysisDisplay.innerHTML = `<div class="placeholder-msg">Decision Submitted: ${action}</div>`;
    } catch (e) {
        alert("Signing failed: " + e.message);
    }
}

async function viewAnalysis(adrId) {
    if (!adrId || adrId === "undefined") return;
    activeAdrId = adrId;
    analysisLoading.classList.remove('hidden');
    analysisDisplay.innerHTML = "";
    decisionActions.classList.add('hidden');
    const mapSection = document.getElementById('consensus-map-section');
    if (mapSection) mapSection.classList.add('hidden');

    try {
        const res = await fetch(`${API_BASE}/analysis/${adrId}`);
        const data = await res.json();
        renderAnalysis(data);
        analysisLoading.classList.add('hidden');
    } catch (e) {
        analysisDisplay.innerHTML = "<p>Historical analysis not found.</p>";
        analysisLoading.classList.add('hidden');
    }
}
