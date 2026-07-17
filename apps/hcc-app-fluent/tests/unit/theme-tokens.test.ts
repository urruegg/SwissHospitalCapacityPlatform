import tokens from '../../src/theme/curavias-tokens.json';

describe('curavias tokens', () => {
  it('exposes the brand and secondary ramps and semantic roles', () => {
    expect(tokens.brand['80']).toBe('#17B890');
    expect(tokens.brandSecondary['80']).toBe('#365B7D');
    expect(tokens.danger['80']).toBe('#E30613');
    expect(tokens.text.onLight).toBe('#0E0F11');
  });
});
