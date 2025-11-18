#!/usr/bin/env node
/**
 * claude-exec - Execute Claude Code with an initial message
 *
 * Wrapper around Claude Code CLI that sends an initial message automatically
 * then allows continued interaction.
 *
 * Usage: node claude-exec.js "file watcher summons you" --dangerously-skip-permissions
 */

const { spawn } = require('child_process');
const process = require('process');

// Parse arguments
const args = process.argv.slice(2);

if (args.length === 0) {
    console.error('Usage: claude-exec "message" [claude-options]');
    console.error('Example: claude-exec "process queue" --dangerously-skip-permissions');
    process.exit(1);
}

// First argument is the message to execute
const initialMessage = args[0];

// Remaining arguments are passed to claude
const claudeArgs = args.slice(1);

console.log('[*] Starting Claude Code with initial message...');
console.log(`    Message: "${initialMessage}"`);
console.log(`    Args: ${claudeArgs.join(' ')}`);
console.log();

// Spawn Claude Code (use full path on Windows)
const claudePath = 'C:\\Users\\bearj\\AppData\\Roaming\\npm\\claude.cmd';
const fs = require('fs');

let allOutput = '';

const claude = spawn(claudePath, claudeArgs, {
    stdio: ['pipe', 'pipe', 'pipe'],  // Capture all for logging
    cwd: process.cwd(),
    shell: true
});

// Capture output
claude.stdout.on('data', (data) => {
    const text = data.toString();
    allOutput += text;
    process.stdout.write(text);
});

claude.stderr.on('data', (data) => {
    const text = data.toString();
    allOutput += '[STDERR] ' + text;
    process.stderr.write(text);
});

// Wait for Claude to initialize, then send message
setTimeout(() => {
    console.log('[*] Sending initial message...');

    claude.stdin.write(initialMessage + '\n');

    console.log('[+] Message sent!');
    console.log('[*] Waiting 12 seconds for agent response...');

    // Wait, then save output and check for success
    setTimeout(() => {
        // Save all captured output
        fs.writeFileSync('terminal_output.txt', allOutput, 'utf-8');
        console.log('[+] Terminal output saved to terminal_output.txt');

        // Check for success.txt
        if (fs.existsSync('success.txt')) {
            console.log('[SUCCESS] Agent created success.txt!');
            const content = fs.readFileSync('success.txt', 'utf-8');
            console.log('Content:', content);
        } else {
            console.log('[FAILED] No success.txt found');
            console.log('[i] Check terminal_output.txt to see what happened');
        }

        process.exit(0);

    }, 12000);

}, 5000); // Wait 5 seconds for Claude to load

// Handle Claude exit
claude.on('close', (code) => {
    console.log(`\n[i] Claude exited with code ${code}`);
    process.exit(code);
});

// Handle errors
claude.on('error', (err) => {
    console.error(`[X] Error spawning Claude: ${err.message}`);
    process.exit(1);
});
