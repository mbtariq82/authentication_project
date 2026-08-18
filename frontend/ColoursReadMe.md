# Frontend Colours

Use the shared colour tokens instead of adding new hardcoded colour values to components.

## CSS Components

For normal styling in `.css` files, use the CSS custom properties defined in `src/index.css`:

```css
.card {
  background: var(--color-white);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.error-message {
  background: var(--color-error-background);
  color: var(--color-error);
}
```

Available CSS variables include:

- `--color-primary`
- `--color-navy`
- `--color-background`
- `--color-white`
- `--color-text`
- `--color-muted`
- `--color-border`
- `--color-success` and `--color-success-background`
- `--color-warning` and `--color-warning-background`
- `--color-error` and `--color-error-background`
- `--color-info` and `--color-info-background`

## TypeScript Components

For charts or other TypeScript code that needs a colour value, import `colors` from `src/theme/colors.ts`:

```tsx
import { colors } from "../theme/colors";

const chartColours = [colors.primary, colors.success, colors.warning];
```

Use CSS variables for component styling. Use `colors.ts` when a library requires a JavaScript string, such as Recharts.

## Adding Colours

When a new shared colour is needed:

1. Add the token to `src/theme/colors.ts`.
2. Add the matching CSS variable to `src/index.css`.
3. Use the shared token where it is needed.
4. Avoid adding one-off hex values directly to components.

Keep the names semantic. Prefer `colors.error` or `var(--color-error)` over names based on appearance, such as `colors.red`.
