import { useState, type FormEvent, type KeyboardEvent } from "react";

interface TaskInputProps {
  disabled: boolean;
  onSubmit: (task: string) => void;
}

const PLACEHOLDER =
  'Describe what to build… e.g. "Write a function that merges two sorted lists, with tests."';

export function TaskInput({ disabled, onSubmit }: TaskInputProps) {
  const [value, setValue] = useState("");

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setValue("");
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    submit();
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-line p-3">
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder={PLACEHOLDER}
        rows={3}
        className="w-full resize-none rounded-md border border-line bg-surface-raised px-3 py-2 text-[13px] text-text placeholder:text-text-dim focus-visible:border-coder disabled:opacity-50"
      />
      <div className="mt-2 flex items-center justify-between">
        <span className="text-[11px] text-text-dim">⌘/Ctrl + Enter to build</span>
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="rounded-md bg-coder px-4 py-1.5 text-[13px] font-medium text-ink transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {disabled ? "Building…" : "Build it"}
        </button>
      </div>
    </form>
  );
}
