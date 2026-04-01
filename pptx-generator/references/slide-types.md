# Slide Page Types

Classify **every slide** as **exactly one** of these 5 types:

## 1. Cover Page

- **Use for**: Opening + tone setting
- **Content**: Big title, subtitle/presenter, date/occasion, strong background/motif

### Layout Options

**Asymmetric Left-Right Layout**
- Text concentrated on one side, image on the opposite
- Best for: Corporate presentations, product launches, professional reports
```
|  Title & Subtitle  |    Visual/Image    |
|  Description       |                    |
```

**Center-Aligned Layout**
- Content centered with background image
- Best for: Inspirational talks, event presentations, creative pitches
```
|                                        |
|           [Background Image]           |
|              MAIN TITLE                |
|              Subtitle                  |
|                                        |
```

### Font Size Hierarchy

| Element | Recommended Size | Ratio to Base |
|---------|-----------------|---------------|
| Main Title | 72-120px | 3x-5x |
| Subtitle | 28-40px | 1.5x-2x |
| Supporting Text | 18-24px | 1x (base) |
| Meta Info (date, name) | 14-18px | 0.7x-1x |

**Key Principles:**
1. **Dramatic Contrast**: Main title should be at least 2-3x larger than subtitle
2. **Visual Anchor**: The largest text becomes the focal point
3. **Readable Hierarchy**: Viewers should instantly understand what's most important
4. **Avoid Similarity**: Never let adjacent text elements be within 20% of each other's size

### Content Elements

1. **Main Title** — Always required, largest font
2. **Subtitle** — When additional context is needed (clearly smaller than title)
3. **Icons** — When they reinforce the theme
4. **Date/Event Info** — When relevant (smallest text)
5. **Company/Brand Logo** — When representing an organization
6. **Presenter Name** — For keynotes (small, subtle)

### Design Decisions

Consider: Purpose (corporate/educational/creative), Audience, Tone, Content Volume, Visual Assets needed.

### Workflow

1. **Analyze**: Understand topic, audience, purpose
2. **Choose Layout**: Select based on content
3. **Write Slide**: Use PptxGenJS. Use shapes and SVG elements for visual interest.
4. **Verify**: Generate preview as `slide-XX-preview.pptx`. Extract text with `python -m markitdown slide-XX-preview.pptx`, verify all content present and no placeholder text remains.

---

## 2. Table of Contents

- **Use for**: Navigation + expectation setting (3-5 sections)
- **Content**: Section list (optional icons / page numbers)

### Layout Options

**Numbered Vertical List** — Best for 3-5 sections, straightforward presentations
```
|  TABLE OF CONTENTS            |
|                                |
|  01  Section Title One         |
|  02  Section Title Two         |
|  03  Section Title Three       |
```

**Two-Column Grid** — Best for 4-6 sections, content-rich presentations
```
|  TABLE OF CONTENTS              |
|                                  |
|  01  Section One   02  Section Two  |
|      Description       Description  |
|  03  Section Three 04  Section Four |
```

**Sidebar Navigation** — Best for 3-5 sections, modern/corporate
```
| ▌01 |  Section Title One           |
| ▌02 |  Section Title Two           |
| ▌03 |  Section Title Three         |
```

**Card-Based** — Best for 3-4 sections, creative/modern
```
|  TABLE OF CONTENTS                    |
|  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  |
|  │ 01  │  │ 02  │  │ 03  │  │ 04  │  |
|  │Title│  │Title│  │Title│  │Title│  |
|  └─────┘  └─────┘  └─────┘  └─────┘  |
```

### Font Size Hierarchy

| Element | Recommended Size | Ratio to Base |
|---------|-----------------|---------------|
| Page Title ("Table of Contents" / "Agenda") | 36-44px | 2.5x-3x |
| Section Number | 28-36px | 2x-2.5x |
| Section Title | 20-28px | 1.5x-2x |
| Section Description | 14-16px | 1x (base) |

**Key Principles:**
1. **Clear Numbering**: Section numbers should be visually prominent — bold, accent color, or larger size
2. **Scannable Structure**: Viewer should scan all sections in 2-3 seconds
3. **Consistent Spacing**: Equal vertical spacing between sections
4. **Visual Markers**: Colored dots, lines, numbers, or icons to anchor each section
5. **Avoid Clutter**: Descriptions one line max or omit entirely

### Content Elements

1. **Page Title** — Always required ("Table of Contents", "Agenda", "Overview")
2. **Section Numbers** — Consistent format (01, 02... or I, II...)
3. **Section Titles** — Clear and concise
4. **Section Descriptions** — Optional one-line summaries
5. **Visual Separators** — SVG dividers or spacing
6. **Decorative Elements** — Subtle accent shapes
7. **Page Number Badge** — **MANDATORY**

### Design Decisions

1. **Section Count**: 3 → vertical list; 4-6 → grid or compact; 7+ → multi-column
2. **Description Length**: Long → vertical list; None → compact grid/cards
3. **Tone**: Corporate → numbered list; Creative → card-based; Academic → Roman numerals
4. **Consistency**: Match visual style of cover page

### Workflow

1. **Analyze**: Section list, count, presentation context
2. **Choose Layout**: Based on section count and content
3. **Plan Visual Hierarchy**: Numbering style, font sizes, spacing
4. **Write Slide**: Use PptxGenJS. Use shapes for decorative elements. **MUST include page number badge.**
5. **Verify**: Generate preview, extract text with markitdown, verify content and badge.

---

## 3. Section Divider

- **Use for**: Clear transitions between major parts
- **Content**: Section number + title (+ optional 1-2 line intro)

### Layout Options

**Bold Center** — Best for minimal, modern presentations
```
|                  02                    |
|           SECTION TITLE               |
|         Optional intro line           |
```

**Left-Aligned with Accent Block** — Best for corporate, structured presentations
```
| ████ |  02                            |
| ████ |  SECTION TITLE                 |
| ████ |  Optional intro line           |
```

**Split Background** — Best for high-contrast, dramatic transitions
```
| ██████████ |     SECTION TITLE        |
| ██  02  ██ |     Optional intro       |
| ██████████ |                          |
```

**Full-Bleed Background with Overlay** — Best for creative, bold presentations
```
| ████████████████████████████████████  |
| ████       large 02        █████████ |
| ████    SECTION TITLE      █████████ |
| ████████████████████████████████████  |
```

### Font Size Hierarchy

| Element | Recommended Size | Notes |
|---------|-----------------|-------|
| Section Number | 72-120px | Bold, accent color or semi-transparent |
| Section Title | 36-48px | Bold, clear, primary text color |
| Intro Text | 16-20px | Light weight, muted color, optional |

**Key Principles:**
1. **Dramatic Number**: Section number = most prominent visual element
2. **Strong Title**: Large but clearly secondary to the number
3. **Minimal Content**: Just number + title + optional one-liner
4. **Breathing Room**: Leave generous whitespace — dividers are pause moments

### Content Elements

1. **Section Number** — Always required. Format: `01`, `02`... or `I`, `II`... Match TOC style.
2. **Section Title** — Always required. Clear, concise.
3. **Intro Text** — Optional 1-2 line description.
4. **Decorative Elements** — SVG accent shapes (bars, lines, geometric blocks).
5. **Page Number Badge** — **MANDATORY**.

### Design Decisions

1. **Tone**: Corporate → accent block; Creative → full-bleed; Minimal → bold center
2. **Color**: Strong palette color for background/accent; high-contrast text
3. **Consistency**: Same divider style across all dividers in one presentation
4. **Contrast with content slides**: Visually distinct (different background color, more whitespace)

### Workflow

1. **Analyze**: Section number, title, optional intro
2. **Choose Layout**: Based on content and tone
3. **Write Slide**: Use PptxGenJS. Use shapes for decorative elements. **MUST include page number badge.**
4. **Verify**: Generate preview, extract text, verify content and badge.

---

## 4. Content Page

Pick a subtype based on the content. Each content slide belongs to exactly ONE subtype:

### Subtypes

**Text** — Bullets, quotes, or short paragraphs
- Must still include icons or SVG shapes — never plain text only
```
|  SLIDE TITLE                          |
|  * Bullet point one                   |
|  * Bullet point two                   |
|  * Bullet point three                 |
```

**Mixed Media** — Two-column or half-bleed image + text
```
|  SLIDE TITLE                          |
|  Text content     |  [Image/Visual]   |
|  and bullets      |                   |
```

**Data Visualization** — Native chart, composed infographic, or external rendered chart + takeaways
- Must include data source
- Every data slide must pair visual with 1-3 key takeaways
```
|  SLIDE TITLE                          |
|  [Chart/Infographic] | Key Takeaway 1  |
|                      | Key Takeaway 2  |
|                      Source: xxx       |
```

**Chart Options (choose based on data and visual need):**

| Visual Type | Best For | Implementation |
|-------------|----------|----------------|
| Native Bar/Column | Comparisons, rankings | `pres.charts.BAR` with styling |
| Native Line/Area | Trends over time | `pres.charts.LINE` with smooth curves |
| Native Pie/Doughnut | Part-to-whole, market share | `pres.charts.PIE` / `DOUGHNUT` |
| Native Scatter/Bubble | Correlations, distributions | `pres.charts.SCATTER` / `BUBBLE` |
| Native Radar | Multi-dimensional scores | `pres.charts.RADAR` |
| Composed Progress Ring | Completion rates, OKRs | Shapes (arc/oval + text) |
| Composed Funnel | Conversion stages | Stacked trapezoids or rounded rects |
| Composed Pictogram | People/products/units | Repeated icons scaled to value |
| Composed Waterfall | Step-by-step gains/losses | Sequential rectangles |
| External Rendered | Advanced/interactive charts | ECharts → SVG → PNG base64 |

**Data Visualization Rules:**
1. **No chart without takeaway** — always explain what the data means
2. **Max 1 chart per slide** — split complex stories across slides
3. **Match palette** — chart colors must come from the chosen palette
4. **Label clearly** — axis names, units, and legends must be readable at a glance
5. **Prefer composed infographics when native charts are too plain** — e.g. donut rings beat basic pie charts for visual impact

**Comparison** — Side-by-side columns or cards (A vs B, pros/cons)
```
|  SLIDE TITLE                          |
|  ┌─ Option A ─┐  ┌─ Option B ─┐      |
|  │  Detail 1  │  │  Detail 1  │      |
|  └────────────┘  └────────────┘      |
```

**Timeline / Process** — Steps with arrows, journey, phases
```
|  SLIDE TITLE                          |
|  [1] ──→ [2] ──→ [3] ──→ [4]         |
|  Step    Step    Step    Step          |
```

**Image Showcase** — Hero image, gallery, visual-first layout
```
|  SLIDE TITLE                          |
|  ┌────────────────────────────────┐   |
|  │         [Hero Image]           │   |
|  └────────────────────────────────┘   |
|  Caption or supporting text           |
```

### Font Size Hierarchy

| Element | Recommended Size | Notes |
|---------|-----------------|-------|
| Slide Title | 36-44px | Bold, top of slide |
| Section Header | 20-24px | Bold, for sub-sections within slide |
| Body Text | 14-16px | Regular weight, left-aligned |
| Captions / Source | 10-12px | Muted color, smallest text |
| Stat Callout | 60-72px | Large bold numbers for key statistics |

**Key Principles:**
1. **Left-align body text** — never center paragraphs or bullet lists
2. **Size contrast** — title must be 36pt+ to stand out from 14-16pt body
3. **Visual elements required** — every content slide must have at least one non-text element
4. **Breathing room** — 0.5" minimum margins, 0.3-0.5" between content blocks

### Content Elements

1. **Slide Title** — Always required, top of slide
2. **Body Content** — Text, bullets, data, or comparisons based on subtype
3. **Visual Element** — Image, chart, icon, or SVG shape — always required
4. **Source / Caption** — When showing data or external content
5. **Page Number Badge** — **MANDATORY**

### Design Decisions

1. **Subtype**: Determine first — drives the entire layout
2. **Content Volume**: Dense → multi-column or smaller font; Light → larger elements with more whitespace
3. **Data vs Narrative**: Data-heavy → charts + stat callouts; Story-driven → images + quotes
4. **Variety**: Each content slide should use a different layout from the previous one
5. **Consistency**: Typography, colors, and spacing must match the rest of the presentation

### Workflow

1. **Analyze**: Content, determine subtype, plan layout
2. **Choose Layout**: Best fit for subtype and content volume
3. **Write Slide**: Use PptxGenJS. Use shapes for charts, decorative elements, icons. **MUST include page number badge.**
4. **Verify**: Generate preview as `slide-XX-preview.pptx`. Extract text with markitdown, verify all content present, no placeholder text, badge included.

---

## 5. Summary / Closing Page

- **Use for**: Wrap-up + action
- **Content**: Key takeaways, CTA/next steps, contact/QR, thank-you

### Layout Options

**Key Takeaways** — Best for educational, corporate, data-driven presentations
```
|  KEY TAKEAWAYS                        |
|  ✓  Takeaway one                      |
|  ✓  Takeaway two                      |
|  ✓  Takeaway three                    |
```

**CTA / Next Steps** — Best for sales pitches, proposals, project kick-offs
```
|  NEXT STEPS                           |
|  [1] Action item one                  |
|  [2] Action item two                  |
|  Contact: email@example.com           |
```

**Thank You / Contact** — Best for conference talks, keynotes
```
|            THANK YOU                   |
|         name@company.com              |
|         @handle | website.com         |
```

**Split Recap** — Best for presentations needing both recap and action
```
|  SUMMARY            |  NEXT STEPS      |
|  * Point one        |  Contact us at   |
|  * Point two        |  email@co.com    |
|  * Point three      |  [QR Code]       |
```

### Font Size Hierarchy

| Element | Recommended Size | Notes |
|---------|-----------------|-------|
| Closing Title ("Thank You" / "Summary") | 48-72px | Bold, commanding |
| Takeaway / Action Item | 18-24px | Clear, scannable |
| Supporting Text | 14-16px | Regular weight |
| Contact Info | 14-16px | Muted color |

**Key Principles:**
1. **Strong closing statement**: Main message should be largest, most prominent
2. **Scannable items**: Takeaways/action items concise (one line each)
3. **Contact clarity**: Legible but not dominant
4. **Memorable finish**: Confident, polished ending

### Content Elements

1. **Closing Title** — Always required
2. **Takeaway Points** — 3-5 concise summary points (if applicable)
3. **Call to Action** — Clear next steps (if applicable)
4. **Contact Info** — Email, website, social handles (if provided)
5. **Decorative Elements** — SVG accents for visual consistency
6. **Page Number Badge** — **MANDATORY**

### Design Decisions

1. **Closing Type**: Recap, CTA, thank-you, or combination
2. **Content Volume**: Many takeaways → list; Simple closing → centered thank-you
3. **Audience Action**: Audience needs to do something → CTA; Informational → takeaways
4. **Tone Consistency**: Match energy of cover page
5. **Visual Distinction**: Special but not disconnected from the rest

### Workflow

1. **Analyze**: Closing content — takeaways, CTA, contact, thank-you
2. **Choose Layout**: Based on content type
3. **Write Slide**: Use PptxGenJS. Use shapes for decorative elements. **MUST include page number badge.**
4. **Verify**: Generate preview, extract text, verify content and badge.

---

## Additional Layout Patterns

Use these across content slides for visual variety:

- **Two-column** (text left, illustration right)
- **Icon + text rows** (icon in colored circle, bold header, description below)
- **2x2 or 2x3 grid** (image on one side, grid of content blocks on other)
- **Half-bleed image** (full left or right side) with content overlay
- **Large stat callouts** (big numbers 60-72pt with small labels below)
- **Comparison columns** (before/after, pros/cons)
- **Timeline or process flow** (numbered steps, arrows)
- **Icons in small colored circles** next to section headers
- **Italic accent text** for key stats or taglines
