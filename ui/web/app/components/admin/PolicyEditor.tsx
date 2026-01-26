import { useEffect, useState } from 'react';
import { PolicyEditor as PolicyEditorView, type PolicyData, type PolicyFormState } from '@icgl/ui-components';

/**
 * Policy Editor
 * 
 * Visual interface for creating and managing channel policies at runtime.
 */

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

    const [formData, setFormData] = useState<PolicyFormState>({
        name: '',
        description: '',
        allowed_actions: [],
        max_messages: 100,
        max_duration_seconds: 300,
        requires_human_approval: false,
        alert_on_violations: true,
    });

    useEffect(() => {
        loadPolicies();
    }, []);

    const loadPolicies = async () => {
        try {
            setLoading(true);
            const baseUrl = 'http://127.0.0.1:8000';
            const res = await fetch(`${baseUrl}/policies`);
            const data = await res.json();
            setPolicies(data.policies || []);
        } catch (error) {
            console.error('Failed to load policies:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadPolicyDetails = async (policyName: string) => {
        // Fetch policy details from backend
        try {
            const baseUrl = 'http://127.0.0.1:8000';
            const res = await fetch(`${baseUrl}/policies/${policyName}`);
            if (!res.ok) {
                const err = await res.json();
                console.error('Policy fetch error:', err);
                alert(`Failed to load policy: ${err.detail || res.statusText}`);
                return;
            }
            const policy = await res.json();
            setSelectedPolicy(policy);

            // Scroll to details on small screens
            if (window.innerWidth <= 1100) {
                setTimeout(() => {
                    document.querySelector('.policy-details-panel')?.scrollIntoView({ behavior: 'smooth' });
                }, 100);
            }
        } catch (error) {
            console.error('Failed to load policy details:', error);
            alert('Failed to connect to server');
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
            alert_on_violations: true,
        });
    };

    const toggleAction = (action: string) => {
        if (formData.allowed_actions.includes(action)) {
            setFormData({
                ...formData,
                allowed_actions: formData.allowed_actions.filter(a => a !== action),
            });
        } else {
            setFormData({
                ...formData,
                allowed_actions: [...formData.allowed_actions, action],
            });
        }
    };

    const handleCreate = () => {
        alert('Policy creation coming soon!');
    };

    return (
        <PolicyEditorView
            policies={policies}
            selectedPolicy={selectedPolicy}
            loading={loading}
            formData={formData}
            availableActions={AVAILABLE_ACTIONS}
            onSelectPolicy={loadPolicyDetails}
            onToggleAction={toggleAction}
            onFormChange={(patch) => setFormData((prev) => ({ ...prev, ...patch }))}
            onResetForm={resetForm}
            onCreatePolicy={handleCreate}
        />
    );
}

export default PolicyEditor;
