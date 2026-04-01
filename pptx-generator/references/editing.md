# Editing Existing Presentations

## Single-Page Precision Edit Workflow (Preview → Confirm → Merge)

When you need to modify one specific slide in an existing deck with full visual control, use this two-stage workflow. It combines the WYSIWYG power of PptxGenJS with template-based editing.

```
Stage 1: Preview (iterative)
  1. Identify target slide N in template.pptx
  2. Rebuild slide N with PptxGenJS in slides_preview/
  3. Generate slide-N.pptx for user review
  4. User gives feedback -> adjust JS -> regenerate preview
  5. Repeat until user says "可以了"

Stage 2: Merge & Repack (one-shot)
  6. Run merge_slide.py to transplant the confirmed slide into unpacked/
  7. Repack -> overwrite original PPTX
```

### Directory Layout

```text
./
├── template.pptx               # Original file (never touched directly)
├── template.md                 # markitdown extraction for reference
├── unpacked/                   # Editable XML tree from template.pptx
│   ├── ppt/
│   │   ├── slides/
│   │   │   ├── slide1.xml
│   │   │   ├── slide2.xml
│   │   │   └── ...
│   │   └── media/
│   └── [Content_Types].xml
└── slides_preview/             # PptxGenJS preview outputs
    ├── slide-03.js
    ├── slide-03.pptx           # Single-slide preview for slide 3
    └── compile-slide-03.js
```

### Step-by-Step

**1. Unpack the original PPTX**

Already done during the initial template workflow:

```bash
python -c "
import zipfile, os
with zipfile.ZipFile('template.pptx', 'r') as z:
    z.extractall('unpacked')
"
```

**2. Create the preview script (`slides_preview/slide-03.js`)**

Re-draw the slide using PptxGenJS. Match the original dimensions (`LAYOUT_16x9` = 10" × 5.625" unless the template uses another layout). Use the original deck's color palette or a palette that fits the context.

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";

const slide = pres.addSlide();
slide.background = { color: "F5F5F5" };

// Rebuild all elements of slide 3 here
slide.addText("Updated Title", {
  x: 0.5, y: 0.5, w: 9, h: 1,
  fontSize: 36, bold: true, color: "22223b"
});

pres.writeFile({ fileName: "slide-03.pptx" });
```

Run it:

```bash
cd slides_preview && node slide-03.js
```

**3. User review loop**

Open `slides_preview/slide-03.pptx`, take a screenshot or describe what needs changing. Iterate on `slide-03.js` until the user confirms with phrases like **"可以了"**, **"OK"**, **"确认"**, or **"合并回去"**.

**4. Merge the confirmed slide back into `unpacked/`**

Use the provided `merge_slide.py` script. It handles slide XML replacement, relationship file porting, media deduplication, and `Content_Types.xml` updates.

```bash
python merge_slide.py slides_preview/slide-03.pptx unpacked/ 3
```

Arguments:
- `slides_preview/slide-03.pptx` — the confirmed single-slide PPTX
- `unpacked/` — the target unpacked directory
- `3` — the target slide number to overwrite

**5. Repack and overwrite the original file**

```bash
python -c "
import zipfile, os, glob

base = 'unpacked'
out = 'template_edited.pptx'

with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(base):
        for f in files:
            p = os.path.join(root, f)
            arc = os.path.relpath(p, base)
            zf.write(p, arc)
"
```

Then replace the original:

```bash
cp template_edited.pptx /path/to/user-provided.pptx
```

### Limitations & Safety Notes

- **Layout compatibility**: `merge_slide.py` copies the new slide's XML and rels directly. The preview PPTX must use standard layouts (`slideLayout1.xml`, `slideMaster1.xml`) that already exist in the target deck. Most PptxGenJS-generated slides and most real-world templates satisfy this.
- **Media deduplication**: If the source preview and target deck contain images with identical filenames but different content, `merge_slide.py` renames the incoming file to avoid collisions.
- **Animation loss**: PptxGenJS does not support animations. Any animations on the original slide will be lost after merge.
- **Only overwrite single slides**: Do not use this to merge multi-slide preview files. Generate one `.pptx` per slide.

### Alternative: python-pptx for Simple Edits

If the change is purely text or image replacement without layout changes, consider `python-pptx` instead of the preview-merge workflow:

```bash
pip install python-pptx
```

```python
from pptx import Presentation
prs = Presentation("template.pptx")
slide = prs.slides[2]  # zero-based
slide.shapes.title.text = "New Title"
prs.save("template_edited.pptx")
```

`python-pptx` is faster for trivial edits but cannot create new visual layouts as flexibly as PptxGenJS.

---

## Template-Based Workflow

When using an existing presentation as a template:

1. **Copy and analyze**:
   ```bash
   cp /path/to/user-provided.pptx template.pptx
   python -m markitdown template.pptx > template.md
   ```
   Review `template.md` to see placeholder text and slide structure.

2. **Plan slide mapping**: For each content section, choose a template slide.

   **USE VARIED LAYOUTS** — monotonous presentations are a common failure mode. Don't default to basic title + bullet slides. Actively seek out:
   - Multi-column layouts (2-column, 3-column)
   - Image + text combinations
   - Full-bleed images with text overlay
   - Quote or callout slides
   - Section dividers
   - Stat/number callouts
   - Icon grids or icon + text rows

   **Avoid:** Repeating the same text-heavy layout for every slide.

   Match content type to layout style (e.g., key points -> bullet slide, team info -> multi-column, testimonials -> quote slide).

3. **Unpack**: Extract the PPTX into an editable XML tree using Python's `zipfile` module. Pretty-print the XML for readability.

4. **Build presentation** (do this yourself, not with subagents):
   - Delete unwanted slides (remove from `<p:sldIdLst>`)
   - Duplicate slides you want to reuse (copy slide XML, relationships, and update `Content_Types.xml` and `presentation.xml`)
   - Reorder slides in `<p:sldIdLst>`
   - **Complete all structural changes before step 5**

5. **Edit content**: Update text in each `slide{N}.xml`.
   **Use subagents here if available** — slides are separate XML files, so subagents can edit in parallel.

6. **Clean**: Remove orphaned files — slides not in `<p:sldIdLst>`, unreferenced media, orphaned rels.

7. **Pack**: Repack the XML tree into a PPTX file. Validate, repair, condense XML, re-encode smart quotes.

   Always write to `/tmp/` first, then copy to the final path. Python's `zipfile` module uses `seek` internally, which fails on some volume mounts (e.g. Docker bind mounts). Writing to a local temp path avoids this.

## Output Structure

Copy the user-provided file to `template.pptx` in cwd. This preserves the original and gives a predictable name for all downstream operations.

```bash
cp /path/to/user-provided.pptx template.pptx
```

```text
./
├── template.pptx               # Copy of user-provided file (never modified)
├── template.md                 # markitdown extraction
├── unpacked/                   # Editable XML tree
└── edited.pptx                 # Final repacked deck
```

Minimum expected deliverable: `edited.pptx`.

## Slide Operations

Slide order is in `ppt/presentation.xml` -> `<p:sldIdLst>`.

**Reorder**: Rearrange `<p:sldId>` elements.

**Delete**: Remove `<p:sldId>`, then clean orphaned files.

**Add**: Copy the source slide's XML file, its `.rels` file, and update `Content_Types.xml` and `presentation.xml`. Never manually copy slide files without updating all references — this causes broken notes references and missing relationship IDs.

## Editing Content

**Subagents:** If available, use them here (after completing step 4). Each slide is a separate XML file, so subagents can edit in parallel. In your prompt to subagents, include:
- The slide file path(s) to edit
- **"Use the Edit tool for all changes"**
- The formatting rules and common pitfalls below

For each slide:
1. Read the slide's XML
2. Identify ALL placeholder content — text, images, charts, icons, captions
3. Replace each placeholder with final content

**Use the Edit tool, not sed or Python scripts.** The Edit tool forces specificity about what to replace and where, yielding better reliability.

## Formatting Rules

- **Bold all headers, subheadings, and inline labels**: Use `b="1"` on `<a:rPr>`. This includes:
  - Slide titles
  - Section headers within a slide
  - Inline labels like (e.g.: "Status:", "Description:") at the start of a line
- **Never use unicode bullets**: Use proper list formatting with `<a:buChar>` or `<a:buAutoNum>`
- **Bullet consistency**: Let bullets inherit from the layout. Only specify `<a:buChar>` or `<a:buNone>`.

## Common Pitfalls — Template Editing

### Template Adaptation

When source content has fewer items than the template:
- **Remove excess elements entirely** (images, shapes, text boxes), don't just clear text
- Check for orphaned visuals after clearing text content
- Run content QA with `markitdown` to catch mismatched counts

When replacing text with different length content:
- **Shorter replacements**: Usually safe
- **Longer replacements**: May overflow or wrap unexpectedly
- Verify with `markitdown` after text changes
- Consider truncating or splitting content to fit the template's design constraints

**Template slots != Source items**: If template has 4 team members but source has 3 users, delete the 4th member's entire group (image + text boxes), not just the text.

### Multi-Item Content

If source has multiple items (numbered lists, multiple sections), create separate `<a:p>` elements for each — **never concatenate into one string**.

**WRONG** — all items in one paragraph:
```xml
<a:p>
  <a:r><a:rPr .../><a:t>Step 1: Do the first thing. Step 2: Do the second thing.</a:t></a:r>
</a:p>
```

**CORRECT** — separate paragraphs with bold headers:
```xml
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 1</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" .../><a:t>Do the first thing.</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 2</a:t></a:r>
</a:p>
<!-- continue pattern -->
```

Copy `<a:pPr>` from the original paragraph to preserve line spacing. Use `b="1"` on headers.

### Smart Quotes

The Edit tool converts smart quotes to ASCII. **When adding new text with quotes, use XML entities:**

```xml
<a:t>the &#x201C;Agreement&#x201D;</a:t>
```

| Character | Name | Unicode | XML Entity |
|-----------|------|---------|------------|
| \u201c | Left double quote | U+201C | `&#x201C;` |
| \u201d | Right double quote | U+201D | `&#x201D;` |
| \u2018 | Left single quote | U+2018 | `&#x2018;` |
| \u2019 | Right single quote | U+2019 | `&#x2019;` |

### Other

- **Whitespace**: Use `xml:space="preserve"` on `<a:t>` with leading/trailing spaces
- **XML parsing**: Use `defusedxml.minidom`, not `xml.etree.ElementTree` (corrupts namespaces)
