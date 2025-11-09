# MCP Server Setup Test

## Test Date: 2025-11-09

## Environment Variables Set
- ✅ NEO4J_PASSWORD
- ✅ ANTHROPIC_API_KEY

## Expected Results

When you open a **NEW terminal** and run `claude mcp list`, you should see:

```
Checking MCP server health...

neo4j: uvx mcp-neo4j-memory@0.4.2 - ✓ Connected
graphiti: graphiti-mcp  - ✓ Connected
obsidian: npx -y @iansinnott/obsidian-claude-code-mcp - ✓ Connected
```

## If Servers Fail to Connect

### neo4j Troubleshooting:
- Check Neo4j Desktop is running
- Verify database "memory-graph" is active
- Open http://localhost:7474 to confirm

### graphiti Troubleshooting:
- Verify `graphiti-mcp` command exists: `graphiti-mcp --help`
- Check pipx installation: `pipx list`
- Reinstall if needed: `pipx install 'git+https://github.com/rawr-ai/mcp-graphiti.git'`

### obsidian Troubleshooting:
- First run will download via npx (may take a minute)
- Check npm/npx is in PATH

## Test MCP Tools in Conversation

After servers connect, test in a Claude session:

```bash
claude
/mcp
```

Should show tools from all 3 servers.

## Test Pipeline Agent with MCP

1. **Start file watcher:**
   ```bash
   python scripts/file_watcher.py
   ```

2. **Create test conversation file:**
   ```bash
   echo "Test conversation for MCP integration" > C:/obsidian-memory-vault/00-Inbox/raw-conversations/unprocessed_test_mcp_20251109_001.md
   ```

3. **Watch for:**
   - Agent spawn message
   - Status updates showing stage progress
   - Completion with "Entities Created: X" (not 0)

4. **Verify in Neo4j:**
   - Open http://localhost:7474
   - Run: `MATCH (n) RETURN n LIMIT 25`
   - Should see conversation entities

## Success Criteria

- [ ] `claude mcp list` shows all 3 servers connected
- [ ] `/mcp` in conversation shows neo4j, graphiti, obsidian tools
- [ ] File watcher spawns agent successfully
- [ ] Agent creates entities in Neo4j (count > 0)
- [ ] QueueMonitor shows correct stage info (not "Unknown")
- [ ] Processing completes without errors

## Files Modified

1. `C:\Users\bearj\.claude.json` - Added mcpServers config
2. `C:\obsidian-memory-vault\scripts\file_watcher.py` - Fixed QueueMonitor regex
3. `C:\obsidian-memory-vault\.claude\agents\processing-pipeline-agent.md` - Added MCP instructions
4. `C:\obsidian-memory-vault\_system\processing-pipeline-protocol.md` - Added queue format + MCP usage

## Next Steps After Verification

1. Monitor automated processing as conversations are captured
2. Review Neo4j graph structure
3. Consider adding Graphiti advanced features if needed
4. Set up cost tracking for automated agent spawning
