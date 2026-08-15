# Remotion project setup and Studio timeline contract

This contract applies whenever the skill creates or updates a Remotion project below a `video/` directory. It prevents duplicate dependency installs and makes every page directly identifiable in Remotion Studio.

## Shared dependency policy

Before scaffolding files or running any package installation, resolve the intended `video_root`. Search only inside that root for a reusable `node_modules` directory. Never traverse into an existing `node_modules` while looking for another candidate.

Candidate priority:

1. `<video_root>/node_modules`
2. `<video_root>/_shared/node_modules`
3. a deliberately shared candidate no more than three directory levels below `<video_root>`

A candidate is usable only when it contains compatible manifests for `remotion`, `react`, and `react-dom`. Its package versions must satisfy the new project's `package.json`; successful existence checks alone are insufficient. Resolve the packages from the project directory after linking and run the package manager's dependency check.

The Remotion project's `node_modules` must be a **symbolic link** to the selected candidate. Prefer a relative link when it remains readable and stable. Do not automatically delete, replace, or merge:

- a real project-local `node_modules` directory;
- a broken link;
- a link pointing outside the declared `video_root`;
- a candidate with incompatible Remotion or React versions.

Stop and report those conflicts. Do not mutate a shared dependency tree merely to satisfy one video project.

If no valid shared candidate exists, create or install the dependency set once in the designated shared location under `video_root`, then link the project to it. Do not install a second full copy under the individual video project.

Record the decision in `dependency-link.json`:

```json
{
  "policy": "reuse_video_shared_node_modules_symlink",
  "video_root": "/absolute/path/to/video",
  "project_link": "node_modules",
  "link_target": "../../../node_modules",
  "resolved_target": "/absolute/path/to/video/node_modules",
  "required_packages": ["remotion", "react", "react-dom"],
  "compatibility_verified": true
}
```

Before Studio starts, verify all of the following:

- the project is inside `video_root`;
- `project/node_modules` is a symbolic link;
- the resolved target remains inside `video_root`;
- `remotion`, `react`, and `react-dom` resolve from the project;
- dependency versions are compatible;
- `python3 scripts/validate_remotion_project.py <project> --video-root <video_root>` passes.

## Stable page identity

Every page receives three related fields:

```json
{
  "page_id": "P001",
  "page_name": "开场：看不见的规则",
  "studio_sequence_name": "P001｜开场：看不见的规则"
}
```

- `page_id` uses uppercase `P` plus at least three digits. It is immutable after first assignment, even if pages are reordered.
- `page_name` is concise, unique in context, and describes the page's reasoning function or content problem.
- `studio_sequence_name` must equal `page_id + "｜" + page_name` exactly.

Carry the same ID through the canonical script, generated image name, timeline scene, Studio sequence, voiceover mark, QA report, and revision note. Report issues as, for example, `[P001] 字幕遮挡人物面部`.

## Studio-visible timeline

`src/timeline.json` must preserve both identity and display name:

```json
{
  "fps": 30,
  "totalFrames": 300,
  "scenes": [
    {
      "id": "P001",
      "name": "P001｜开场：看不见的规则",
      "durationFrames": 300
    }
  ]
}
```

Author every page sequence as **explicit authored JSX**. Do not construct Studio sequences with `pages.map()`, `scenes.map()`, or another runtime loop. Remotion Studio can then expose each sequence as a discrete, named timeline item that is easy to select and adjust.

```tsx
<Series>
  <Series.Sequence
    name="P001｜开场：看不见的规则"
    durationInFrames={timeline.scenes[0].durationFrames}
  >
    <StaticBookPage page={pages.P001} />
  </Series.Sequence>

  <Series.Sequence
    name="P002｜模型：规则如何形成"
    durationInFrames={timeline.scenes[1].durationFrames}
  >
    <StaticBookPage page={pages.P002} />
  </Series.Sequence>
</Series>
```

Data objects may be generated, but the `Series.Sequence` elements themselves must remain explicit and carry a literal `name` prop. When the page list changes, regenerate the explicit JSX and re-run the project validator.

## Studio acceptance check

In Remotion Studio, confirm that:

- every page appears as one separate timeline item;
- every item visibly shows the correct `P###｜page name`;
- clicking an item seeks to the intended full-screen page;
- item order matches the canonical script;
- the item's displayed duration matches `timeline.json`;
- no unnamed, duplicated, nested, or hidden page sequence exists;
- a reported page ID can be located in script data, JSX, assets, timeline, and QA notes without guessing.

The Studio check is incomplete if the composition plays but page numbers and names are not visible and independently addressable on the timeline.
