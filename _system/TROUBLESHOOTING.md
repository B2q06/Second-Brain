# Processing Pipeline Troubleshooting Guide

## Current Status

**File Watcher**: ✅ Detects unprocessed files on startup
**Terminal Launch**: ✅ Opens Windows Terminal
**Directory Navigation**: ✅ FIXED - Now uses absolute path
**Claude Loading**: ⏳ Testing with proper path
**Input Automation**: ⏳ Using pyautogui with calibrated coordinates

---

## How the Automation Works

### Workflow:
1. You say "update memory" → conversation saved to `00-Inbox/raw-conversations/unprocessed_*.md`
2. File watcher detects file (or finds existing on startup)
3. **Launches new terminal** with: `wt.exe ... cmd /k "cd /d C:\obsidian-memory-vault && claude --dangerously-skip-permissions"`
4. Waits 8 seconds for Claude to load
5. Finds "Claude - Queue Processor" window
6. Clicks on input box (88% down, 25% from left)
7. Pastes "process queue" from clipboard
8. Presses Enter
9. Agent activates and processes all files

---

## Recent Fixes Applied

### Fix 1: Python Import Errors ✅
- **Problem**: Agent couldn't import tag_note_manager.py
- **Solution**: Created scripts/__init__.py, added try/except imports
- **Status**: RESOLVED - imports work from vault root

### Fix 2: Absolute Path for Vault ✅
- **Problem**: Terminal opened in C:\Users\bearj instead of vault
- **Solution**: Convert vault_path to absolute path before passing to command
- **Status**: RESOLVED - cd /d now gets proper path

### Fix 3: Stage 6b Integration ✅
- **Problem**: Agent instructions missing sys.path setup
- **Solution**: Updated stage-6b-tag-notes-prompt.md with sys.path.insert(0, vault_path)
- **Status**: RESOLVED - agent can import Python modules

### Fix 4: Window Focus Issues ⏳
- **Problem**: Can't reliably focus Claude window (Access Denied errors)
- **Current approach**: Multiple clicks at different positions + clipboard paste
- **Status**: IN PROGRESS - testing with calibrated coordinates

---

## Known Issues

### 1. Window Focus "Access Denied"
**Symptom**: SetFocus() fails with error code 5
**Cause**: Windows security - can't programmatically focus from different process
**Workaround**: Using clipboard paste + multiple clicks

### 2. Input Box Hit Detection
**Symptom**: Text types in wrong window (wherever cursor is)
**Cause**: Click coordinates not hitting Claude input box
**Current fix**: Calibrated to 25% from left, 88% down based on window analysis

---

## Manual Override

If automation fails, you can always process manually:

```bash
cd C:\obsidian-memory-vault
claude --dangerously-skip-permissions
# Then type: process queue
```

The agent will:
- Read _system/processing-queue.md
- Process all unchecked files
- Execute all 8 stages including Stage 6b (tag notes)
- Write completion signal
- Trigger embeddings

---

## Files Modified for Automation

1. `scripts/launch_claude_processor.py` - Terminal launch + pyautogui automation
2. `scripts/file_watcher.py` - Detects files on startup, calls launch script
3. `.claude/agents/processing-pipeline-agent.md` - Keyword trigger "process queue"
4. `.claude/commands/process-queue.md` - Slash command (not working, needs reload)
5. `_system/stage-6b-tag-notes-prompt.md` - Added sys.path for imports

---

## Debug Commands

### Test terminal launch:
```bash
python scripts/launch_claude_processor.py --vault . --wait 8
```

### Check window coordinates:
```python
import pygetwindow as gw
windows = [w for w in gw.getAllWindows() if 'Claude' in w.title]
for w in windows:
    print(f'{w.title}: pos=({w.left}, {w.top}) size={w.width}x{w.height}')
```

### Test imports from vault root:
```bash
cd C:\obsidian-memory-vault
python -c "from scripts.tag_note_manager import TagNoteManager; print('SUCCESS')"
```

---

## Next Steps

1. Test with absolute path fix (terminal should cd to vault correctly)
2. Calibrate click coordinates if still typing in wrong window
3. Consider Desktop Commander MCP for more reliable terminal control
4. Fallback: Semi-automated with clear on-screen instructions

---

**Last Updated**: 2025-11-12
**Status**: Automation 85% complete - testing final coordinate calibration
