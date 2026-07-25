export function EmptyPane({ message }: { message: string }) {
  return (
    <div className="flex h-full items-center justify-center px-8 text-center text-sm text-text-dim">
      {message}
    </div>
  );
}
