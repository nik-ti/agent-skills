# Writing the knowledge doc

Write for one smart reader who hasn't watched any of these videos. This is a long-form read: not a summary, not a book. Teach each concept the way a good friend who watched everything would explain it.

## Length

| Depth | Reading time | Words |
|---|---|---|
| Focused | about 15 min | 3,000 to 4,000 |
| Standard | about 30 min | 6,000 to 8,000 |
| Deep | about 60 min | 12,000 to 15,000 |

These are targets for rich material. Thin sources give a shorter doc, and the doc says so at the top. As a guide, a doc shouldn't run past about 1.5 times the words of its transcripts, and a repetitive conversation condenses further than a tight lecture.

## Structure

1. **Title and framing.** What this covers, whose ideas they are and how many hours it condenses. Use a title like "Notes on <channel>: <theme>", so the page can't pass for the creator's own work.
2. **The short version.** Five to eight of the most important takeaways, so the reader has the map before the territory.
3. **Concept sections.** The bulk of the doc, in the order from your outline. Each builds on the last.
4. **Where they disagree or changed their mind**, if it applies. These are often the most interesting parts, and they can also sit inside the relevant sections.
5. **What to do with this**, if the material is practical.
6. **Sources.** The assembler builds this list. Put any caveats, such as caption gaps or how thin the material was, in `{{SOURCE_NOTES}}`.

## Teaching well

- Start each section from the question or problem the concept answers, then build the idea up. Define a term the first time it appears.
- Use the speakers' own examples, since they're usually the most memorable part. A concrete case beats an abstract restatement.
- Give the reasoning, not only the conclusion: why it works, when it fails, what it trades away.
- Vary the rhythm. Prose carries the explanation; use lists for things that really are lists, and diagrams for structure.

## Honesty

- Credit ideas to the speaker in the text ("Karpathy argues..."). Their opinion is not established fact, and a shaky claim should read that way.
- Everything in the main text comes from the transcripts, so the reader can always tell the channel's ideas from yours. Your own additions go in labelled boxes: `.background` for outside context, and `.apply` for connecting an idea to the reader's stated purpose.
- Check claims that carry weight. When a speaker leans on a study, statistic or history that sounds doubtful, verify it with a quick web search and report the result in a `.background` note with a link. Channels often oversell, and this can be the most useful thing the doc does. If you didn't check something, don't imply that you did.
- If a name or number was unclear in the captions, say so or leave it out.
- Paraphrase. Keep quotes short and only where the exact words matter. The doc teaches the ideas and doesn't reproduce the transcript.

## Citations

Cite right after the idea with `[[V3 12:34]]`, using the V number printed by the chunker and a stamp from the notes. The assembler turns these into linked chips. When an idea appears in several videos, cite each. Aim for a citation about once a paragraph, not on every sentence.

## Language

Write in the language agreed in the interview. For a non-English doc, also translate the template's headings and the `L` labels at the top of its script. Avoid filler like "in this section we will explore" or "it's important to note". Don't use a "not X, but Y" reveal as a habit. Plain, specific sentences teach better.
