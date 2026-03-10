"use client";

import { useState } from "react";
import { DocumentEditor } from "@/components/document-editor";
import { Button } from "@/components/ui/button";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const DOC_ID = "sandstone_dumbo_loan_agreement";

type DocumentResponse = {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  version: number;
  party_id: string | null;
  party_name: string | null;
  doc_type: string | null;
};

export default function Home() {
  const [doc, setDoc] = useState<DocumentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadDocument() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/documents/${DOC_ID}`);
      if (!res.ok) {
        setError(res.status === 404 ? "Document not found." : `Error ${res.status}`);
        setDoc(null);
        return;
      }
      const data: DocumentResponse = await res.json();
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
          {loading ? "Loading…" : "Load Sandstone Dumbo Loan Agreement"}
        </Button>
        {error && (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}
        {doc && <DocumentEditor title={doc.title} content={doc.content} />}
      </main>
    </div>
  );
}
