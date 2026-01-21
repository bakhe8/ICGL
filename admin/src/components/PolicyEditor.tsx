import { useState, useEffect } from 'react';
import './PolicyEditor.css';

/**
 * Policy Editor
 * 
 * Visual interface for creating and managing channel policies at runtime.
 */

interface PolicyData {
    name: string;
    description: string;
    type: string;
    allowed_actions: string[];
    max_messages: number;
    max_duration_seconds: number;
    requires_human_approval: boolean;
    conditions_count?: number;
    alert_on_violations?: boolean;
}

const AVAILABLE_ACTIONS = [
    { value: 'READ_KB', label: '📚 Read KB', description: 'Query knowledge base' },
    { value: 'QUERY_SENTINEL', label: '🛡️ Query Sentinel', description: 'Check sentinel rules' },
    { value: 'SHARE_ANALYSIS', label: '🔍 Share Analysis', description: 'Share analysis results' },
    { value: 'REQUEST_REVIEW', label: '👀 Request Review', description: 'Ask for review' },
    { value: 'PROPOSE_CHANGE', label: '✏️ Propose Change', description: 'Suggest modifications' },
    { value: 'REQUEST_APPROVAL', label: '✅ Request Approval', description: 'Ask for approval' }
];

export function PolicyEditor() {
    const [policies, setPolicies] = useState<PolicyData[]>([]);
    const [selectedPolicy, setSelectedPolicy] = useState<PolicyData | null>(null);
    const [loading, setLoading] = useState(true);

    // Form state
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        allowed_actions: [] as string[],
        max_messages: 100,
        max_duration_seconds: 300,
        requires_human_approval: false,
        alert_on_violations: true
    });

    useEffect(() => {
        loadPolicies();
    }, []);

    const loadPolicies = async () => {
        try {
            setLoading(true);
            const res = await fetch('http://127.0.0.1:8000/policies');
            const data = await res.json();
            setPolicies(data.policies || []);
        } catch (error) {
            console.error('Failed to load policies:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadPolicyDetails = async (policyName: string) => {
        try {
            const res = await fetch(`http://127.0.0.1:8000/policies/${policyName}`);
            const policy = await res.json();
            setSelectedPolicy(policy);
        } catch (error) {
            console.error('Failed to load policy details:', error);
        }
    };

    const resetForm = () => {
        setFormData({
            name: '',
            description: '',
            allowed_actions: [],
            max_messages: 100,
            max_duration_seconds: 300,
            requires_human_approval: false,
            alert_on_violations: true
        });
    };

    const toggleAction = (action: string) => {
        if (formData.allowed_actions.includes(action)) {
            setFormData({
                ...formData,
                allowed_actions: formData.allowed_actions.filter(a => a !== action)
            });
        } else {
            setFormData({
                ...formData,
                allowed_actions: [...formData.allowed_actions, action]
            });
        }
    };

    if (loading) {
        return <div className="policy-editor loading">Loading policies...</div>;
    }

    return (
        <div className="policy-editor">
            <div className="editor-layout">
                {/* Policy List */}
                <div className="policy-list-panel">
                    <h2>📋 Available Policies</h2>
                    <div className="policy-list">
                        {policies.map(policy => (
                            <div
                                key={policy.name}
                                className={`policy-card ${selectedPolicy?.name === policy.name ? 'selected' : ''}`}
                                onClick={() => loadPolicyDetails(policy.name)}
                            >
                                <div className="policy-header">
                                    <h3>{policy.name}</h3>
                                    <span className={`policy-type type-${policy.type}`}>
                                        {policy.type}
                                    </span>
                                </div>
                                <p className="policy-description">{policy.description}</p>
                                <div className="policy-stats">
                                    <div className="stat">
                                        <span>{policy.allowed_actions.length}</span>
                                        <small>Actions</small>
                                    </div>
                                    <div className="stat">
                                        <span>{policy.max_messages}</span>
                                        <small>Max Msgs</small>
                                    </div>
                                    <div className="stat">
                                        <span>{policy.max_duration_seconds}s</span>
                                        <small>Duration</small>
                                    </div>
                                    {policy.conditions_count !== undefined && policy.conditions_count > 0 && (
                                        <div className="stat">
                                            <span>{policy.conditions_count}</span>
                                            <small>Conditions</small>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Policy Details / Editor */}
                <div className="policy-details-panel">
                    {selectedPolicy ? (
                        <div className="policy-details">
                            <div className="details-header">
                                <h2>{selectedPolicy.name}</h2>
                                <span className={`policy-type type-${selectedPolicy.type}`}>
                                    {selectedPolicy.type}
                                </span>
                            </div>

                            <p className="policy-description">{selectedPolicy.description}</p>

                            <div className="details-section">
                                <h3>🎯 Allowed Actions</h3>
                                <div className="action-grid">
                                    {selectedPolicy.allowed_actions.map(action => {
                                        const actionInfo = AVAILABLE_ACTIONS.find(a => a.value === action);
                                        return (
                                            <div key={action} className="action-badge">
                                                {actionInfo?.label || action}
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>

                            <div className="details-section">
                                <h3>⚙️ Limits</h3>
                                <div className="limits-grid">
                                    <div className="limit-item">
                                        <strong>Max Messages:</strong>
                                        <span>{selectedPolicy.max_messages}</span>
                                    </div>
                                    <div className="limit-item">
                                        <strong>Max Duration:</strong>
                                        <span>{selectedPolicy.max_duration_seconds}s</span>
                                    </div>
                                    <div className="limit-item">
                                        <strong>Human Approval:</strong>
                                        <span>{selectedPolicy.requires_human_approval ? '✅ Required' : '❌ Not Required'}</span>
                                    </div>
                                    <div className="limit-item">
                                        <strong>Alert on Violations:</strong>
                                        <span>{selectedPolicy.alert_on_violations ? '✅ Yes' : '❌ No'}</span>
                                    </div>
                                </div>
                            </div>

                            {selectedPolicy.type === 'conditional' && 'conditions' in selectedPolicy && (
                                <div className="details-section">
                                    <h3>🔀 Conditions</h3>
                                    <div className="conditions-list">
                                        {((selectedPolicy as unknown as { conditions: Array<{ type: string; operator: string; value: unknown; description?: string }> }).conditions || []).map((cond, idx: number) => (
                                            <div key={idx} className="condition-item">
                                                <div className="condition-type">{cond.type}</div>
                                                <div className="condition-operator">{cond.operator}</div>
                                                <div className="condition-value">{JSON.stringify(cond.value)}</div>
                                            </div>
                                        ))}
                                    </div>
                                    {('fallback_policy' in selectedPolicy) && (selectedPolicy as unknown as { fallback_policy?: string }).fallback_policy && (
                                        <div className="fallback-info">
                                            <strong>Fallback:</strong> {(selectedPolicy as unknown as { fallback_policy: string }).fallback_policy}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="no-selection">
                            <div className="empty-state">
                                <h3>📋 Select a Policy</h3>
                                <p>Click on a policy from the list to view details</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Create New Policy Panel */}
                <div className="policy-create-panel">
                    <h2>➕ Create New Policy</h2>

                    <div className="form-group">
                        <label>Policy Name</label>
                        <input
                            type="text"
                            placeholder="e.g., restricted_weekend"
                            value={formData.name}
                            onChange={e => setFormData({ ...formData, name: e.target.value })}
                        />
                    </div>

                    <div className="form-group">
                        <label>Description</label>
                        <textarea
                            placeholder="Describe when and how this policy should be used..."
                            value={formData.description}
                            onChange={e => setFormData({ ...formData, description: e.target.value })}
                            rows={3}
                        />
                    </div>

                    <div className="form-group">
                        <label>Allowed Actions ({formData.allowed_actions.length} selected)</label>
                        <div className="action-selector">
                            {AVAILABLE_ACTIONS.map(action => (
                                <label key={action.value} className="action-checkbox">
                                    <input
                                        type="checkbox"
                                        checked={formData.allowed_actions.includes(action.value)}
                                        onChange={() => toggleAction(action.value)}
                                        aria-label={`Toggle ${action.label}`}
                                        title={action.description}
                                    />
                                    <div className="action-info">
                                        <strong>{action.label}</strong>
                                        <small>{action.description}</small>
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Max Messages</label>
                            <input
                                type="number"
                                min="1"
                                value={formData.max_messages}
                                onChange={e => setFormData({ ...formData, max_messages: parseInt(e.target.value) })}
                            />
                        </div>

                        <div className="form-group">
                            <label>Max Duration (seconds)</label>
                            <input
                                type="number"
                                min="1"
                                value={formData.max_duration_seconds}
                                onChange={e => setFormData({ ...formData, max_duration_seconds: parseInt(e.target.value) })}
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={formData.requires_human_approval}
                                onChange={e => setFormData({ ...formData, requires_human_approval: e.target.checked })}
                                aria-label="Require human approval"
                                title="Require human approval for channel creation"
                            />
                            Require human approval for channel creation
                        </label>
                    </div>

                    <div className="form-group">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={formData.alert_on_violations}
                                onChange={e => setFormData({ ...formData, alert_on_violations: e.target.checked })}
                                aria-label="Alert on violations"
                                title="Send alert when policy violations occur"
                            />
                            Alert on policy violations
                        </label>
                    </div>

                    <div className="form-actions">
                        <button className="btn-secondary" onClick={resetForm}>
                            Reset
                        </button>
                        <button
                            className="btn-primary"
                            disabled={!formData.name || formData.allowed_actions.length === 0}
                            onClick={() => alert('Policy creation coming soon!')}
                        >
                            Create Policy
                        </button>
                    </div>

                    <div className="creation-notice">
                        <strong>ℹ️ Note:</strong> Custom policy creation requires backend support.
                        Currently viewing pre-defined policies only.
                    </div>
                </div>
            </div>
        </div>
    );
}

export default PolicyEditor;
