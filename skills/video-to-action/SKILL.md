---
name: video-to-action
description: >
  Use Gemini as a video analysis passthrough to extract actionable steps from YouTube videos, tutorials, and demos. Claude queries Gemini about video content and converts it into executable instructions. Triggers on "watch this video", "learn from this video", "extract steps from video", "video to action", "analyze this YouTube", or /video-to-action. Also triggers on phrases like "what does this tutorial show", "turn this video into steps", or "learn from this tutorial".
allowed-tools: Read, Grep, Glob, Bash, Task, Write, Edit
---

# Video-to-Action via Gemini Passthrough

Claude can't watch video natively. But Gemini can analyze YouTube videos. Use Gemini as a passthrough: send it the video URL, ask structured questions, get back actionable steps that Claude can execute.

**Why this works:** Agents can now learn from the same medium humans learn from. A 30-minute tutorial becomes executable instructions. Course content, documentation videos, product demos — all become agent-parseable. The key insight: you don't need Claude to "see" the video — you need a structured extraction of what the video teaches, then Claude executes against that extraction.

## Execution

### 1. Parse the request

Extract from the user's message:
- **Video URL** — YouTube link or video identifier
- **Intent** — what the user wants to learn/do from the video
  - "Follow this tutorial" → extract and execute steps
  - "What does this video show?" → extract and summarize
  - "Learn this technique" → extract the technique as a reusable procedure
- **Scope** — full video or specific section ("the part about X", "starting at 5:00")

If no URL is provided, ask for one. If the intent is unclear, ask what they want to extract.

### 2. Query Gemini for video analysis

Use the `gemini-design` MCP server to analyze the video. Gemini can process YouTube URLs directly.

#### Phase 1: Overview extraction

Call `execute_task` with:
```
task: "Analyze this YouTube video and provide a structured breakdown."
context: |
  VIDEO URL: {url}

  Provide:
  1. VIDEO TITLE and approximate length
  2. SUMMARY — what the video teaches in 2-3 sentences
  3. PREREQUISITES — what tools, software, or knowledge is needed before starting
  4. MAIN SECTIONS — list the major sections/chapters with approximate timestamps
  5. KEY OUTCOMES — what the viewer can do after watching this video

  Be specific and concrete. Don't say "the presenter shows techniques" — say what the techniques are.
```

Read the response. If the video can't be analyzed (private, unavailable, not a tutorial), tell the user.

#### Phase 2: Step-by-step extraction

Call `execute_task` with:
```
task: "Extract detailed step-by-step instructions from this video."
context: |
  VIDEO URL: {url}

  For each major step in the video:
  1. STEP NUMBER and TITLE
  2. TIMESTAMP — approximately when this step occurs
  3. ACTION — what to do, in imperative form ("Click File > New", "Set the value to 0.5")
  4. DETAILS — any specific values, settings, parameters shown
  5. VISUAL REFERENCE — describe what the screen/result should look like after this step
  6. COMMON MISTAKES — if the presenter mentions pitfalls, note them

  Format as a numbered list. Be extremely specific about values, menu paths, and settings.
  If the presenter says "adjust to taste" or similar, note the value they actually used in the demo.

  {scope_constraint — e.g., "Focus only on the section about X" if user specified}
```

#### Phase 3: Technical details (if needed)

For coding tutorials, software workflows, or technical content, do a third pass:
```
task: "Extract all code, commands, configurations, and technical details from this video."
context: |
  VIDEO URL: {url}

  Extract:
  1. All CODE SNIPPETS shown (reconstruct from what's visible on screen)
  2. All TERMINAL COMMANDS run
  3. All CONFIGURATION values or settings changed
  4. All FILE PATHS referenced
  5. All DEPENDENCIES or PACKAGES installed
  6. Any API keys, environment variables, or config needed (note if they're placeholder values)

  For code: provide the complete snippet, not fragments. If code is partially visible, note what's inferred.
  For commands: provide the exact command, including flags and arguments.
```

### 3. Compile the procedure document

Combine all Gemini responses into a structured procedure document.

Write to `active/video-actions/{sanitized-video-title}.md`:

```markdown
# {Video Title} — Extracted Procedure

**Source**: {video URL}
**Extracted**: {date}
**Intent**: {what the user wants to do with this}

## Prerequisites
- {tool/software 1}
- {tool/software 2}
- {knowledge requirement}

## Steps

### Step 1: {title} ({timestamp})
**Action**: {what to do}
**Details**: {specific values, settings}
**Expected result**: {what it should look like after}
{Common mistake warning if applicable}

### Step 2: {title} ({timestamp})
...

## Code & Commands
{All extracted code snippets and commands, in order}

## Configuration
{All settings, env vars, config values mentioned}

## Notes
- {Any caveats, version-specific details, or "your mileage may vary" items}
```

### 4. Execute or deliver

Based on the user's intent:

#### "Follow this tutorial" → Execute the steps
- Work through the procedure step by step
- Use the extracted code/commands directly
- If a step requires visual verification you can't do, tell the user: "Step 5 requires visual confirmation — check that {expected result} before I continue"
- Adapt paths, filenames, and project structure to the user's actual environment

#### "What does this video show?" → Deliver the summary
- Present the overview and step list
- Don't execute anything
- Offer to execute if the user wants

#### "Learn this technique" → Save as reusable procedure
- Write the procedure doc to a permanent location (not `active/`)
- Suggest saving to project docs or a procedures directory
- Strip video-specific details, generalize where appropriate

### 5. Handle limitations

Be transparent about what Gemini can and can't extract:

- **Can extract**: Spoken instructions, on-screen text, code shown on screen, UI interactions described verbally, settings and values mentioned
- **Partially reliable**: Code that's partially visible, fast-scrolling content, background details
- **Cannot extract**: Subtle visual techniques (brush strokes, precise mouse movements), audio-only cues with no verbal description, content in languages Gemini doesn't support well

If a step relies on something Gemini couldn't capture, flag it:
```
Step 7: {title}
⚠️ LOW CONFIDENCE — This step involves a visual technique that may not be fully captured.
The video shows: {best description available}
Recommend: Watch {timestamp} directly for this step.
```

## Multi-video learning

For complex topics spanning multiple videos:

1. Extract procedures from each video separately
2. Merge into a single procedure, resolving conflicts (later videos override earlier ones)
3. De-duplicate steps that appear in multiple videos
4. Note where videos disagree on approach

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| detail_level | high | Extraction depth: summary, standard, high |
| execute | false | Auto-execute steps after extraction |
| save_location | active/video-actions/ | Where to save the procedure doc |
| phases | 2 | Analysis passes (2 for general, 3 for technical content) |

## Cost considerations

- Each Gemini call for video analysis: relatively cheap (Gemini pricing for video)
- 2-3 Gemini calls per video is typical
- Long videos (1hr+) may need to be analyzed in segments
- Consider extracting only the relevant section if the user specifies a scope

## Edge cases

- **Video is unavailable/private**: Tell the user. Suggest they provide a transcript instead.
- **Video is not a tutorial**: Still extract what's useful — key claims, demonstrated results, referenced tools. Note that it's not step-by-step content.
- **Video is very long (1hr+)**: Ask the user which section matters. Analyze in segments if they want the full thing.
- **Video is in a non-English language**: Gemini handles many languages. Note the language and any potential translation artifacts.
- **Extracted code doesn't work**: Common — video code is often shown partially or has typos. Note which parts were inferred and flag them for the user to verify.
- **Video content is outdated**: Check if tools/APIs shown in the video have newer versions. Note version discrepancies.
- **Existing procedure file**: Overwrite in `active/video-actions/`. These are working documents.

## Output files

| File | Description |
|------|-------------|
| `active/video-actions/{video-title}.md` | Extracted procedure document |

Previous extractions are kept (one file per video, not overwritten across different videos).