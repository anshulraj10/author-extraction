import { useState } from "react";

type ExtractResult = {
  authors: string[];
};

const defaultLaunchState = {
  text: "",
  status: "idle",
  authors: [] as string[],
};

function App() {
  const [text, setText] = useState(defaultLaunchState.text);
  const [status, setStatus] = useState(defaultLaunchState.status);
  const [result, setResult] = useState<ExtractResult>({
    authors: defaultLaunchState.authors,
  });

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!text.trim()) {
      return;
    }

    setStatus("loading");
    try {
      const response = await fetch("/api/extract", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error("Failed to reach backend");
      }

      const data: ExtractResult = await response.json();
      setResult(data);
      setStatus("success");
    } catch (error) {
      console.error(error);
      setStatus("error");
    }
  };

  return (
    <div className="app-shell">
      <header>
        <h1>Author Extraction</h1>
        <p>Send sample text to the backend and get author suggestions.</p>
      </header>

      <form onSubmit={handleSubmit}>
        <label htmlFor="extract-text">Paste text to analyze</label>
        <textarea
          id="extract-text"
          rows={6}
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Once upon a time..."
        />

        <button type="submit" disabled={status === "loading"}>
          {status === "loading" ? "Analyzing…" : "Extract authors"}
        </button>

        {status === "success" && (
          <section>
            <h2>Detected authors</h2>
            {result.authors.length ? (
              <ul>
                {result.authors.map((author) => (
                  <li key={author}>{author}</li>
                ))}
              </ul>
            ) : (
              <p>No authors detected yet.</p>
            )}
          </section>
        )}

        {status === "error" && (
          <p className="error-message">Unable to contact the backend.</p>
        )}
      </form>
    </div>
  );
}

export default App;
