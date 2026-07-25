import { EmptyPane } from "./EmptyPane";

const KEYWORDS = new Set([
  "def", "return", "if", "elif", "else", "for", "while", "in", "not", "and", "or", "is",
  "import", "from", "as", "class", "try", "except", "finally", "with", "raise",
  "pass", "break", "continue", "lambda", "yield", "global", "nonlocal", "async",
  "await", "del", "assert", "None", "True", "False", "self",
]);

interface Token {
  text: string;
  className: string;
}

/** Naive quote-tracking scan so a '#' inside a string isn't mistaken for a comment. */
function findCommentStart(line: string): number {
  let inSingle = false;
  let inDouble = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === "'" && !inDouble) inSingle = !inSingle;
    else if (ch === '"' && !inSingle) inDouble = !inDouble;
    else if (ch === "#" && !inSingle && !inDouble) return i;
  }
  return -1;
}

const TOKEN_PATTERN = /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\b\d+\.?\d*\b|\b[A-Za-z_][A-Za-z0-9_]*\b|\s+|.)/g;

/**
 * A deliberately simple regex-based tokenizer — not a real Python lexer
 * (triple-quoted strings and escaped edge cases will look slightly off) but
 * enough visual structure for generated scripts without pulling in Shiki or
 * Prism for what's meant to be a lightweight local tool.
 */
function tokenizeLine(line: string): Token[] {
  const commentIndex = findCommentStart(line);
  const codePart = commentIndex === -1 ? line : line.slice(0, commentIndex);
  const commentPart = commentIndex === -1 ? "" : line.slice(commentIndex);

  const tokens: Token[] = [];
  for (const match of codePart.matchAll(TOKEN_PATTERN)) {
    const text = match[0];
    let className = "text-text";
    if (text.startsWith('"') || text.startsWith("'")) className = "text-good";
    else if (/^\d/.test(text)) className = "text-executor";
    else if (KEYWORDS.has(text)) className = "text-reviewer";
    tokens.push({ text, className });
  }
  if (commentPart) tokens.push({ text: commentPart, className: "italic text-text-dim" });
  return tokens;
}

interface CodeViewProps {
  code: string;
  attempt: number;
}

export function CodeView({ code, attempt }: CodeViewProps) {
  if (!code) {
    return <EmptyPane message="Code will appear here once the Coder writes a first draft." />;
  }

  const lines = code.split("\n");

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-line px-4 py-2 text-[11px] font-medium uppercase tracking-wide text-text-dim">
        solution.py · attempt {attempt}
      </div>
      <div className="flex-1 overflow-auto">
        <pre className="min-w-full py-2 font-mono text-[13px] leading-6">
          <code>
            {lines.map((line, index) => (
              <div key={index} className="flex px-2 hover:bg-surface-raised/60">
                <span className="w-9 shrink-0 select-none pr-3 text-right text-line">{index + 1}</span>
                <span className="whitespace-pre">
                  {tokenizeLine(line).map((token, tokenIndex) => (
                    <span key={tokenIndex} className={token.className}>
                      {token.text}
                    </span>
                  ))}
                </span>
              </div>
            ))}
          </code>
        </pre>
      </div>
    </div>
  );
}
