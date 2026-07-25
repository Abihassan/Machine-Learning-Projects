export function TableRowSkeleton() {
  return (
    <tr className="border-b border-line">
      {Array.from({ length: 5 }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-3 rounded bg-raised animate-pulse" style={{ width: `${50 + i * 8}%` }} />
        </td>
      ))}
    </tr>
  );
}

export function CardSkeleton() {
  return (
    <div className="rounded-lg border border-line bg-surface p-4 space-y-3">
      <div className="h-3 w-1/3 rounded bg-raised animate-pulse" />
      <div className="h-6 w-1/2 rounded bg-raised animate-pulse" />
    </div>
  );
}
