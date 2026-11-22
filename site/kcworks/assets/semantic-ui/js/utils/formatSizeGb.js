/*
 * This file is part of Knowledge Commons Works.
 * Copyright (C) 2026 Mesh Research.
 */

/**
 * Format a Data Hub `size_gb` value for display.
 *
 * Whole multiples of 1024 GB are shown as TB; otherwise as GB.
 *
 * @param {number|string|null|undefined} sizeGb
 * @returns {string|null} Formatted label, or `null` if the value is not usable.
 */
export function formatSizeGb(sizeGb) {
  const n = Number(sizeGb);
  if (!Number.isFinite(n) || n < 0) return null;
  if (n >= 1024 && n % 1024 === 0) {
    return `${n / 1024} TB`;
  }
  return `${n} GB`;
}
