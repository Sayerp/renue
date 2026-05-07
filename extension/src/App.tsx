import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    setStatusMessage(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setLoading(true);
    setError(null);
    setStatusMessage(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/extract", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data = await response.json();
      if (data.status === "queued") {
        setStatusMessage(data.message);
    } else {
        setStatusMessage("Task started successfully.");
    }

    } catch (err: any) {
      setError(err.message || "Something went wrong during extraction.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ width: '400px', minHeight: '550px', padding: '20px', fontFamily: 'sans-serif', boxSizing: 'border-box' }}>
      <h1>Renue Prototype</h1>
      <p>Upload a CE Certificate (PDF) to extract data.</p>
      
      <div style={{ marginBottom: '20px', padding: '20px', border: '2px dashed #ccc', borderRadius: '8px' }}>
        <input 
          type="file" 
          accept="application/pdf" 
          onChange={handleFileChange} 
        />
        {file && <p style={{ color: 'green', marginTop: '10px' }}>Selected: {file.name}</p>}
      </div>

      <button 
        onClick={handleUpload} 
        disabled={!file || loading}
        style={{ padding: '10px 20px', fontSize: '16px', cursor: loading ? 'not-allowed' : 'pointer' }}
      >
        {loading ? "Extracting Data with AI..." : "Process Certificate"}
      </button>

      {error && (
        <div style={{ color: 'red', marginTop: '20px', padding: '10px', background: '#fee' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {statusMessage && (
        <div style={{ marginTop: '20px', padding: '15px', background: '#e8f5e9', border: '1px solid #4caf50', borderRadius: '8px', color: '#2e7d32' }}>
            <h3 style={{ marginTop: 0 }}>Upload Successful!</h3>
            <p style={{ margin: 0 }}>{statusMessage}</p>
            </div>
        )}
    </div>
  )
}

export default App