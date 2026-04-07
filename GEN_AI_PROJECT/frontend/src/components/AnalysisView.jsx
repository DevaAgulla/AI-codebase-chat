import { useState } from 'react';

const AnalysisView = ({ analysis, repoUrl, onGenerateReadme, generatingReadme, readme }) => {
  const [activeTab, setActiveTab] = useState('architecture');

  const tabs = [
    { id: 'architecture', label: 'Architecture' },
    { id: 'folder_structure', label: 'Folder Structure' },
    { id: 'api_flow', label: 'API Flow' },
    { id: 'db_models', label: 'Database/Models' },
  ];

  const renderContent = () => {
    const content = analysis[activeTab] || 'No content available for this section.';
    return (
      <div className="content-section">
        {content}
      </div>
    );
  };

  const handleCopyReadme = () => {
    if (readme) {
      navigator.clipboard.writeText(readme);
      alert('README copied to clipboard!');
    }
  };

  return (
    <div className="container">
      <h2>Analysis Results</h2>
      
      {analysis.total_files !== undefined && (
        <div className="stats">
          <div className="stat-item">
            <div className="stat-label">Total Files</div>
            <div className="stat-value">{analysis.total_files}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Total Characters</div>
            <div className="stat-value">{analysis.total_chars?.toLocaleString() || 0}</div>
          </div>
        </div>
      )}

      <div className="tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {renderContent()}
      </div>

      <div style={{ marginTop: '30px' }}>
        <button
          onClick={() => onGenerateReadme(repoUrl, analysis)}
          disabled={generatingReadme}
        >
          {generatingReadme ? 'Generating README...' : 'Generate README.md'}
        </button>
      </div>

      {readme && (
        <div className="readme-container">
          <h3>Generated README.md</h3>
          <div className="readme-content">{readme}</div>
          <button className="copy-button" onClick={handleCopyReadme}>
            Copy README to Clipboard
          </button>
        </div>
      )}
    </div>
  );
};

export default AnalysisView;
