import { useState } from 'react';

const QuestionPanel = ({ repoUrl, analysis, onAskQuestion, asking, answer, question }) => {
  const [currentQuestion, setCurrentQuestion] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (currentQuestion.trim()) {
      onAskQuestion(currentQuestion.trim(), repoUrl, analysis);
      setCurrentQuestion('');
    }
  };

  const exampleQuestions = [
    'How does authentication work?',
    'What is the main entry point?',
    'How are API routes structured?',
    'What database is used?',
    'How is error handling implemented?',
  ];

  return (
    <div className="container question-section">
      <h2>Ask Questions</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Ask natural language questions about the codebase.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label htmlFor="question">Your Question</label>
          <textarea
            id="question"
            className="question-input"
            value={currentQuestion}
            onChange={(e) => setCurrentQuestion(e.target.value)}
            placeholder="e.g., How does authentication work in this codebase?"
            required
            disabled={asking}
          />
        </div>

        <button type="submit" disabled={asking || !currentQuestion.trim()}>
          {asking ? 'Asking...' : 'Ask Question'}
        </button>
      </form>

      <div style={{ marginTop: '20px' }}>
        <p style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
          Example questions:
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {exampleQuestions.map((q, idx) => (
            <button
              key={idx}
              className="secondary"
              style={{ fontSize: '12px', padding: '6px 12px', margin: 0 }}
              onClick={() => setCurrentQuestion(q)}
              disabled={asking}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {answer && (
        <div className="answer-section">
          <h3>Answer</h3>
          <div className="answer-content">{answer}</div>
        </div>
      )}
    </div>
  );
};

export default QuestionPanel;
