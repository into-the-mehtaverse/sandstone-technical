"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { listDocuments, createFromTemplate, type DocumentSummary } from "@/lib/documents";
import { TemplateList } from "@/components/template-list";

export default function Home() {
  const router = useRouter();
  const [templates, setTemplates] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creatingId, setCreatingId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    listDocuments({ doc_type: "template" })
      .then((list) => {
        if (!cancelled) setTemplates(list);
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load templates");
          setTemplates([]);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSelectTemplate(templateId: string) {
    setCreatingId(templateId);
    try {
      const doc = await createFromTemplate(templateId);
      router.push(`/document/${doc.id}`);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to create document";
      toast.error(message);
    } finally {
      setCreatingId(null);
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <main className="mx-auto max-w-4xl flex flex-col gap-6">
        <h1 className="text-2xl font-semibold text-foreground">Templates</h1>
        {loading && (
          <p className="text-muted-foreground text-sm">Loading templates…</p>
        )}
        {error && (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}
        {!loading && !error && (
          <TemplateList
            templates={templates}
            onSelectTemplate={handleSelectTemplate}
            disabled={creatingId !== null}
          />
        )}
        {creatingId && (
          <p className="text-sm text-muted-foreground">Creating document…</p>
        )}
      </main>
    </div>
  );
}
