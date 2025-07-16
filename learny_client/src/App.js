import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const navigate = useNavigate();

  const handleSubmit = () => {
    if (prompt.trim() === "") {
      alert("Please enter a prompt.");
      return;
    }
    // Navigate to the Results page with the prompt as state
    navigate("/results", { state: { prompt } });
  };

  return (
    <div className="app">
      <h1>Generate Images from Prompt</h1>
      <div className="input-container">
        <input
          type="text"
          placeholder="Enter your prompt here"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="text-input"
        />
        <button onClick={handleSubmit} className="generate-button">
          Generate
        </button>
      </div>
    </div>
  );
}

export default App;
