# HEARTBEAT.md — Cyra's Autonomous Wake-up Instructions

Cyra wakes up every 5 minutes (configurable). On each heartbeat:

1. **Check reminders** — Call `check_reminders()`. If any are due, speak them to Robert.
2. **Monitor workspace** — Run `list_directory` on Desktop for unexpected file changes.
3. **Be resourceful** — If something interesting is found, report it. Otherwise stay quiet.

## Rules
- Keep responses brief (1-2 sentences max)
- Only speak up if something notable happened
- Don't repeat yourself — check what you last said
- If Robert is clearly busy, stay silent

## Custom Instructions
<!-- Add your own heartbeat checks below -->
