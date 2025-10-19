import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import {
  FileText,
  Upload,
  CheckCircle,
  Sparkles,
  Download,
  Settings,
  Sun,
  Moon,
  Wand2,
  FileCode,
  AlertCircle,
  Info,
  Loader2,
  Heart
} from 'lucide-react';
import './styles/App.css';
import { explainYAML, validateYAML, getLLMConfigs, getSettings, updateSetting } from './services/api';
import SettingsModal from './components/SettingsModal';
import WizardModal from './components/WizardModal';

function App() {
  const [yamlContent, setYamlContent] = useState('');
  const [activeTab, setActiveTab] = useState('summary');
  const [theme, setTheme] = useState('light');
  const [loading, setLoading] = useState(false);
  const [explanationData, setExplanationData] = useState(null);
  const [validationData, setValidationData] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [showWizard, setShowWizard] = useState(false);
  const [hasLLM, setHasLLM] = useState(false);

  // Load theme and settings on mount
  useEffect(() => {
    loadSettings();
    checkLLMAvailability();
  }, []);

  // Apply theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const loadSettings = async () => {
    try {
      const settings = await getSettings();
      if (settings.theme) {
        setTheme(settings.theme);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const checkLLMAvailability = async () => {
    try {
      const configs = await getLLMConfigs();
      setHasLLM(configs.some(c => c.is_active));
    } catch (error) {
      console.error('Failed to check LLM:', error);
    }
  };

  const toggleTheme = async () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    try {
      await updateSetting('theme', newTheme);
    } catch (error) {
      console.error('Failed to save theme:', error);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setYamlContent(e.target.result);
      };
      reader.readAsText(file);
    }
  };

  const handleValidate = async () => {
    if (!yamlContent.trim()) {
      alert('Please enter some YAML content first');
      return;
    }

    setLoading(true);
    try {
      const result = await validateYAML(yamlContent);
      setValidationData(result);
      setActiveTab('validation');
    } catch (error) {
      alert('Validation failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExplain = async (useLLM = false) => {
    if (!yamlContent.trim()) {
      alert('Please enter some YAML content first');
      return;
    }

    if (useLLM && !hasLLM) {
      alert('Please configure an LLM connection in settings first');
      return;
    }

    setLoading(true);
    try {
      const result = await explainYAML(yamlContent, useLLM);
      setExplanationData(result);
      setActiveTab('summary');
    } catch (error) {
      alert('Explanation failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    const blob = new Blob([yamlContent], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'kubernetes-manifest.yaml';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleWizardComplete = (yaml) => {
    setYamlContent(yaml);
    setShowWizard(false);
  };

  return (
    <div className="app">
      {/* Top Bar */}
      <div className="top-bar">
        <div className="logo">
          <FileCode size={28} />
          <span>K8s YAML Explainer</span>
        </div>

        <div className="toolbar">
          <button className="btn btn-secondary" onClick={() => setShowWizard(true)}>
            <Wand2 size={18} />
            New YAML
          </button>
          <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
            <Upload size={18} />
            Upload
            <input
              type="file"
              accept=".yaml,.yml"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </label>
          <button
            className="btn btn-primary"
            onClick={handleValidate}
            disabled={loading || !yamlContent.trim()}
          >
            {loading && activeTab === 'validation' ? (
              <Loader2 size={18} className="spinner" />
            ) : (
              <CheckCircle size={18} />
            )}
            Validate
          </button>
          <button
            className="btn btn-primary"
            onClick={() => handleExplain(false)}
            disabled={loading || !yamlContent.trim()}
          >
            {loading && !hasLLM ? (
              <Loader2 size={18} className="spinner" />
            ) : (
              <FileText size={18} />
            )}
            Explain
          </button>
          {hasLLM && (
            <button
              className="btn btn-success"
              onClick={() => handleExplain(true)}
              disabled={loading || !yamlContent.trim()}
            >
              {loading ? (
                <Loader2 size={18} className="spinner" />
              ) : (
                <Sparkles size={18} />
              )}
              Explain with AI
            </button>
          )}
          <button
            className="btn btn-secondary"
            onClick={handleExport}
            disabled={!yamlContent.trim()}
          >
            <Download size={18} />
            Export
          </button>
        </div>

        <div className="actions">
          <button className="btn btn-icon btn-secondary" onClick={toggleTheme}>
            {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          </button>
          <button
            className="btn btn-icon btn-secondary"
            onClick={() => setShowSettings(true)}
          >
            <Settings size={20} />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Editor Panel */}
        <div className="editor-panel">
          <div className="panel" style={{ flex: 1 }}>
            <div className="panel-header">
              <span>YAML Editor</span>
            </div>
            <div style={{ flex: 1 }}>
              <Editor
                height="100%"
                defaultLanguage="yaml"
                theme={theme === 'dark' ? 'vs-dark' : 'light'}
                value={yamlContent}
                onChange={(value) => setYamlContent(value || '')}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                }}
              />
            </div>
          </div>
        </div>

        {/* Explanation Panel */}
        <div className="explanation-panel">
          <div className="panel" style={{ flex: 1 }}>
            <div className="tabs">
              <button
                className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
                onClick={() => setActiveTab('summary')}
              >
                Summary
              </button>
              <button
                className={`tab ${activeTab === 'details' ? 'active' : ''}`}
                onClick={() => setActiveTab('details')}
              >
                Field Details
              </button>
              <button
                className={`tab ${activeTab === 'validation' ? 'active' : ''}`}
                onClick={() => setActiveTab('validation')}
              >
                Validation
              </button>
            </div>
            <div className="panel-content">
              {activeTab === 'summary' && <SummaryTab data={explanationData} />}
              {activeTab === 'details' && <DetailsTab data={explanationData} />}
              {activeTab === 'validation' && <ValidationTab data={validationData} />}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="footer">
        <div className="footer-text">
          Crafted with <Heart size={16} className="heart" fill="currentColor" /> by RoarinPenguin
        </div>
      </div>

      {/* Modals */}
      {showSettings && (
        <SettingsModal
          onClose={() => {
            setShowSettings(false);
            checkLLMAvailability();
          }}
        />
      )}
      {showWizard && (
        <WizardModal
          onClose={() => setShowWizard(false)}
          onComplete={handleWizardComplete}
        />
      )}
    </div>
  );
}

// Summary Tab Component
function SummaryTab({ data }) {
  if (!data) {
    return (
      <div className="empty-state">
        <FileText size={48} className="empty-state-icon" />
        <div className="empty-state-title">No Explanation Yet</div>
        <div className="empty-state-description">
          Upload or paste a Kubernetes YAML manifest and click "Explain" to see a detailed explanation.
        </div>
      </div>
    );
  }

  if (!data.success) {
    return (
      <div className="empty-state">
        <AlertCircle size={48} className="empty-state-icon" />
        <div className="empty-state-title">Explanation Failed</div>
        <div className="empty-state-description">{data.error || 'An error occurred'}</div>
      </div>
    );
  }

  return (
    <div className="summary-content">
      {data.llm_used && (
        <div className="status-badge success" style={{ marginBottom: '1rem' }}>
          <Sparkles size={14} />
          Enhanced with AI
        </div>
      )}
      <div dangerouslySetInnerHTML={{ __html: formatSummary(data.summary) }} />
      {data.resources && data.resources.length > 0 && (
        <>
          <h3>Resources</h3>
          <ul>
            {data.resources.map((resource, idx) => (
              <li key={idx}>
                <strong>{resource.kind}</strong>
                {resource.name && `: ${resource.name}`}
                {resource.namespace && ` (namespace: ${resource.namespace})`}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

// Details Tab Component
function DetailsTab({ data }) {
  if (!data || !data.explanations || data.explanations.length === 0) {
    return (
      <div className="empty-state">
        <Info size={48} className="empty-state-icon" />
        <div className="empty-state-title">No Details Available</div>
        <div className="empty-state-description">
          Run an explanation first to see field-by-field details.
        </div>
      </div>
    );
  }

  const regularExplanations = data.explanations.filter(exp => exp.path !== '_llm_summary');

  return (
    <div className="explanations-list">
      {regularExplanations.map((explanation, idx) => (
        <div key={idx} className="explanation-item">
          <div className="explanation-path">{explanation.path}</div>
          <div className="explanation-text">{explanation.explanation}</div>
          <div className="explanation-source">
            {explanation.source === 'llm' ? <Sparkles size={12} /> : <FileText size={12} />}
            {explanation.source === 'llm' ? 'AI-Enhanced' : 'Rule-based'}
          </div>
        </div>
      ))}
    </div>
  );
}

// Validation Tab Component
function ValidationTab({ data }) {
  if (!data) {
    return (
      <div className="empty-state">
        <CheckCircle size={48} className="empty-state-icon" />
        <div className="empty-state-title">No Validation Results</div>
        <div className="empty-state-description">
          Click "Validate" to check your YAML for errors and best practices.
        </div>
      </div>
    );
  }

  if (!data.success) {
    return (
      <div className="empty-state">
        <AlertCircle size={48} className="empty-state-icon" />
        <div className="empty-state-title">Validation Failed</div>
        <div className="empty-state-description">{data.error || 'An error occurred'}</div>
      </div>
    );
  }

  if (data.valid && data.issues.length === 0) {
    return (
      <div className="empty-state">
        <CheckCircle size={48} className="empty-state-icon" style={{ color: 'var(--success-green)' }} />
        <div className="empty-state-title">All Good!</div>
        <div className="empty-state-description">
          Your YAML manifest is valid with no issues detected.
        </div>
      </div>
    );
  }

  return (
    <div className="validation-issues">
      {data.issues.map((issue, idx) => (
        <div key={idx} className={`issue ${issue.severity}`}>
          <div className="issue-header">
            {issue.severity === 'error' && <AlertCircle size={18} />}
            {issue.severity === 'warning' && <Info size={18} />}
            {issue.severity === 'info' && <Info size={18} />}
            <span style={{ textTransform: 'capitalize' }}>{issue.severity}</span>
          </div>
          <div className="issue-path">{issue.path}</div>
          <div className="issue-message">{issue.message}</div>
          {issue.suggestion && (
            <div className="issue-suggestion">
              <strong>Suggestion:</strong> {issue.suggestion}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// Helper to format summary text
function formatSummary(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>');
}

export default App;
