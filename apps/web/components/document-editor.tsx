"use client";

import { cn } from "@/lib/utils";

type DocumentEditorProps = {
  /** Document body text to render */
  content: string;
  /** Optional document title shown above the content */
  title?: string;
  className?: string;
};

/**
 * Renders a document's content (and optional title).
 * Use this for read-only display; extend later for editing + PATCH.
 */
export function DocumentEditor({ content, title, className }: DocumentEditorProps) {
  return (
    <div className={cn("flex flex-col gap-2", className)}>
      {title != null && title !== "" && (
        <h1 className="text-lg font-semibold text-foreground">{title}</h1>
      )}
      <div
        className="min-h-[12rem] rounded-md border border-border bg-background px-3 py-3 text-sm text-foreground whitespace-pre-wrap"
        role="document"
      >
        {content || "No content."}
      </div>
    </div>
  );
}
