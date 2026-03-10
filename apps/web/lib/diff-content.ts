import type { DocumentChange } from "./documents";

/**
 * Derive a single replace change from old vs new content using common prefix/suffix.
 * Returns one change covering the differing region, or empty array if identical.
 * Backend expects changes; apply in reverse order by range.start.
 */
export function contentToReplaceChanges(
  oldContent: string,
  newContent: string
): DocumentChange[] {
  if (oldContent === newContent) return [];

  let prefixLen = 0;
  const maxPrefix = Math.min(oldContent.length, newContent.length);
  while (
    prefixLen < maxPrefix &&
    oldContent[prefixLen] === newContent[prefixLen]
  ) {
    prefixLen++;
  }

  let suffixLen = 0;
  const oldRemain = oldContent.length - prefixLen;
  const newRemain = newContent.length - prefixLen;
  while (
    suffixLen < oldRemain &&
    suffixLen < newRemain &&
    oldContent[oldContent.length - 1 - suffixLen] ===
      newContent[newContent.length - 1 - suffixLen]
  ) {
    suffixLen++;
  }

  const start = prefixLen;
  const end = oldContent.length - suffixLen;
  const text = newContent.slice(prefixLen, newContent.length - suffixLen);

  return [{ operation: "replace", range: { start, end }, text }];
}
