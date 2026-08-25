# Day 5 - Evidence Sufficiency Loop

## Goal

Let the research agent decide whether
the collected evidence is sufficient.

## Architecture

Topic
→ Plan
→ Search
→ Evidence
→ Evaluate
   → sufficient → Write
   → insufficient → Search Again

## What I Learned

1. An agent should evaluate observations
   before deciding the next action.

2. Research does not need to stop after
   a fixed number of searches.

3. A critic can identify information gaps.

4. The next search query can be generated
   from the current evidence gap.

5. MAX_EXTRA_SEARCHES prevents
   uncontrolled research loops.

6. The writer still uses only collected
   evidence.

## Tests

- [x] weak evidence is rejected
- [x] simple topic can terminate
- [x] complex topic can trigger extra search
- [x] maximum search guard works

## Question for next day

How can research evidence be stored
and retrieved semantically instead of
keeping everything in the prompt?