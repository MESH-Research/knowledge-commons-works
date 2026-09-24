#!/usr/bin/env node
/* eslint-disable */
/**
 * JS-side parity helper for the geopattern port.
 *
 * Reads one slug per line from stdin and writes a JSON object per line to
 * stdout describing what the JS Geopattern library produces. The Python
 * parity test compares each line against the port's output.
 *
 * Why stdin: many test slugs contain spaces, '+', '&', or non-ASCII chars;
 * passing those via argv is fragile across shells and on different
 * platforms. Stdin keeps each slug as a single newline-terminated record.
 *
 * Run manually:
 *   printf 'alpha\nmy-community\nhello world\n' | node dump_js.js
 *
 * Output JSON shape (one object per slug):
 *   {
 *     "slug":      <input slug as-is>,
 *     "encoded":   encodeURI(slug),
 *     "hash":      SHA1(encoded),                  // 40 hex chars
 *     "color":     pattern.color,                  // "#RRGGBB"
 *     "hexValSeq": [int, int, ...]                 // hash split into 40 hex digits
 *   }
 */

"use strict";

const path = require("path");
const readline = require("readline");

// Resolve relative to the parent repo root so the helper works regardless of
// the current working directory pytest invokes us from.
const repoRoot = path.resolve(__dirname, "..", "..", "..");
const Geopattern = require(path.join(repoRoot, "node_modules", "geopattern"));
const SHA1 = require(path.join(repoRoot, "node_modules", "geopattern", "lib", "sha1"));

const rl = readline.createInterface({ input: process.stdin });

rl.on("line", (rawSlug) => {
    // Strip the trailing newline that readline already removed; readline keeps
    // any other whitespace as-is (e.g. for the literal slug 'hello world').
    const slug = rawSlug;
    const encoded = encodeURI(slug);
    const hash = SHA1(encoded);
    // The app calls Geopattern.generate(encodeURI(slug)); mirror that exactly,
    // not Geopattern.generate(slug), to match the SHA1 input that the Pattern
    // constructor consumes.
    const pattern = Geopattern.generate(encoded);
    const hexValSeq = [];
    for (let i = 0; i < 40; i += 1) {
        hexValSeq.push(parseInt(hash.substr(i, 1), 16));
    }
    process.stdout.write(
        JSON.stringify({
            slug,
            encoded,
            hash,
            color: pattern.color,
            hexValSeq,
        }) + "\n",
    );
});

rl.on("close", () => {
    process.exit(0);
});
