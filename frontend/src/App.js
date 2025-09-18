// frontend/src/App.js

import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [status, setStatus] = useState('Ready');

  const handleUpload = async () => {
    if (!file) return alert("Please select a file!");
    setStatus("Uploading...");

    const formData = new FormData();
    formData.append("document", file);

    try {
      // TODO: Later connect to Azure Function or direct upload
      alert("In real app, this uploads to Azure Blob via API.");
      setStatus("Uploaded! (Simulated)");
    } catch (err) {
      setStatus("Upload failed: " + err.message);
    }
  };

  const handleAsk = async () => {
    if (!question) return alert("Ask a question!");
    setStatus("Thinking...");

    try {
      // TODO: Later connect to Azure Function
      setAnswer("This is a simulated answer. In real app, Azure ML + Gemini will answer based on your document.");
      setStatus("Answer ready!");
    } catch (err) {
      setStatus("Error: " + err.message);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <h1>📚 Azure ML RAG Q&A System</h1>
      
      <div>
        <h3>1. Upload Document (.txt)</h3>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} accept=".txt" />
        <button onClick={handleUpload} style={{ marginLeft: "1rem" }}>Upload & Index</button>
        <p><i>After upload, Azure ML will process it (we’ll set this up next).</i></p>
      </div>

      <div style={{ marginTop: "2rem" }}>
        <h3>2. Ask a Question</h3>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="E.g., What is machine learning?"
          style={{ width: "100%", padding: "0.5rem", marginBottom: "0.5rem" }}
        />
        <button onClick={handleAsk} style={{ width: "100%" }}>Ask AI</button>
      </div>

      {status && <p style={{ color: "#555" }}><strong>Status:</strong> {status}</p>}
      {answer && (
        <div style={{ marginTop: "2rem", padding: "1rem", background: "#f9f9f9", borderLeft: "4px solid #0078d4" }}>
          <h4>💡 Answer:</h4>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default App;
