# Marp Presentation Guide

This guide provides instructions on how to create and customize presentations using Marp.

## Getting Started

1.  **Install Marp CLI:** If you haven't already, install the Marp command-line interface:
    ```bash
    npm install -g @marp-team/marp-cli
    ```

2.  **Create a Markdown File:** Create a new `.md` file in the `presentations` directory.

3.  **Add Marp Front-matter:** At the top of your Markdown file, add the following front-matter to enable Marp:
    ```yaml
    ---
    marp: true
    ---
    ```

## Creating Slides

-   Use `---` to separate your slides.
-   Use standard Markdown syntax to format your content (e.g., `#` for headings, `*` for lists, etc.).

**Example:**

```markdown
---
marp: true
---

# Slide 1

This is the content of the first slide.

---

# Slide 2

This is the content of the second slide.
```

## Adding Images

You can add images to your slides using the standard Markdown image syntax.

-   **Local Images:** Place your images in the `presentations/assets` directory (you may need to create it) and reference them using a relative path.

    ```markdown
    ![My Image](./assets/my-image.png)
    ```

-   **Image Sizing:** You can control the size of your images using the `width` and `height` keywords.

    ```markdown
    ![w:200 h:150](./assets/my-image.png)
    ```

-   **Background Images:** You can set a background image for a slide using the `backgroundImage` directive.

    ```markdown
    ---
    backgroundImage: url('./assets/background.jpg')
    ---
    ```

## Styling Your Presentation

### Themes

Marp comes with a few built-in themes. You can set the theme for your presentation using the `theme` directive in the front-matter.

**Available Themes:** `default`, `gaia`, `uncover`

**Example:**

```yaml
---
marp: true
theme: gaia
---
```

### Custom Styling

You can add custom styles to your presentation using the `style` directive. This allows you to override the default theme styles with your own CSS.

**Example:**

```yaml
---
marp: true
style: |
  h1 {
    color: #ff0000;
  }
  section {
    background-color: #f0f0f0;
  }
---
```

You can also include an external stylesheet:

```yaml
---
marp: true
theme: default
stylesheet:
  - ./assets/custom-styles.css
---
```

## Building Your Presentation

To build your presentation, run the following command from the root of the monorepo:

```bash
make build-presentations
```

This will generate an HTML file for each Markdown file in the `presentations` directory. The output files will be placed in the `presentations/build` directory.

## Viewing Your Presentation

To view your presentation, open the generated HTML file in a web browser. For example:

```bash
open presentations/build/your-presentation-file.html
