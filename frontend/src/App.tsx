import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import * as XLSX from "xlsx";

type Author = {
  name?: string;
  affiliation?: string | null;
  email?: string | null;
  website?: string | null;
};

type PaperEntry = {
  title?: string | null;
  year?: number | string | null;
  authors?: Author[] | null;
  journal?: string | null;
  notes?: string | null;
};

type AuthorRow = {
  title: string;
  year: string;
  author: string;
  affiliation: string;
  email: string;
  website: string;
  journal: string;
  notes: string;
};

type ColumnKey = keyof AuthorRow;

type HealthService = {
  name: string;
  connected: boolean;
  message: string;
};

type HealthPayload = {
  timestamp: string;
  services: HealthService[];
};

const MODEL_FALLBACK = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-pro-preview"];
const DEFAULT_FALLBACK_MODEL = MODEL_FALLBACK[1];

const RESULT_COLUMNS: { label: string; key: ColumnKey }[] = [
  { label: "Title", key: "title" },
  { label: "Year", key: "year" },
  { label: "Author", key: "author" },
  { label: "Affiliation", key: "affiliation" },
  { label: "Email", key: "email" },
  { label: "Website", key: "website" },
  { label: "Journal", key: "journal" },
  { label: "Notes", key: "notes" },
];

const COLUMN_LABELS = RESULT_COLUMNS.map((col) => col.label);

const toCsv = (rows: AuthorRow[]) => {
  const headers = COLUMN_LABELS.join(",");
  const safeValue = (value: string) =>
    `"${value.replace(/"/g, '""').replace(/\n/g, " ")}"`;

  const lines = rows.map((row) =>
    RESULT_COLUMNS.map((column) => safeValue(row[column.key])).join(","),
  );
  return [headers, ...lines].join("\n");
};

const downloadFile = (content: string, mimeType: string, filename: string) => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
};

const exportExcel = (rows: AuthorRow[]) => {
  const payload = rows.map((row) => {
    const ordered: Record<string, string> = {};
    RESULT_COLUMNS.forEach((column) => {
      ordered[column.label] = row[column.key];
    });
    return ordered;
  });

  const worksheet = XLSX.utils.json_to_sheet(payload, { header: COLUMN_LABELS });
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Authors");
  XLSX.writeFile(workbook, "authors.xlsx");
};

const flattenAuthors = (entries: PaperEntry[]): AuthorRow[] => {
  const rows: AuthorRow[] = [];

  entries.forEach((entry) => {
    const commonData = {
      title: entry.title ?? "",
      year: entry.year ? String(entry.year) : "",
      journal: entry.journal ?? "",
      notes: entry.notes ?? "",
    };

    (entry.authors ?? []).forEach((author) => {
      rows.push({
        ...commonData,
        author: author.name ?? "",
        affiliation: author.affiliation ?? "",
        email: author.email ?? "",
        website: author.website ?? "",
      });
    });
  });

  return rows;
};

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [uploading, setUploading] = useState(false);
  const [rows, setRows] = useState<AuthorRow[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [healthData, setHealthData] = useState<HealthPayload | null>(null);
  const [healthError, setHealthError] = useState("");
  const [healthLoading, setHealthLoading] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [modelOptions, setModelOptions] = useState<string[]>(MODEL_FALLBACK);
  const [selectedModel, setSelectedModel] = useState<string>(DEFAULT_FALLBACK_MODEL);
  const [modelError, setModelError] = useState("");

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setRows([]);
    setStatusMessage("");
    const file = event.target.files?.[0];
    if (!file) {
      setSelectedFile(null);
      setFileError("");
      return;
    }

    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setSelectedFile(null);
      setFileError("Please upload a PDF file.");
      return;
    }

    setFileError("");
    setSelectedFile(file);
  };

  const handleModelChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setSelectedModel(event.target.value);
  };

  const parseJson = (payload: string): unknown => {
    if (!payload) {
      return null;
    }

    try {
      return JSON.parse(payload);
    } catch {
      return payload;
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatusMessage("");
    if (!selectedFile) {
      setFileError("Choose a PDF before submitting.");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("file", selectedFile, selectedFile.name);
    formData.append("model_id", selectedModel || DEFAULT_FALLBACK_MODEL);

    try {
      const response = await fetch("/process-pdf", {
        method: "POST",
        body: formData,
      });

      const textBody = await response.text();
      const parsedPayload = parseJson(textBody);

      if (!response.ok) {
        const detail =
          typeof parsedPayload === "object" && parsedPayload
            ? (parsedPayload as { detail?: string }).detail || String(parsedPayload)
            : textBody || "Failed to process PDF.";
        throw new Error(detail);
      }

      if (!Array.isArray(parsedPayload)) {
        throw new Error("Unexpected response format from the backend.");
      }

      const papers = parsedPayload as PaperEntry[];
      const flattened = flattenAuthors(papers);
      setRows(flattened);
      setStatusMessage(
        flattened.length
          ? `Found ${flattened.length} author records.`
          : "No authors found in the uploaded PDF.",
      );
    } catch (error) {
      setStatusMessage(
        error instanceof Error ? error.message : "Unable to reach the server.",
      );
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    if (!uploading) {
      setElapsedSeconds(0);
      return;
    }

    const interval = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  }, [uploading]);

  useEffect(() => {
    let isMounted = true;
    setModelError("");

    fetch("/models")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Unable to fetch model list.");
        }
        return response.json();
      })
      .then((data: { models?: string[]; default?: string }) => {
        if (!isMounted) {
          return;
        }

        if (Array.isArray(data.models) && data.models.length) {
          setModelOptions(data.models);
          setSelectedModel(data.default ?? data.models[0]);
          setModelError("");
        } else {
          setModelError("Using default models.");
        }
      })
      .catch((error) => {
        if (!isMounted) {
          return;
        }

        setModelError(error instanceof Error ? error.message : "Model loading failed.");
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const openHealth = async () => {
    setModalOpen(true);
    setHealthLoading(true);
    setHealthError("");
    try {
      const response = await fetch("/health");
      if (!response.ok) {
        throw new Error("Health endpoint unavailable.");
      }
      const data: HealthPayload = await response.json();
      setHealthData(data);
    } catch (error) {
      setHealthData(null);
      setHealthError(error instanceof Error ? error.message : "Unknown error");
    } finally {
      setHealthLoading(false);
    }
  };

  return (
    <div className="page-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">Author Extraction</p>
          <h3>Upload a paper to inspect its contributors</h3>
          <p>
            Drop a PDF and process its references. The table below lists every
            author found in the references!
          </p>
        </div>
        <button type="button" className="ghost-button" onClick={openHealth}>
          Test Connection
        </button>
      </header>

      <section className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <label htmlFor="pdf-upload">PDF file</label>
            <input
              id="pdf-upload"
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
            />
          </div>
          <div className="form-row">
            <label htmlFor="model-select">Model</label>
            <select
              id="model-select"
              value={selectedModel}
              onChange={handleModelChange}
            >
              {modelOptions.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
            {modelError && <p className="field-error">{modelError}</p>}
          </div>
          {fileError && <p className="field-error">{fileError}</p>}
          <button type="submit" className="primary-button" disabled={uploading}>
            {uploading ? "Processing…" : "Upload and analyze"}
          </button>
          {statusMessage && (
            <p className="status-message" aria-live="polite">
              {statusMessage}
            </p>
          )}
          {uploading && (
            <p className="status-message" aria-live="polite">
              Processing time: {elapsedSeconds}s
            </p>
          )}
        </form>
      </section>

      {rows.length > 0 && (
        <section className="results-card">
          <header className="results-header">
            <div>
              <h2>Author results</h2>
              <p>Each row is one author discovered in the document.</p>
            </div>
            <div className="export-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() =>
                  downloadFile(toCsv(rows), "text/csv;charset=utf-8", "authors.csv")
                }
              >
                Export CSV
              </button>
              <button
                type="button"
                className="secondary-button"
                onClick={() => exportExcel(rows)}
              >
                Export Excel
              </button>
            </div>
          </header>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  {RESULT_COLUMNS.map((column) => (
                    <th key={column.key}>{column.label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => (
                  <tr key={`${row.author}-${index}`}>
                    {RESULT_COLUMNS.map((column) => (
                      <td key={column.key}>{row[column.key]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {modalOpen && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="modal modal-wide">
            <header>
            <h2>Health check</h2>
            <button
              type="button"
              aria-label="Close health modal"
              className="ghost-button"
              onClick={() => setModalOpen(false)}
            >
              ✕
            </button>
          </header>
            {healthLoading ? (
              <p>Loading status…</p>
            ) : healthError ? (
              <p className="field-error">{healthError}</p>
            ) : healthData ? (
              <>
                <p className="health-timestamp">Snapshot: {healthData.timestamp}</p>
                <div className="health-services">
                  {healthData.services.map((service) => (
                    <div key={service.name} className="health-service">
                      <p className="service-name">{service.name}</p>
                      <p className={service.connected ? "service-status success" : "service-status error"}>
                        {service.connected ? "connected" : "offline"}
                      </p>
                      <p className="service-message">{service.message}</p>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p>No health data available.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
