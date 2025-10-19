import React, { useState, useEffect } from 'react';
import { X, Settings, Sparkles, Trash2, CheckCircle, AlertCircle, Loader2, Plus } from 'lucide-react';
import {
  getLLMConfigs,
  createLLMConfig,
  deleteLLMConfig,
  activateLLMConfig,
  testLLMConnection
} from '../services/api';

function SettingsModal({ onClose }) {
  const [activeSection, setActiveSection] = useState('llm');
  const [llmConfigs, setLLMConfigs] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [testStatus, setTestStatus] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    endpoint: '',
    api_key: '',
    model_name: '',
    is_active: true
  });

  useEffect(() => {
    loadLLMConfigs();
  }, []);

  const loadLLMConfigs = async () => {
    try {
      const configs = await getLLMConfigs();
      setLLMConfigs(configs);
    } catch (error) {
      console.error('Failed to load LLM configs:', error);
    }
  };

  const handleTest = async () => {
    if (!formData.endpoint || !formData.api_key) {
      alert('Please provide endpoint and API key');
      return;
    }

    setLoading(true);
    setTestStatus(null);
    
    try {
      const result = await testLLMConnection(
        formData.endpoint,
        formData.api_key,
        formData.model_name || null
      );
      
      setTestStatus({
        success: result.success,
        message: result.message
      });
    } catch (error) {
      setTestStatus({
        success: false,
        message: error.message || 'Connection test failed'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!formData.name || !formData.endpoint || !formData.api_key) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      await createLLMConfig(formData);
      await loadLLMConfigs();
      setShowAddForm(false);
      setFormData({
        name: '',
        endpoint: '',
        api_key: '',
        model_name: '',
        is_active: true
      });
      setTestStatus(null);
    } catch (error) {
      alert('Failed to save configuration: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this LLM configuration?')) {
      return;
    }

    try {
      await deleteLLMConfig(id);
      await loadLLMConfigs();
    } catch (error) {
      alert('Failed to delete configuration: ' + error.message);
    }
  };

  const handleActivate = async (id) => {
    try {
      await activateLLMConfig(id);
      await loadLLMConfigs();
    } catch (error) {
      alert('Failed to activate configuration: ' + error.message);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setTestStatus(null);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <Settings size={24} />
            Settings
          </div>
          <button className="btn btn-icon btn-secondary" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <div className="tabs" style={{ marginBottom: '1.5rem' }}>
            <button
              className={`tab ${activeSection === 'llm' ? 'active' : ''}`}
              onClick={() => setActiveSection('llm')}
            >
              <Sparkles size={16} />
              LLM Configuration
            </button>
          </div>

          {activeSection === 'llm' && (
            <div>
              {llmConfigs.length > 0 && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ marginBottom: '1rem', fontSize: '1rem', fontWeight: 600 }}>
                    Configured LLM Connections
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {llmConfigs.map((config) => (
                      <div key={config.id} className="glass-card" style={{ padding: '1rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                          <div>
                            <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                              {config.name}
                            </div>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                              {config.endpoint}
                            </div>
                            {config.model_name && (
                              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                Model: {config.model_name}
                              </div>
                            )}
                          </div>
                          <div style={{ display: 'flex', gap: '0.5rem' }}>
                            {config.is_active ? (
                              <span className="status-badge success">Active</span>
                            ) : (
                              <button
                                className="btn btn-secondary"
                                style={{ padding: '0.375rem 0.75rem', fontSize: '0.8125rem' }}
                                onClick={() => handleActivate(config.id)}
                              >
                                Activate
                              </button>
                            )}
                            <button
                              className="btn btn-icon btn-secondary"
                              style={{ padding: '0.375rem' }}
                              onClick={() => handleDelete(config.id)}
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {!showAddForm && (
                <button
                  className="btn btn-primary"
                  onClick={() => setShowAddForm(true)}
                  style={{ width: '100%' }}
                >
                  <Plus size={18} />
                  Add New LLM Connection
                </button>
              )}

              {showAddForm && (
                <div className="glass-card">
                  <h3 style={{ marginBottom: '1.5rem', fontSize: '1rem', fontWeight: 600 }}>
                    Add LLM Connection
                  </h3>

                  <div className="form-group">
                    <label className="form-label">Provider Name *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g., OpenAI, Anthropic, Ollama"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">API Endpoint *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="https://api.openai.com/v1/chat/completions"
                      value={formData.endpoint}
                      onChange={(e) => handleInputChange('endpoint', e.target.value)}
                    />
                    <div className="form-helper">
                      Full URL including the chat/completions path
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">API Key *</label>
                    <input
                      type="password"
                      className="form-input"
                      placeholder="sk-..."
                      value={formData.api_key}
                      onChange={(e) => handleInputChange('api_key', e.target.value)}
                    />
                    <div className="form-helper">
                      Your API key will be encrypted and stored securely
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Model Name</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="gpt-3.5-turbo, claude-3-sonnet-20240229, etc."
                      value={formData.model_name}
                      onChange={(e) => handleInputChange('model_name', e.target.value)}
                    />
                    <div className="form-helper">
                      Optional: Specify the model to use
                    </div>
                  </div>

                  {testStatus && (
                    <div className={`status-badge ${testStatus.success ? 'success' : 'error'}`} style={{ marginBottom: '1rem' }}>
                      {testStatus.success ? (
                        <>
                          <CheckCircle size={16} />
                          {testStatus.message}
                        </>
                      ) : (
                        <>
                          <AlertCircle size={16} />
                          {testStatus.message}
                        </>
                      )}
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
                    <button
                      className="btn btn-secondary"
                      onClick={handleTest}
                      disabled={loading}
                      style={{ flex: 1 }}
                    >
                      {loading ? (
                        <Loader2 size={18} className="spinner" />
                      ) : (
                        <CheckCircle size={18} />
                      )}
                      Test Connection
                    </button>
                    <button
                      className="btn btn-primary"
                      onClick={handleSave}
                      disabled={loading}
                      style={{ flex: 1 }}
                    >
                      Save
                    </button>
                    <button
                      className="btn btn-secondary"
                      onClick={() => {
                        setShowAddForm(false);
                        setFormData({
                          name: '',
                          endpoint: '',
                          api_key: '',
                          model_name: '',
                          is_active: true
                        });
                        setTestStatus(null);
                      }}
                      disabled={loading}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-glass)', borderRadius: '8px', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                <strong>Tip:</strong> You can use this with OpenAI, Anthropic Claude, local Ollama instances, 
                or any OpenAI-compatible API endpoint.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SettingsModal;
