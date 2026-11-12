# SPEC.md template — product agreement

Use this template for backend and other non-frontend work. It records the agreed product behavior and acceptance criteria; websites and frontend-only work do not require a spec.

## Rules for keeping it useful

- Describe what the product must do, for whom, and under which constraints. Include business rules and scope; exclude architecture research, implementation plans, commands, status, and history.
- Ask thoughtful follow-up questions about meaningful gaps before treating a rule as agreed. Reuse existing answers and inspect available context; do not repeat obvious questions or stop at a fixed number of rounds.
- Write multiple distinct success and failure criteria covering important workflows, alternatives, boundaries, and recovery. Do not pad counts with duplicates or generic wishes.
- Each criterion has an ID, a concrete scenario, an observable expected/prohibited result, and a feasible acceptance check. Use agreed thresholds where relevant; do not invent them.
- Keep unresolved product decisions visibly unapproved. Do not silently turn assumptions or current implementation behavior into requirements.
- Keep requirements concise without removing necessary detail to meet a line cap. Link detailed feature agreements when useful.
- Change approved requirements only when authorized by the user. Failing code or tests do not change the agreement.
- Keep setup/test commands and technical choices in the README or an existing run/design guide. Keep concise progress and verification evidence in the required project-root `changelog.md`, including for frontend projects without a spec.
- Use plain language and never include secrets or customer data. Use synthetic examples.

## Skeleton

```markdown
# <Product or feature name>

## Product agreement
<What it does, who uses it, and the real workflow it supports.>

GOAL: <The overall observable outcome.>

SCOPE:
- Included: <workflows and capabilities covered now>.
- Excluded: <explicit boundaries>.

CONSTRAINTS:
- <Hard limits: budget, compatibility, permissions, required stack if specified>.

FORMAT:
- <Required inputs, outputs, destinations, and delivery surface>.

## Business rules
- <Agreed calculations, thresholds, permissions, and exception behavior>.

## SUCCESS — acceptance criteria
| ID | Scenario / example input | Expected result | Acceptance check |
| --- | --- | --- | --- |
| S1 | <Actor, starting conditions, trigger> | <Observable result; agreed threshold if relevant> | <How to observe or test it> |
| S2 | <Meaningful alternative scenario> | <Specific expected result> | <How to observe or test it> |

## FAILURE — any triggered condition means not done
| ID | Scenario / trigger | Unacceptable outcome | Acceptance check |
| --- | --- | --- | --- |
| F1 | <Relevant error or edge case> | <Concrete prohibited result> | <How to detect it> |
| F2 | <Another distinct failure scenario> | <Concrete prohibited result> | <How to detect it> |

<Add enough distinct criteria for the actual workflows and risks; the sample rows are not a quota or a limit.>

## Unresolved product decisions
- <Only when applicable: the missing decision and affected behavior; clearly unapproved>.
```

## Example of useful precision

- Success: Given a valid request, when the caller retries that same request, the system returns the original record and the stored record count remains one. Check by submitting the same request twice and inspecting both responses and stored data.
- Failure: When a request is rejected for invalid input, any record is created or any customer email is sent. Check both stored data and the email boundary after the rejected request.

These are examples, not default requirements. Choose relevant scenarios with the user. An acceptance check describes how to determine whether a requirement holds; execution dates, commands, pass/fail results, and evidence belong outside the agreement.
