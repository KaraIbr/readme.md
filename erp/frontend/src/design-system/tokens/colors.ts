export const colors = {
  primary: '#0F9F5F',
  primaryHover: '#0D8A52',
  primarySoft: '#E8F8F0',

  warning: '#FF9F00',
  warningHover: '#E68F00',
  warningSoft: '#FFF5E6',

  info: '#32A2FF',
  infoHover: '#2B8FE0',
  infoSoft: '#EBF5FF',

  danger: '#F94B60',
  dangerHover: '#E04356',
  dangerSoft: '#FFEDEF',

  text: '#212121',
  textSecondary: '#616161',
  textTertiary: '#9E9E9E',

  white: '#FFFFFF',

  neutral: {
    25:  '#FAFAFA',
    50:  '#F5F5F5',
    100: '#EEEEEE',
    200: '#E0E0E0',
    300: '#BDBDBD',
    400: '#9E9E9E',
    500: '#757575',
    600: '#616161',
    700: '#424242',
    800: '#303030',
    900: '#212121',
  },

  border: '#E0E0E0',
  borderLight: '#EEEEEE',
  surface: '#FFFFFF',
  surfaceSecondary: '#FAFAFA',
  backdrop: 'rgba(0, 0, 0, 0.4)',
} as const

export type ColorToken = keyof typeof colors
