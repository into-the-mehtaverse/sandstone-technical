"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { DocumentEditor } from "@/components/document-editor";
import { SearchPanel } from "@/components/search-panel";
import { getDocument, type Document } from "@/lib/documents";

export default function DocumentPage() {
  const params = useParams();
  const router = useRouter();
  const id = typeof params.id === "string" ? params.id : null;
  const [doc, setDoc] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setLoading(false);
      setError("Missing document id");
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    getDocument(id)
      .then((d) => {
        if (!cancelled && d) setDoc(d);
        if (!cancelled && !d) setError("Document not found");
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (!id) {
    return (
      <div className="min-h-screen bg-background p-6">
        <p className="text-destructive">Missing document id.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-6">
        <p className="text-muted-foreground">Loading…</p>
      </div>
    );
  }

  if (error || !doc) {
    return (
      <div className="min-h-screen bg-background p-6">
        <p className="text-destructive" role="alert">{error ?? "Document not found."}</p>
        <button
          type="button"
          onClick={() => router.push("/")}
          className="mt-2 text-sm text-primary underline"
        >
          Back to templates
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="mx-auto max-w-6xl flex flex-col gap-4">
        <button
          type="button"
          onClick={() => router.push("/")}
          className="text-sm text-muted-foreground hover:text-foreground underline self-start"
        >
          ← Back to templates
        </button>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <DocumentEditor document={doc} />
          </div>
          <aside className="lg:border-l lg:border-border lg:pl-6 pt-4 lg:pt-0">
            <SearchPanel documentId={doc.id} />
          </aside>
        </div>
      </div>
    </div>
  );
}
