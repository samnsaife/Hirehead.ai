"use client";
import { useState } from "react";

export default function Home() {
  const [resume, setResume] = useState("");
  const [result, setResult] = useState<any>(null);

  async function analyzeResume() {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_RESUME_API_URL}/analyze`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: resume }),
      }
    );

    const data = await res.json();
    setResult(data);
  }

  return (
    <main style={{ padding: 20 }}>
      <h1>Resume ATS Analyzer</h1>

      <textarea
        value={resume}
        onChange={(e) => setResume(e.target.value)}
        placeholder="Paste resume text here"
        style={{ width: "100%", height: "150px", marginTop: 12 }}
      />

      <button
        onClick={analyzeResume}
        style={{
          marginTop: 12,
          padding: "10px 20px",
          background: "black",
          color: "white",
          borderRadius: 8,
        }}
      >
        Analyze Resume
      </button>

      {result && (
        <pre
          style={{
            background: "#111",
            color: "#0f0",
            padding: 12,
            marginTop: 20,
          }}
        >
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </main>
  );
}
