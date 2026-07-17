import { curaviasLightTheme, curaviasDarkTheme, ragColors } from '../../src/theme/curavias-theme';

describe('curavias theme', () => {
  it('sets brand primary and keeps dark text on the green fill', () => {
    expect(curaviasLightTheme.colorBrandBackground).toBe('#17B890');
    expect(curaviasLightTheme.colorNeutralForegroundOnBrand).toBe('#0E0F11');
  });

  it('provides a dark theme variant', () => {
    expect(curaviasDarkTheme.colorBrandBackground).toBe('#17B890');
    expect(curaviasDarkTheme.colorNeutralBackground1).not.toBe(curaviasLightTheme.colorNeutralBackground1);
  });

  it('exposes Curavias RAG accents for cards', () => {
    expect(ragColors.good).toBe('#17B890');
    expect(ragColors.neutral).toBe('#E8A200');
    expect(ragColors.bad).toBe('#E30613');
  });
});
