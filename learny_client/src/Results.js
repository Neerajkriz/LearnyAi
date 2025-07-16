import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import "./Results.css";

function Results() {
  const location = useLocation();
  const [data, setData] = useState({ images: [], texts: [] });
  const prompt = location.state?.prompt;

  useEffect(() => {
    if (prompt) {
      // Fetch generated data from the backend
      fetch("http://localhost:5000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      })
        .then((response) => response.json())
        .then((result) => setData(result))
        .catch((error) => console.error("Error fetching data:", error));
    }
  }, [prompt]);

  return (
    <div className="results">
      <h1>Generated Results</h1>
      <div className="results-container">
        <div className="texts">
          <h2>Generated Text</h2>
          {data.texts.map((text, index) => (
            <p key={index}>{text}</p>
          ))}
        </div>
        <div className="images">
          <h2>Generated Images</h2>
          {data.images.map((image, index) => (
            <img key={index} src={image} alt={`Generated ${index}`} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default Results;
