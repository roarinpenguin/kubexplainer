import React, { useState } from 'react';
import { X, Wand2, ChevronRight, ChevronLeft } from 'lucide-react';
import { generateYAML } from '../services/api';

function WizardModal({ onClose, onComplete }) {
  const [step, setStep] = useState(1);
  const [resourceType, setResourceType] = useState('deployment');
  const [config, setConfig] = useState({
    name: '',
    image: '',
    replicas: 3,
    port: 80,
    targetPort: 80,
    serviceType: 'ClusterIP',
    host: '',
    path: '/',
    serviceName: '',
    app: '',
    data: {}
  });
  const [loading, setLoading] = useState(false);

  const resourceTypes = [
    { value: 'deployment', label: 'Deployment', description: 'Manage replicated pods' },
    { value: 'service', label: 'Service', description: 'Expose pods as a network service' },
    { value: 'ingress', label: 'Ingress', description: 'HTTP/HTTPS routing to services' },
    { value: 'configmap', label: 'ConfigMap', description: 'Store configuration data' }
  ];

  const handleNext = () => {
    if (step === 1 && resourceType) {
      setStep(2);
    }
  };

  const handleBack = () => {
    if (step === 2) {
      setStep(1);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      // Prepare config based on resource type
      let finalConfig = { ...config };
      
      if (resourceType === 'deployment') {
        finalConfig = {
          name: config.name,
          image: config.image,
          replicas: parseInt(config.replicas),
          port: parseInt(config.port)
        };
      } else if (resourceType === 'service') {
        finalConfig = {
          name: config.name,
          app: config.app || config.name,
          port: parseInt(config.port),
          targetPort: parseInt(config.targetPort),
          type: config.serviceType
        };
      } else if (resourceType === 'ingress') {
        finalConfig = {
          name: config.name,
          host: config.host,
          path: config.path,
          serviceName: config.serviceName,
          servicePort: parseInt(config.port)
        };
      } else if (resourceType === 'configmap') {
        finalConfig = {
          name: config.name,
          data: config.data
        };
      }

      const result = await generateYAML(resourceType, finalConfig);
      onComplete(result.yaml);
    } catch (error) {
      alert('Failed to generate YAML: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = (field, value) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  const isStepValid = () => {
    if (step === 1) {
      return resourceType !== '';
    }
    if (step === 2) {
      if (resourceType === 'deployment') {
        return config.name && config.image;
      }
      if (resourceType === 'service') {
        return config.name && config.port;
      }
      if (resourceType === 'ingress') {
        return config.name && config.host && config.serviceName;
      }
      if (resourceType === 'configmap') {
        return config.name;
      }
    }
    return false;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px' }}>
        <div className="modal-header">
          <div className="modal-title">
            <Wand2 size={24} />
            YAML Wizard
          </div>
          <button className="btn btn-icon btn-secondary" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {/* Progress Indicator */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: step >= 1 ? 'var(--primary-blue)' : 'var(--bg-secondary)',
              color: step >= 1 ? 'white' : 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 600
            }}>
              1
            </div>
            <div style={{ flex: 1, height: '2px', background: step >= 2 ? 'var(--primary-blue)' : 'var(--border-color)' }} />
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: step >= 2 ? 'var(--primary-blue)' : 'var(--bg-secondary)',
              color: step >= 2 ? 'white' : 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 600
            }}>
              2
            </div>
          </div>

          {/* Step 1: Choose Resource Type */}
          {step === 1 && (
            <div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                Choose Resource Type
              </h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                Select the type of Kubernetes resource you want to create
              </p>

              <div style={{ display: 'grid', gap: '1rem' }}>
                {resourceTypes.map((type) => (
                  <div
                    key={type.value}
                    className="glass-card"
                    onClick={() => setResourceType(type.value)}
                    style={{
                      cursor: 'pointer',
                      border: resourceType === type.value ? '2px solid var(--primary-blue)' : undefined,
                      background: resourceType === type.value ? 'var(--bg-glass)' : undefined
                    }}
                  >
                    <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                      {type.label}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      {type.description}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Configure Resource */}
          {step === 2 && (
            <div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                Configure {resourceTypes.find(t => t.value === resourceType)?.label}
              </h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                Fill in the required information
              </p>

              {resourceType === 'deployment' && (
                <>
                  <div className="form-group">
                    <label className="form-label">Deployment Name *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="my-app"
                      value={config.name}
                      onChange={(e) => updateConfig('name', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Container Image *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="nginx:latest"
                      value={config.image}
                      onChange={(e) => updateConfig('image', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Replicas</label>
                    <input
                      type="number"
                      className="form-input"
                      min="1"
                      value={config.replicas}
                      onChange={(e) => updateConfig('replicas', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Container Port</label>
                    <input
                      type="number"
                      className="form-input"
                      value={config.port}
                      onChange={(e) => updateConfig('port', e.target.value)}
                    />
                  </div>
                </>
              )}

              {resourceType === 'service' && (
                <>
                  <div className="form-group">
                    <label className="form-label">Service Name *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="my-service"
                      value={config.name}
                      onChange={(e) => updateConfig('name', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">App Label</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="app-name (selector)"
                      value={config.app}
                      onChange={(e) => updateConfig('app', e.target.value)}
                    />
                    <div className="form-helper">Selector to match pods</div>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Service Type</label>
                    <select
                      className="form-select"
                      value={config.serviceType}
                      onChange={(e) => updateConfig('serviceType', e.target.value)}
                    >
                      <option value="ClusterIP">ClusterIP</option>
                      <option value="NodePort">NodePort</option>
                      <option value="LoadBalancer">LoadBalancer</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Service Port *</label>
                    <input
                      type="number"
                      className="form-input"
                      value={config.port}
                      onChange={(e) => updateConfig('port', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Target Port</label>
                    <input
                      type="number"
                      className="form-input"
                      value={config.targetPort}
                      onChange={(e) => updateConfig('targetPort', e.target.value)}
                    />
                  </div>
                </>
              )}

              {resourceType === 'ingress' && (
                <>
                  <div className="form-group">
                    <label className="form-label">Ingress Name *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="my-ingress"
                      value={config.name}
                      onChange={(e) => updateConfig('name', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Host *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="example.com"
                      value={config.host}
                      onChange={(e) => updateConfig('host', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Path</label>
                    <input
                      type="text"
                      className="form-input"
                      value={config.path}
                      onChange={(e) => updateConfig('path', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Backend Service Name *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="my-service"
                      value={config.serviceName}
                      onChange={(e) => updateConfig('serviceName', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Backend Service Port</label>
                    <input
                      type="number"
                      className="form-input"
                      value={config.port}
                      onChange={(e) => updateConfig('port', e.target.value)}
                    />
                  </div>
                </>
              )}

              {resourceType === 'configmap' && (
                <>
                  <div className="form-group">
                    <label className="form-label">ConfigMap Name *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="my-config"
                      value={config.name}
                      onChange={(e) => updateConfig('name', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Configuration Data</label>
                    <textarea
                      className="form-textarea"
                      placeholder='{"key1": "value1", "key2": "value2"}'
                      value={JSON.stringify(config.data, null, 2)}
                      onChange={(e) => {
                        try {
                          const parsed = JSON.parse(e.target.value);
                          updateConfig('data', parsed);
                        } catch (err) {
                          // Invalid JSON, update anyway to allow editing
                          updateConfig('data', {});
                        }
                      }}
                    />
                    <div className="form-helper">Enter key-value pairs as JSON</div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        <div className="modal-footer">
          {step === 2 && (
            <button className="btn btn-secondary" onClick={handleBack}>
              <ChevronLeft size={18} />
              Back
            </button>
          )}
          {step === 1 && (
            <button
              className="btn btn-primary"
              onClick={handleNext}
              disabled={!isStepValid()}
            >
              Next
              <ChevronRight size={18} />
            </button>
          )}
          {step === 2 && (
            <button
              className="btn btn-success"
              onClick={handleGenerate}
              disabled={!isStepValid() || loading}
            >
              {loading ? 'Generating...' : 'Generate YAML'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default WizardModal;
