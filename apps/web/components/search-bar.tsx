"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  listDocuments,
  searchDocuments,
  type DocumentSummary,
  type SearchMatch,
} from "@/lib/documents";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type SnippetResults = { kind: "snippets"; matches: SearchMatch[]; total: number };
type SummaryResults = { kind: "summaries"; summaries: DocumentSummary[] };
type ResultsState = SnippetResults | SummaryResults | null;

export type SearchBarProps = {
  className?: string;
};

/**
 * Global search bar: search across all documents (optionally scoped by metadata).
 * Shows snippet results or metadata-matched doc list; clicking a result opens the document editor.
 */
export function SearchBar({ className }: SearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [docType, setDocType] = useState("");
  const [partyId, setPartyId] = useState("");
  const [partyName, setPartyName] = useState("");
  const [results, setResults] = useState<ResultsState>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasFilters = Boolean(docType.trim() || partyId.trim() || partyName.trim());

  const runSearch = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      if (query.trim()) {
        if (hasFilters) {
          const summaries = await listDocuments({
            doc_type: docType.trim() || undefined,
            party_id: partyId.trim() || undefined,
            party_name: partyName.trim() || undefined,
          });
          const ids = summaries.map((s) => s.id);
          if (ids.length === 0) {
            setResults({ kind: "snippets", matches: [], total: 0 });
          } else {
            const res = await searchDocuments(query.trim(), {
              documentIds: ids,
              limit: 20,
              offset: 0,
            });
            setResults({ kind: "snippets", matches: res.matches, total: res.total });
          }
        } else {
          const res = await searchDocuments(query.trim(), {
            limit: 20,
            offset: 0,
          });
          setResults({ kind: "snippets", matches: res.matches, total: res.total });
        }
      } else if (hasFilters) {
        const summaries = await listDocuments({
          doc_type: docType.trim() || undefined,
          party_id: partyId.trim() || undefined,
          party_name: partyName.trim() || undefined,
        });
        setResults({ kind: "summaries", summaries });
      } else {
        setResults(null);
        setError("Enter a query or set filters.");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
      setResults(null);
    } finally {
      setLoading(false);
    }
  }, [query, docType, partyId, partyName, hasFilters]);

  return (
    <div className={cn("flex flex-col gap-4", className)}>
      <h2 className="text-sm font-semibold text-foreground">Search across documents</h2>

      <div className="flex flex-col gap-2">
        <label htmlFor="global-search-query" className="text-xs text-muted-foreground">
          Query
        </label>
        <Input
          id="global-search-query"
          type="text"
          placeholder="Search in all documents…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runSearch()}
        />
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="flex flex-col gap-1">
          <label htmlFor="sb-doc-type" className="text-xs text-muted-foreground">
            Doc type
          </label>
          <Input
            id="sb-doc-type"
            type="text"
            placeholder="e.g. template"
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="w-36"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="sb-party-id" className="text-xs text-muted-foreground">
            Party ID
          </label>
          <Input
            id="sb-party-id"
            type="text"
            placeholder="party_id"
            value={partyId}
            onChange={(e) => setPartyId(e.target.value)}
            className="w-36"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="sb-party-name" className="text-xs text-muted-foreground">
            Party name
          </label>
          <Input
            id="sb-party-name"
            type="text"
            placeholder="party_name"
            value={partyName}
            onChange={(e) => setPartyName(e.target.value)}
            className="w-36"
          />
        </div>
      </div>

      <Button onClick={runSearch} disabled={loading} size="sm" className="w-fit">
        {loading ? "Searching…" : "Search"}
      </Button>

      {error && (
        <p className="text-xs text-destructive" role="alert">
          {error}
        </p>
      )}

      {results && results.kind === "snippets" && (
        <div className="flex flex-col gap-2">
          <p className="text-xs text-muted-foreground">
            {results.total} match{results.total !== 1 ? "es" : ""} — click to open document
          </p>
          <ul className="flex flex-col gap-2 list-none p-0 m-0">
            {results.matches.map((m, i) => (
              <li key={`${m.documentId}-${m.startIndex}-${i}`}>
                <button
                  type="button"
                  onClick={() => router.push(`/document/${m.documentId}`)}
                  className={cn(
                    "w-full text-left rounded-md border border-border bg-muted/30 px-3 py-2 text-sm",
                    "hover:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 transition"
                  )}
                >
                  <p className="font-medium text-foreground truncate" title={m.title}>
                    {m.title}
                  </p>
                  <p className="text-muted-foreground whitespace-pre-wrap break-words mt-1 line-clamp-2">
                    {m.snippet}
                  </p>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {results && results.kind === "summaries" && (
        <div className="flex flex-col gap-2">
          <p className="text-xs text-muted-foreground">
            {results.summaries.length} document{results.summaries.length !== 1 ? "s" : ""} — click to open
          </p>
          <ul className="flex flex-col gap-2 list-none p-0 m-0">
            {results.summaries.map((s) => (
              <li key={s.id}>
                <button
                  type="button"
                  onClick={() => router.push(`/document/${s.id}`)}
                  className={cn(
                    "w-full text-left rounded-md border border-border bg-muted/30 px-3 py-2 text-sm",
                    "hover:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 transition"
                  )}
                >
                  <p className="font-medium text-foreground truncate" title={s.title}>
                    {s.title}
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5">{s.id}</p>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {results === null && !error && !loading && (
        <p className="text-xs text-muted-foreground">
          Enter a query to search by content, or set filters to list documents by metadata.
        </p>
      )}
    </div>
  );
}
