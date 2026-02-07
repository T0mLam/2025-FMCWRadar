# AI Usage Declaration

This document describes the usage of AI tools within the FMCW Radar project, what limits we place on them, and how we ensure we are compliant with university standards. We hereby declare that any and all AI usage within the project has been recorded and noted below. We understand that failing to divulge use of AI within our work counts as contract cheating and can result in a zero mark for SEP.

## AI Tools
- **ChatGPT 5.2** and **Google Gemini** are both used as conversational assistants to help with debugging code, note clean-ups to catch typos and grammar issues, and introductory research on new topics or new languages.
- **Editor Autocomplete:** (e.g. VS Code suggestions) is used to speed up typing not to generate significant program logic.

We do not rely on any AI tool to author large sections of code or documentation.

## Allowed use cases
- **Debugging support:** Asking for error interpretation and alternative approaches.
- **Code autocomplete:** Accept short completions (e.g. imports, boilerplate, trivial helpers) when we understand the result.
- **Formatting Notes:** Used to help catch typos and correct grammar not write entire sections.
- **Learning and research:** Request explanations of Python, libraries, TI radar concepts, etc.

All research and learning with the help of AI Tools is cross-referenced with official sources.

## Prohibited use cases
- **No large code generation:** We do not paste full functions/snippets of code produced by AI into the codebase.
- **No sensitive data:** We do not paste any proprietary material or documentation not publicly available into AI tools.
- **No copied text:** We do not use long passages suggested by AI to write our README or any other reports/presentations.

## Example Prompts

#### Research:

- “What is ONNX used for in ML deployment pipelines, and why would exporting a PyTorch model to ONNX help when compiling for embedded targets?”

- “Explain FMCW chirp configuration terms (slope, sampling rate, number of chirps/frames), how they work and why they are important."

#### Documentation:
- "We have written user instructions to add to the project README, however I would like it to be formatted into a `Click to expand` menu on markdown. How can I do that?"

- “Check this README section for spelling mistakes, inconsistent capitalization (e.g., Visualiser/Visualizer), and punctuation. Keep changes minimal."

#### Debugging:

- “Our Docusaurus site builds locally but fails in GitHub Pages with broken links and missing sidebar items. Here’s the error output and our `docusaurus.config.js` + `sidebars.js` what is the cause of this error?"

- “We added a `Record Data` button to the visualiser, but clicking it doesn’t create a file in `binData/`. Here’s the button callback code and the expected output path. What could be going wrong here?"


## Review Process
- All technical claims from AI are cross-referenced against primary sources (TI docs, SDK manuals etc.)

- Any AI-assisted edits that are kept are reviewed for correctness, style, and compliance with project standards.

## Compliance
- We follow University guidance on acceptable AI assistance and academic integrity

- We, the FMCW Radar team, declare that this document is accurate to our AI usage throughout the course of SEP.