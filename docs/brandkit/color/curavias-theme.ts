// Curavias — Fluent UI v9 theme. PRIMARY brand = Success Green #17B890; SECONDARY = Curavias Blue #365B7D.
import { BrandVariants, createLightTheme, createDarkTheme, Theme } from '@fluentui/react-components';

export const curaviasBrand: BrandVariants = {
  10: '#0B1D1D',
  20: '#0D332D',
  30: '#0F493E',
  40: '#10604E',
  50: '#12765F',
  60: '#148C6F',
  70: '#15A280',
  80: '#17B890',
  90: '#39C2A0',
  100: '#56CAAE',
  110: '#73D3BB',
  120: '#8FDBC9',
  130: '#AAE3D5',
  140: '#C5EBE2',
  150: '#E0F2EF',
  160: '#FAFAFB'
};          // #17B890 = brand[80]
export const curaviasSecondary = {"10": "#0E141B", "20": "#141E29", "30": "#1A2837", "40": "#1F3245", "50": "#253D53", "60": "#2B4761", "70": "#30516F", "80": "#365B7D", "90": "#537290", "100": "#6D87A0", "110": "#859BB0", "120": "#9EAFC0", "130": "#B5C2CF", "140": "#CCD5DE", "150": "#E3E8EC", "160": "#FAFAFB"};        // blue: nav/headers/white-text buttons

// Green #17B890 is bright -> white text on it FAILS WCAG AA. Use DARK text on green surfaces.
const brandFix: Partial<Theme> = {
  colorNeutralForegroundOnBrand: '#0E0F11',
  colorBrandForegroundLink: '#12765F',
  colorBrandForegroundLinkHover: '#10604E',
} as Partial<Theme>;

const statusLight: Partial<Theme> = {
  colorStatusSuccessForeground1: '#12765F', colorStatusSuccessBackground3: '#17B890', colorStatusSuccessBackground1: '#E0F2EF',
  colorStatusDangerForeground1: '#E62A35', colorStatusDangerBackground3: '#E30613', colorStatusDangerBackground1: '#F7DEE0',
  colorStatusWarningForeground1: '#EBAF25', colorStatusWarningBackground3: '#E8A200',
} as Partial<Theme>;

export const curaviasLightTheme: Theme = { ...createLightTheme(curaviasBrand), ...brandFix, ...statusLight };
export const curaviasDarkTheme:  Theme = { ...createDarkTheme(curaviasBrand) };
// <FluentProvider theme={curaviasLightTheme}><App/></FluentProvider>
