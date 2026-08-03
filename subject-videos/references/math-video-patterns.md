# Mathematics Video Patterns

Use this reference for every high-school mathematics video with formulas, function graphs, derivations, or logic comparisons.

## Required Toolchain

| Need | Required pattern |
| --- | --- |
| Formula, set, domain, interval, derivation | KaTeX through a shared `MathFormula` component |
| Function or data graph | SVG rendered by React; D3 computes scales, axes, and paths |
| Expression sampling | Math.js parses the expression; sample only finite valid points in the intended domain |
| Motion | Remotion `frame`/`interpolate`; never CSS animation or a library timer |

Keep expression parsing, sampling, and path generation deterministic. Break paths at invalid or discontinuous samples; do not draw a misleading line across a hole, asymptote, or excluded domain point.

## Formula Boards

- Put formal notation in KaTeX, including the domain and any condition that controls validity.
- Reveal a derivation one semantic step at a time: condition, transformation, result, and check.
- Keep the original expression visible when a simplification removes a domain restriction.
- Reserve visual color for meaning: normal structure, current step, valid result, and invalid condition. Do not use color as the sole carrier of a conclusion.
- Use screen text for a short reason; leave complete prose explanation to narration and timed subtitles.

### LaTeX Source Safety

- In TSX props, prefer `latex={String.raw`...`}` when a formula contains LaTeX commands. JSX quoted attributes can silently consume backslashes and display command names as italic text.
- In TypeScript data, either use `String.raw` or escape every command consistently. Do not mix raw strings, JSX quoted attributes, and partially escaped strings in one formula pipeline.
- Render a still after adding commands such as `\Rightarrow`, `\quad`, `\dfrac`, `\infty`, or `\text`. Reject frames that display command names such as `Rightarrow`, `quad`, or `dfrac`.
- Render the formula, interval, and domain in KaTeX even when they appear in an example title or question header. Do not place raw formula text beside a correctly rendered derivation.

## Worked-Example Contract

Represent each example and each proof step as typed data. Each step should carry:

```ts
type WorkedStep = {
  label: string;
  latex: string;
  reason: string;
  detail?: string;
  warning?: string;
};
```

- Reveal one semantic step at a time: setup, operation, transformation, sign/condition check, and conclusion.
- Keep the active formula, its reason, its explanatory detail, and the matching subtitle visible at the same time.
- Give sign analysis its own visible checks. Do not jump from a transformed expression directly to the monotonicity verdict.
- Add a focused unit test for every nontrivial algebraic transformation, especially when factoring changes a sign or reverses an order.

## Logic-Comparison Pages

For a definition or identity that requires more than one condition:

1. Show the reference object and its formal conditions.
2. Give each candidate its own formula and stated domain.
3. Render one visible check per required condition.
4. Render an explicit final verdict after the checks.
5. Include at least one positive and one negative comparison, so the learner sees both the rule and its boundary.

Represent candidates as data with explicit booleans or verdict fields. Add a unit test that verifies the expected result before changing a faulty comparison page.

## Mathematics QA

- Render the start, middle, and end of every formula-dense, multi-card, graph, or reported-problem scene.
- Check KaTeX baseline alignment, superscripts, roots, fractions, set symbols, and domain notation at final video resolution.
- Check that subtitles do not cover graph axes, domain restrictions, verdicts, or final conclusions.
- Check graph examples against known points and domain restrictions in tests; check derivations and comparison verdicts as data rather than only by visual inspection.
- After TTS timing changes, verify each scene boundary is contiguous and every subtitle range lies inside its scene.
- Check graph geometry against mathematical invariants, not only appearance: correct quadrants, intercepts, asymptotes, holes, endpoints, and branch separation.
- For every worked example, render at least the setup, transformation, sign-analysis, and conclusion states. Verify that the narration cue at each frame explains the visible state.
