# /design — 5 add-ons (scraped)
## Installs
- npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
- npx skills add vercel-labs/agent-skills --skill web-design-guidelines
- git clone https://github.com/VoltAgent/awesome-design-md && cp awesome-design-md/design-md/stripe/DESIGN.md ./DESIGN.md
- git clone https://github.com/abi/screenshot-to-code (Docker, ANTHROPIC_API_KEY)
- npm install -g @playwright/cli@latest && playwright-cli install --skills
## Prompts
- "Redesign my landing page with the design-taste-frontend skill. Keep the copy, drop the purple gradient."
- "Review src/app/page.tsx with web-design-guidelines, then fix every issue you find."
- "Restyle the app following DESIGN.md: colors, type, spacing and components. Don't copy their logo or their copy."
- "Here's the code screenshot-to-code made from a section I like. Rebuild it as a component in my app with my colors, fonts and copy, so it looks like it was always mine."
- "Open localhost:3000 on a phone-sized screen with playwright-cli, take screenshots of every page, and fix anything cut off, overlapping or misaligned."
## Master prompt
Make my app look premium, step by step. After each step, show me a screenshot.
1. Use the design-taste-frontend skill to redesign the landing page: real photos, bold type, no purple gradients.
2. Review the result with web-design-guidelines and fix every issue.
3. Apply the style from ./DESIGN.md (colors, type, spacing, components).
4. If I give you a screenshot of a section I like, rebuild that section in my brand.
5. Open the app with playwright-cli at 390px and 1280px wide, screenshot every page, and fix anything cut off, overlapping or misaligned.
Keep my copy and features. Don't change logic, auth or payments.
