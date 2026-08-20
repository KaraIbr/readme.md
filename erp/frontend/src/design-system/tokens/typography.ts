export const typography = {
  fontFamily: "'Manrope', system-ui, sans-serif",

  fontSize: {
    xs:   '0.75rem',
    sm:   '0.8125rem',
    base: '0.875rem',
    md:   '0.9375rem',
    lg:   '1rem',
    xl:   '1.125rem',
    '2xl': '1.25rem',
    '3xl': '1.5rem',
    '4xl': '2rem',
    '5xl': '2.5rem',
  },

  fontWeight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },

  lineHeight: {
    tight: '1.2',
    normal: '1.5',
    relaxed: '1.75',
  },

  letterSpacing: {
    tight: '-0.02em',
    normal: '0em',
    wide: '0.02em',
  },
} as const
