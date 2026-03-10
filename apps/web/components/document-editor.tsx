"use client";

import { useState, useCallback } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { patchDocument, type Document, type DocumentChange } from "@/lib/documents";
import { contentToReplaceChanges } from "@/lib/diff-content";
import { Button } from "@/components/ui/button";

export type DocumentEditorProps = {
  /** Initial document (id, version, title, content). Editor keeps its own state after load. */
  document: Document;
  className?: string;
  /** Called after a successful save with the updated document. */
  onSave?: (doc: Document) => void;
};

/**
 * Editable document editor. Tracks content vs last-saved, derives replace changes on save,
 * and shows success or conflict toasts.
 */
export function DocumentEditor({
  document: initialDoc,
  className,
  onSave,
}: DocumentEditorProps) {
  const [title, setTitle] = useState(initialDoc.title);
  const [lastSavedTitle, setLastSavedTitle] = useState(initialDoc.title);
  const [content, setContent] = useState(initialDoc.content);
  const [lastSavedContent, setLastSavedContent] = useState(initialDoc.content);
  const [version, setVersion] = useState(initialDoc.version);
  const [saving, setSaving] = useState(false);

  const contentChanged = content !== lastSavedContent;
  const titleChanged = title !== lastSavedTitle;
  const hasUnsavedChanges = contentChanged || titleChanged;

  const handleSave = useCallback(async () => {
    if (!hasUnsavedChanges) {
      toast.info("No changes to save.");
      return;
    }

    const changes: DocumentChange[] = contentToReplaceChanges(lastSavedContent, content);
    const sendTitle = titleChanged ? title : undefined;

    if (changes.length === 0 && sendTitle === undefined) {
      setLastSavedContent(content);
      setLastSavedTitle(title);
      toast.success("Saved.");
      return;
    }

    setSaving(true);
    try {
      const updated = await patchDocument(initialDoc.id, version, changes, {
        title: sendTitle,
      });
      setLastSavedContent(updated.content);
      setLastSavedTitle(updated.title);
      setTitle(updated.title);
      setVersion(updated.version);
      setContent(updated.content);
      toast.success("Saved.");
      onSave?.(updated);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      const is412 =
        message.includes("412") ||
        message.toLowerCase().includes("precondition");
      if (is412) {
        toast.error(
          "Conflict: document was changed elsewhere. Refetch to get the latest version."
        );
      } else {
        toast.error(message || "Save failed.");
      }
    } finally {
      setSaving(false);
    }
  }, [
    initialDoc.id,
    version,
    content,
    lastSavedContent,
    title,
    lastSavedTitle,
    titleChanged,
    hasUnsavedChanges,
    onSave,
  ]);

  return (
    <div className={cn("flex flex-col gap-3", className)}>
      <label htmlFor="doc-title" className="sr-only">
        Document title
      </label>
      <input
        id="doc-title"
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="text-lg font-semibold text-foreground bg-transparent border-b border-border focus:outline-none focus:ring-0 focus:border-ring pb-1"
        placeholder="Untitled"
      />
      <textarea
        className="min-h-[32rem] w-full rounded-md border border-border bg-background px-3 py-3 text-sm text-foreground whitespace-pre-wrap resize-y focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="No content."
        aria-label="Document content"
      />
      <div className="flex items-center gap-2">
        <Button
          onClick={handleSave}
          disabled={saving || !hasUnsavedChanges}
          size="sm"
        >
          {saving ? "Saving…" : "Save"}
        </Button>
        {hasUnsavedChanges && (
          <span className="text-xs text-muted-foreground">
            Unsaved changes
          </span>
        )}
      </div>
    </div>
  );
}
