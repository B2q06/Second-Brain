# Pipeline Agent Processing Logs

This directory contains detailed logs from the Processing Pipeline Agent. Each log captures the complete audit trail of a pipeline run.

## Log Structure

Logs are automatically created by the Processing Pipeline Agent at the end of Stage 8 (Finalization), just before the completion signal is written.

### Filename Format

```
processing_log_YYYY-MM-DD_HHMMSS_NNNN.md
```

- **Date**: `YYYY-MM-DD` - The date the pipeline ran
- **Time**: `HHMMSS` - The time the pipeline completed (24-hour format)
- **Log Number**: `NNNN` - Sequential log number (0001, 0002, etc.)

### Example

```
processing_log_2025-11-17_143045_0001.md
```

This log was created on November 17, 2025 at 14:30:45 (2:30:45 PM) and is log #1.

## Log Contents

Each log contains:

1. **Frontmatter Metadata**
   - Log number, timestamp, date, time
   - Enables easy filtering and sorting

2. **Files Processed**
   - List of all conversation files processed in this run

3. **Summary Statistics**
   - Total files, entities, relationships, tag notes created
   - Processing duration

4. **Stage Completion Checklist**
   - Shows which stages completed successfully
   - Useful for debugging partial failures

5. **Errors & Warnings**
   - Any issues encountered during processing
   - Empty if processing was successful

6. **Next Actions**
   - Suggested follow-up tasks
   - New areas to review, monthly consolidations pending, etc.

7. **File Details**
   - Per-file breakdown of entities, tags, duration, novelty score
   - Primary area assignment for each conversation

## Usage

### Viewing Logs in Obsidian

Logs are Markdown files with frontmatter, so they integrate seamlessly with Obsidian:

- View in graph view to see connections
- Search by date, log number, or content
- Link to logs from other notes using `[[processing_log_2025-11-17_143045_0001]]`

### Viewing Logs in File Watcher

When the pipeline completes, the file watcher automatically:
1. Detects the completion signal
2. Reads the latest processing log
3. Displays a summary in the terminal
4. Removes the completion signal file

### Manual Review

You can manually review any log to:
- Audit what was processed
- Troubleshoot errors
- Track pipeline performance over time
- Understand how conversations were categorized

## Log Rotation

Currently, logs are **not automatically deleted**. They accumulate over time to provide a complete audit trail.

### Future Considerations

- Archive logs older than 90 days
- Compress old logs
- Summary reports aggregating multiple logs

## Integration with Pipeline

The logging happens in Stage 8 of the Processing Pipeline Protocol:

1. **Create Detailed Processing Log** (this directory)
2. **Signal Completion** (write to `_system/agent_completion_signal.txt`)
3. **Agent Exits** (clean shutdown)

The file watcher monitors the completion signal, displays the log summary, then removes the signal file.

---

**Related Documentation:**
- `_system/processing-pipeline-protocol.md` - Full pipeline specification
- `scripts/file_watcher.py` - File watcher implementation
