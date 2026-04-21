import { clsx, type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}

export function formatDate(date: string | Date | null): string {
  if (!date) return '—';
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatScore(score: number | null): string {
  if (score === null) return '—';
  return score.toFixed(1);
}

export function getScoreColor(score: number | null): string {
  if (score === null) return 'text-[#94A3B8]';
  if (score >= 80) return 'text-[#166534]';
  if (score >= 60) return 'text-[#92400E]';
  return 'text-[#991B1B]';
}

export function getScoreBgColor(score: number | null): string {
  if (score === null) return 'bg-[#E2E8F0]';
  if (score >= 80) return 'bg-[#22C55E]';
  if (score >= 60) return 'bg-[#F59E0B]';
  return 'bg-[#EF4444]';
}