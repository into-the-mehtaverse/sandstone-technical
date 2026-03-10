"use client";

import { useState, useCallback } from "react";
import { cn } from "@/lib/utils";
import {
  listDocuments,
  searchDocuments,
  searchInDocument,
  type DocumentSummary,
  type SearchMatch,
} from "@/lib/documents";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export type SearchPanelProps = {
  /** When set, search runs only in this document (metadata filters hidden). */
  documentId?: string;
  className?: string;
};

type SnippetResults = { kind: "snippets"; matches: SearchMatch[]; total: number };
type SummaryResults = { kind: "summaries"; summaries: DocumentSummary[] };
type ResultsState = SnippetResults | SummaryResults | null;

export function SearchPanel({ documentId, className }: SearchPanelProps) {
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
        // Query search → snippets
        if (documentId) {
          const res = await searchInDocument(documentId, query.trim(), {
            limit: 20,
            offset: 0,
          });
          setResults({ kind: "snippets", matches: res.matches, total: res.total });
        } else if (hasFilters) {
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
      } else if (hasFilters && !documentId) {
        // No query but filters → doc summaries
        const summaries = await listDocuments({
          doc_type: docType.trim() || undefined,
          party_id: partyId.trim() || undefined,
          party_name: partyName.trim() || undefined,
        });
        setResults({ kind: "summaries", summaries });
      } else {
        setResults(null);
        setError(documentId ? "Enter a search query." : "Enter a query or set filters.");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
      setResults(null);
    } finally {
      setLoading(false);
    }
  }, [query, docType, partyId, partyName, documentId, hasFilters]);

  return (
    <div className={cn("flex flex-col gap-4", className)}>
      <h2 className="text-sm font-semibold text-foreground">Search</h2>

      <div className="flex flex-col gap-2">
        <label htmlFor="search-query" className="text-xs text-muted-foreground">
          Query
        </label>
        <Input
          id="search-query"
          type="text"
          placeholder={documentId ? "Search in current document" : "Search in documents…"}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runSearch()}
        />
      </div>

      {!documentId && (
        <>
          <div className="flex flex-col gap-2">
            <label htmlFor="filter-doc-type" className="text-xs text-muted-foreground">
              Doc type (e.g. template, loan_agreement)
            </label>
            <Input
              id="filter-doc-type"
              type="text"
              placeholder="doc_type"
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <label htmlFor="filter-party-id" className="text-xs text-muted-foreground">
              Party ID
            </label>
            <Input
              id="filter-party-id"
              type="text"
              placeholder="party_id"
              value={partyId}
              onChange={(e) => setPartyId(e.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <label htmlFor="filter-party-name" className="text-xs text-muted-foreground">
              Party name
            </label>
            <Input
              id="filter-party-name"
              type="text"
              placeholder="party_name"
              value={partyName}
              onChange={(e) => setPartyName(e.target.value)}
            />
          </div>
        </>
      )}

      <Button onClick={runSearch} disabled={loading} size="sm">
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
            {results.total} match{results.total !== 1 ? "es" : ""}
          </p>
          <ul className="flex flex-col gap-3 list-none p-0 m-0">
            {results.matches.map((m, i) => (
              <li
                key={`${m.documentId}-${m.startIndex}-${i}`}
                className="rounded-md border border-border bg-muted/30 px-3 py-2 text-sm"
              >
                <p className="font-medium text-foreground truncate" title={m.title}>
                  {m.title}
                </p>
                <p className="text-muted-foreground whitespace-pre-wrap break-words mt-1">
                  {m.snippet}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {results && results.kind === "summaries" && (
        <div className="flex flex-col gap-2">
          <p className="text-xs text-muted-foreground">
            {results.summaries.length} document{results.summaries.length !== 1 ? "s" : ""}
          </p>
          <ul className="flex flex-col gap-2 list-none p-0 m-0">
            {results.summaries.map((s) => (
              <li
                key={s.id}
                className="rounded-md border border-border bg-muted/30 px-3 py-2 text-sm"
              >
                <p className="font-medium text-foreground truncate" title={s.title}>
                  {s.title}
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">{s.id}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {results === null && !error && !loading && (
        <p className="text-xs text-muted-foreground">
          {documentId
            ? "Search within this document."
            : "Enter a query to search all documents, or set filters to list documents."}
        </p>
      )}
    </div>
  );
}
