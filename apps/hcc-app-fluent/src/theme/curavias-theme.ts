import {
  createLightTheme,
  createDarkTheme,
  type BrandVariants,
  type Theme,
} from '@fluentui/react-components';
import tokens from './curavias-tokens.json';

const curaviasBrand: BrandVariants = {
  10: tokens.brand['10'],
  20: tokens.brand['10'],
  30: tokens.brand['20'],
  40: tokens.brand['20'],
  50: tokens.brand['40'],
  60: tokens.brand['40'],
  70: tokens.brand['60'],
  80: tokens.brand['80'],
  90: tokens.brand['80'],
  100: tokens.brand['80'],
  110: tokens.brand['80'],
  120: tokens.brand['100'],
  130: tokens.brand['100'],
  140: tokens.brand['100'],
  150: tokens.brand['100'],
  160: tokens.brand['100'],
};

export const curaviasLightTheme: Theme = {
  ...createLightTheme(curaviasBrand),
  colorBrandBackground: tokens.brand['80'],
  colorNeutralForegroundOnBrand: tokens.text.onLight,
};

export const curaviasDarkTheme: Theme = {
  ...createDarkTheme(curaviasBrand),
  colorBrandBackground: tokens.brand['80'],
  colorNeutralForegroundOnBrand: tokens.text.onLight,
};
