import React from "react";
import "./PolicyEditor.css";

export interface PolicyData {
  name: string;
  description: string;
  type: string;
  allowed_actions: string[];
  max_messages: number;
  max_duration_seconds: number;
  requires_human_approval: boolean;
  conditions_count?: number;
  alert_on_violations?: boolean;
  conditions?: PolicyCondition[];
  fallback_policy?: string;
}

export interface PolicyCondition {
  type: string;
  operator: string;
  value: unknown;
}

export interface PolicyFormState {
  name: string;
  description: string;
  allowed_actions: string[];
  max_messages: number;
  max_duration_seconds: number;
  requires_human_approval: boolean;
  alert_on_violations: boolean;
}

export interface PolicyEditorProps {
  policies: PolicyData[];
  selectedPolicy: PolicyData | null;
  loading?: boolean;
  formData: PolicyFormState;
  availableActions: { value: string; label: string; description: string }[];
  onSelectPolicy: (policyName: string) => void;
  onToggleAction: (action: string) => void;
  onFormChange: (patch: Partial<PolicyFormState>) => void;
  onResetForm: () => void;
  onCreatePolicy?: () => void;
}

export const PolicyEditor: React.FC<PolicyEditorProps> = ({
  policies,
  selectedPolicy,
  loading,
  formData,
  availableActions,
  onSelectPolicy,
  onToggleAction,
  onFormChange,
  onResetForm,
  onCreatePolicy,
}) => {
  if (loading) {
    return <div className="policy-editor loading">Loading policies...</div>;
  }

  return (
    <div className="policy-editor">
      <div className="editor-layout">
        <div className="policy-list-panel">
          <h2>📋 Available Policies</h2>
          <div className="policy-list">
            {policies.map((policy) => (
              <div
                key={policy.name}
                className={`policy-card ${selectedPolicy?.name === policy.name ? "selected" : ""}`}
                onClick={() => onSelectPolicy(policy.name)}
              >
                <div className="policy-header">
                  <h3>{policy.name}</h3>
                  <span className={`policy-type type-${policy.type}`}>{policy.type}</span>
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

        <div className="policy-details-panel">
          {selectedPolicy ? (
            <div className="policy-details">
              <div className="details-header">
                <h2>{selectedPolicy.name}</h2>
                <span className={`policy-type type-${selectedPolicy.type}`}>{selectedPolicy.type}</span>
              </div>

              <p className="policy-description">{selectedPolicy.description}</p>

              <div className="details-section">
                <h3>🎯 Allowed Actions</h3>
                <div className="action-grid">
                  {selectedPolicy.allowed_actions?.map((action) => {
                    const actionInfo = availableActions.find((a) => a.value === action);
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
                    <span>{selectedPolicy.requires_human_approval ? "✅ Required" : "❌ Not Required"}</span>
                  </div>
                  <div className="limit-item">
                    <strong>Alert on Violations:</strong>
                    <span>{selectedPolicy.alert_on_violations ? "✅ Yes" : "❌ No"}</span>
                  </div>
                </div>
              </div>

              {selectedPolicy.type === "conditional" && selectedPolicy.conditions && (
                <div className="details-section">
                  <h3>🔀 Conditions</h3>
                  <div className="conditions-list">
                    {selectedPolicy.conditions.map((cond, idx) => (
                      <div key={idx} className="condition-item">
                        <div className="condition-type">{cond.type}</div>
                        <div className="condition-operator">{cond.operator}</div>
                        <div className="condition-value">{JSON.stringify(cond.value)}</div>
                      </div>
                    ))}
                  </div>
                  {selectedPolicy.fallback_policy && (
                    <div className="fallback-info">
                      <strong>Fallback:</strong> {selectedPolicy.fallback_policy}
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

        <div className="policy-create-panel">
          <h2>➕ Create New Policy</h2>

          <div className="form-group">
            <label>Policy Name</label>
            <input
              type="text"
              placeholder="e.g., restricted_weekend"
              value={formData.name}
              onChange={(e) => onFormChange({ name: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              placeholder="Describe when and how this policy should be used..."
              value={formData.description}
              onChange={(e) => onFormChange({ description: e.target.value })}
              rows={3}
            />
          </div>

          <div className="form-group">
            <label>Allowed Actions ({formData.allowed_actions.length} selected)</label>
            <div className="action-selector">
              {availableActions.map((action) => (
                <label key={action.value} className="action-checkbox">
                  <input
                    type="checkbox"
                    checked={formData.allowed_actions.includes(action.value)}
                    onChange={() => onToggleAction(action.value)}
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
                onChange={(e) => onFormChange({ max_messages: parseInt(e.target.value, 10) || 0 })}
              />
            </div>

            <div className="form-group">
              <label>Max Duration (seconds)</label>
              <input
                type="number"
                min="1"
                value={formData.max_duration_seconds}
                onChange={(e) => onFormChange({ max_duration_seconds: parseInt(e.target.value, 10) || 0 })}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.requires_human_approval}
                onChange={(e) => onFormChange({ requires_human_approval: e.target.checked })}
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
                onChange={(e) => onFormChange({ alert_on_violations: e.target.checked })}
                aria-label="Alert on violations"
                title="Send alert when policy violations occur"
              />
              Alert on policy violations
            </label>
          </div>

          <div className="form-actions">
            <button className="btn-secondary" onClick={onResetForm}>
              Reset
            </button>
            <button
              className="btn-primary"
              disabled={!formData.name || formData.allowed_actions.length === 0}
              onClick={onCreatePolicy}
            >
              Create Policy
            </button>
          </div>

          <div className="creation-notice">
            <strong>ℹ️ Note:</strong> Custom policy creation requires backend support. Currently viewing pre-defined policies only.
          </div>
        </div>
      </div>
    </div>
  );
};
