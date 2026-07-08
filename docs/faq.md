# Frequently Asked Questions

## Why does the repository require documentation with every implementation?

Embedded failures often come from timing, power, electrical, scheduling, or production assumptions that are not visible in code. Documentation preserves those assumptions and explains how to validate them.

## Why not keep everything in the root README?

A single README cannot scale across theory, APIs, debugging, benchmarks, production, examples, diagrams, and references. The root README is an entry point; detailed engineering knowledge belongs in focused documents.

## What makes an example acceptable?

An example should be independently understandable and should include wiring, build instructions, expected output, validation method, and failure modes.

## What makes a benchmark acceptable?

A benchmark must include hardware revision, firmware revision, configuration, instrumentation, procedure, measured result, and acceptance criteria.

## Should references include blog posts?

References should prioritize official documentation, datasheets, standards, books, and peer-reviewed or academic sources. Blog posts may be useful background but should not be the primary engineering authority.
