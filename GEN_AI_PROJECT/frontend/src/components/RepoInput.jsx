import { useState } from 'react';

const RepoInput = ({ onAnalyze, loading }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (repoUrl.trim()) {
      onAnalyze(repoUrl.trim(), branch.trim() || null);
    }
  };

  return (
    <div className="container">
      <h1>🤖 AI Codebase Explainer</h1>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Paste a GitHub repository URL to get AI-generated architecture, structure, API flow, and more.
      </p>
      
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label htmlFor="repo-url">GitHub Repository URL *</label>
          <input
            id="repo-url"
            type="url"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/owner/repo"
            required
            disabled={loading}
          />
        </div>
        
        <div className="input-group">
          <label htmlFor="branch">Branch (optional)</label>
          <input
            id="branch"
            type="text"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            placeholder="main, master, develop, etc. (default: main/master)"
            disabled={loading}
          />
        </div>
        
        <button type="submit" disabled={loading || !repoUrl.trim()}>
          {loading ? 'Analyzing...' : 'Analyze Repository'}
        </button>
      </form>
    </div>
  );
};

export default RepoInput;
