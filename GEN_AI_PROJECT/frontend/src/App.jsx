import { useState } from 'react';
import RepoInput from './components/RepoInput';
import AnalysisView from './components/AnalysisView';
import QuestionPanel from './components/QuestionPanel';
import { analyzeRepository, generateReadme, askQuestion } from './api/client';

function App() {
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [repoUrl, setRepoUrl] = useState(null);
  const [error, setError] = useState(null);
  const [generatingReadme, setGeneratingReadme] = useState(false);
  const [readme, setReadme] = useState(null);
  const [asking, setAsking] = useState(false);
  const [answer, setAnswer] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);

  const handleAnalyze = async (url, branch) => {
    setLoading(true);
    setError(null);
    setAnalysis(null);
    setReadme(null);
    setAnswer(null);
    setRepoUrl(url);

    try {
      const result = await analyzeRepository(url, branch);
      setAnalysis(result);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        err.message || 
        'Failed to analyze repository. Please check the URL and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReadme = async (url, analysisData) => {
    setGeneratingReadme(true);
    setError(null);
    setReadme(null);

    try {
      const result = await generateReadme(url, analysisData);
      setReadme(result.readme);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        err.message || 
        'Failed to generate README. Please try again.'
      );
    } finally {
      setGeneratingReadme(false);
    }
  };

  const handleAskQuestion = async (question, url, analysisData) => {
    setAsking(true);
    setError(null);
    setAnswer(null);
    setCurrentQuestion(question);

    try {
      const result = await askQuestion(question, url, analysisData);
      setAnswer(result.answer);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        err.message || 
        'Failed to get answer. Please try again.'
      );
    } finally {
      setAsking(false);
    }
  };

  return (
    <div>
      <RepoInput onAnalyze={handleAnalyze} loading={loading} />

      {error && (
        <div className="container">
          <div className="error">{error}</div>
        </div>
      )}

      {analysis && (
        <>
          <AnalysisView
            analysis={analysis}
            repoUrl={repoUrl}
            onGenerateReadme={handleGenerateReadme}
            generatingReadme={generatingReadme}
            readme={readme}
          />
          <QuestionPanel
            repoUrl={repoUrl}
            analysis={analysis}
            onAskQuestion={handleAskQuestion}
            asking={asking}
            answer={answer}
            question={currentQuestion}
          />
        </>
      )}
    </div>
  );
}

export default App;
