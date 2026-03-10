"use client";

import { useState } from "react";
import { DocumentEditor } from "@/components/document-editor";
import { Button } from "@/components/ui/button";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** List endpoint returns summaries (no content). */
type DocumentSummary = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  version: number;
  party_id: string | null;
  party_name: string | null;
  doc_type: string | null;
};

/** Single-doc endpoint returns full document (with content). */
type DocumentResponse = DocumentSummary & { content: string };

export default function Home() {
  const [doc, setDoc] = useState<DocumentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadDocument() {
    setLoading(true);
    setError(null);
    try {
      // 1) List loan agreements via metadata filter
      const listRes = await fetch(
        `${API_BASE}/documents?doc_type=loan_agreement`
      );
      if (!listRes.ok) {
        setError(listRes.status === 404 ? "No documents found." : `Error ${listRes.status}`);
        setDoc(null);
        return;
      }
      const summaries: DocumentSummary[] = await listRes.json();
      const first = summaries[0];
      if (!first) {
        setError("No loan agreements found.");
        setDoc(null);
        return;
      }
      // 2) Fetch full document by id for content
      const docRes = await fetch(`${API_BASE}/documents/${first.id}`);
      if (!docRes.ok) {
        setError(docRes.status === 404 ? "Document not found." : `Error ${docRes.status}`);
        setDoc(null);
        return;
      }
      const data: DocumentResponse = await docRes.json();
      setDoc(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch document.");
      setDoc(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <main className="mx-auto max-w-3xl flex flex-col gap-6">
        <h1 className="text-2xl font-semibold text-foreground">Document viewer</h1>
        <Button onClick={loadDocument} disabled={loading}>
          {loading ? "Loading…" : "Load loan agreement (doc_type=loan_agreement)"}
        </Button>
        {error && (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}
        {doc && <DocumentEditor document={doc} />}
      </main>
    </div>
  );
}
