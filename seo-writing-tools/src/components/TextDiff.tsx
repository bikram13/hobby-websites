import { h, Fragment } from "preact";
import { useState, useRef, useCallback } from "preact/hooks";
import { diffWords } from "diff";

type Change = { value: string; added?: boolean; removed?: boolean };

function computeDiff(original: string, revised: string): Change[] {
  return diffWords(original, revised);
}

function DiffOutput({ changes, view }: { changes: Change[]; view: "side" | "unified" }) {
  const added = changes.filter((c) => c.added).reduce((n, c) => n + c.value.split(/\s+/).filter(Boolean).length, 0);
  const removed = changes.filter((c) => c.removed).reduce((n, c) => n + c.value.split(/\s+/).filter(Boolean).length, 0);
  const unchanged = changes.filter((c) => !c.added && !c.removed).reduce((n, c) => n + c.value.split(/\s+/).filter(Boolean).length, 0);

  const renderInline = (filter?: "added" | "removed" | "all") =>
    changes
      .filter((c) => {
        if (filter === "added") return !c.removed;
        if (filter === "removed") return !c.added;
        return true;
      })
      .map((c, i) => {
        if (c.added) return <mark key={i} style={{ background: "#bbf7d0", borderRadius: "2px" }}>{c.value}</mark>;
        if (c.removed) return <del key={i} style={{ background: "#fecaca", borderRadius: "2px", textDecoration: "line-through" }}>{c.value}</del>;
        return <span key={i}>{c.value}</span>;
      });

  return (
    <div>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "0.75rem", fontSize: "0.85rem", flexWrap: "wrap" }}>
        <span style={{ color: "#16a34a", fontWeight: 600 }}>+{added} added</span>
        <span style={{ color: "#dc2626", fontWeight: 600 }}>−{removed} removed</span>
        <span style={{ color: "#6b7280" }}>{unchanged} unchanged</span>
      </div>
      {view === "side" ? (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
          <div style={{ background: "#fff7f7", border: "1px solid #fecaca", borderRadius: "0.5rem", padding: "0.75rem", lineHeight: 1.7, fontSize: "0.9rem", whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
            <div style={{ fontWeight: 600, marginBottom: "0.5rem", color: "#dc2626", fontSize: "0.75rem", textTransform: "uppercase" }}>Original</div>
            {renderInline("removed")}
          </div>
          <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "0.5rem", padding: "0.75rem", lineHeight: 1.7, fontSize: "0.9rem", whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
            <div style={{ fontWeight: 600, marginBottom: "0.5rem", color: "#16a34a", fontSize: "0.75rem", textTransform: "uppercase" }}>Revised</div>
            {renderInline("added")}
          </div>
        </div>
      ) : (
        <div style={{ background: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: "0.5rem", padding: "0.75rem", lineHeight: 1.7, fontSize: "0.9rem", whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
          {renderInline("all")}
        </div>
      )}
    </div>
  );
}

export default function TextDiff() {
  const [original, setOriginal] = useState("");
  const [revised, setRevised] = useState("");
  const [changes, setChanges] = useState<Change[] | null>(null);
  const [view, setView] = useState<"side" | "unified">("side");
  const [computing, setComputing] = useState(false);
  const workerRef = useRef<Worker | null>(null);
  const reqId = useRef(0);

  const runDiff = useCallback((orig: string, rev: string) => {
    if (!orig.trim() && !rev.trim()) { setChanges(null); return; }
    setComputing(true);
    const id = ++reqId.current;

    if (typeof Worker !== "undefined" && !workerRef.current) {
      try {
        workerRef.current = new Worker("/diff-worker.js");
        workerRef.current.onmessage = (e) => {
          if (e.data.id !== reqId.current) return;
          setChanges(e.data.error ? computeDiff(original, revised) : e.data.changes);
          setComputing(false);
        };
      } catch { workerRef.current = null; }
    }

    if (workerRef.current) {
      workerRef.current.postMessage({ original: orig, revised: rev, id });
    } else {
      setTimeout(() => {
        setChanges(computeDiff(orig, rev));
        setComputing(false);
      }, 0);
    }
  }, []);

  function handleOriginal(e: Event) {
    const v = (e.target as HTMLTextAreaElement).value;
    setOriginal(v);
    runDiff(v, revised);
  }

  function handleRevised(e: Event) {
    const v = (e.target as HTMLTextAreaElement).value;
    setRevised(v);
    runDiff(original, v);
  }

  const taStyle = { width: "100%", minHeight: "160px", padding: "0.6rem 0.75rem", border: "1px solid #d1d5db", borderRadius: "0.5rem", fontFamily: "inherit", fontSize: "0.9rem", lineHeight: 1.6, resize: "vertical" as const, boxSizing: "border-box" as const };

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
        <div>
          <label style={{ display: "block", fontWeight: 600, marginBottom: "0.35rem", fontSize: "0.85rem" }}>Original Text</label>
          <textarea style={taStyle} placeholder="Paste original text here…" onInput={handleOriginal} />
        </div>
        <div>
          <label style={{ display: "block", fontWeight: 600, marginBottom: "0.35rem", fontSize: "0.85rem" }}>New Text</label>
          <textarea style={taStyle} placeholder="Paste revised text here…" onInput={handleRevised} />
        </div>
      </div>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", alignItems: "center" }}>
        <span style={{ fontSize: "0.8rem", color: "#6b7280", marginRight: "0.25rem" }}>View:</span>
        {(["side", "unified"] as const).map((v) => (
          <button key={v} onClick={() => setView(v)} style={{ padding: "0.3rem 0.75rem", borderRadius: "999px", border: "1px solid", fontSize: "0.8rem", cursor: "pointer", background: view === v ? "#2563eb" : "#fff", color: view === v ? "#fff" : "#374151", borderColor: view === v ? "#2563eb" : "#d1d5db" }}>
            {v === "side" ? "Side-by-side" : "Unified"}
          </button>
        ))}
        {computing && <span style={{ fontSize: "0.8rem", color: "#6b7280" }}>Computing…</span>}
      </div>

      {changes ? (
        <DiffOutput changes={changes} view={view} />
      ) : (
        <div style={{ padding: "2rem", textAlign: "center", color: "#9ca3af", background: "#f9fafb", borderRadius: "0.75rem", border: "1px solid #e5e7eb" }}>
          Paste text in both boxes to see differences
        </div>
      )}
    </div>
  );
}
