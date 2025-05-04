import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  useEffect(() => {
    document.title = "Teacher's Assistant - AI Powered Suggestions";
  }, []);
  const [formData, setFormData] = useState({
    numStudents: '',
    level: 'beginner',
    learningStyle: 'audio',
    subject: '',
    customQuery: ''
  });
  const [suggestion, setSuggestion] = useState('');
  const [loading, setLoading] = useState(false);

  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuggestion('');

    try {
      console.log('Sending request with data:', formData);
      const response = await fetch('http://localhost:5000/api/get-teaching-suggestion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (data.success) {
        setSuggestion(data.suggestion.choices[0].message.content);
      } else {
        setError(data.error || 'Failed to get suggestion');
      }
    } catch (error) {
      console.error('Error:', error);
      if (!navigator.onLine) {
        setError('You are offline. Please check your internet connection.');
      } else if (error.message.includes('Failed to fetch')) {
        setError('Cannot connect to the server. Please make sure the backend server is running.');
      } else if (error.message.includes('getaddrinfo failed')) {
        setError('Cannot reach the AI service. Please check your internet connection.');
      } else {
        setError('Network error: ' + (error.message || 'Failed to connect to server'));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="App">
      <div className="container">
        <div className="app-header">
          <h1>Teacher's Assistant</h1>
          <p className="subtitle">Get AI-powered suggestions to enhance your teaching methodology</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Number of Students:</label>
            <input
              type="number"
              name="numStudents"
              value={formData.numStudents}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Student Level:</label>
            <select name="level" value={formData.level} onChange={handleChange}>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          <div className="form-group">
            <label>Learning Style:</label>
            <select name="learningStyle" value={formData.learningStyle} onChange={handleChange}>
              <option value="audio">Audio</option>
              <option value="video">Video</option>
              <option value="textual">Textual</option>
              <option value="practical">Practical</option>
            </select>
          </div>

          <div className="form-group">
            <label>Subject:</label>
            <input
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Custom Query (Optional):</label>
            <textarea
              name="customQuery"
              value={formData.customQuery}
              onChange={handleChange}
              rows="3"
            ></textarea>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Getting Suggestions...' : 'Get Teaching Suggestions'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {suggestion && (
          <div className="suggestion-container">
            <h2>Teaching Suggestions:</h2>
            <div className="suggestion-content">
              {suggestion.split('\n').map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
