import { curaviasLightTheme, curaviasDarkTheme } from '../../src/theme/curavias-theme';

describe('curavias theme', () => {
  it('sets brand primary and keeps dark text on the green fill', () => {
    expect(curaviasLightTheme.colorBrandBackground).toBe('#17B890');
    expect(curaviasLightTheme.colorNeutralForegroundOnBrand).toBe('#0E0F11');
  });

  it('provides a dark theme variant', () => {
    expect(curaviasDarkTheme.colorBrandBackground).toBe('#17B890');
    expect(curaviasDarkTheme.colorNeutralBackground1).not.toBe(curaviasLightTheme.colorNeutralBackground1);
  });
});
