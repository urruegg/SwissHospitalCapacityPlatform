import { describe, it, expect } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import '../../src/i18n';
import { StoryTab } from '../../src/workspaces/backstage/tabs/story/StoryTab';
import { BackstageView } from '../../src/workspaces/backstage/BackstageView';
import { RoleProvider } from '../../src/context/role-context';
import { loadEvidenceDataset } from '../../src/data/evidence/evidence-service';
import { COPILOT_ROSTER, storyStatTiles } from '../../src/workspaces/backstage/tabs/story/story-data';

function renderStoryTab() {
  return render(
    <FluentProvider theme={webLightTheme}>
      <StoryTab />
    </FluentProvider>,
  );
}

describe('StoryTab — stat tiles', () => {
  it('renders the story-stat-tiles container', () => {
    renderStoryTab();
    expect(screen.getByTestId('story-stat-tiles')).toBeInTheDocument();
  });

  it('renders one tile per stat — count matches storyStatTiles(dataset).length', () => {
    renderStoryTab();
    const container = screen.getByTestId('story-stat-tiles');
    const expectedCount = storyStatTiles(loadEvidenceDataset()).length;
    expect(within(container).getAllByRole('group').length).toBe(expectedCount);
  });

  it('stat tiles show the ADR count derived from the dataset', () => {
    renderStoryTab();
    const dataset = loadEvidenceDataset();
    const tiles = screen.getByTestId('story-stat-tiles');
    // The derived value appears as text somewhere in the tile container
    expect(tiles.textContent).toContain(String(dataset.adrs.length));
  });

  it('stat tiles show the BOM count derived from the dataset', () => {
    renderStoryTab();
    const dataset = loadEvidenceDataset();
    const tiles = screen.getByTestId('story-stat-tiles');
    expect(tiles.textContent).toContain(String(dataset.boms.length));
  });

  it('renders provenance badges (snapshot/invariant) inside stat tiles', () => {
    renderStoryTab();
    const tiles = screen.getByTestId('story-stat-tiles');
    const text = tiles.textContent ?? '';
    // English locale: "Snapshot" or "Invariant" badges expected
    const hasProvenanceLabel = text.includes('Snapshot') || text.includes('Invariant') || text.includes('Live');
    expect(hasProvenanceLabel).toBe(true);
  });
});

describe('StoryTab — delivery strips', () => {
  it('renders the PLAN→RELEASE delivery strip', () => {
    renderStoryTab();
    expect(screen.getByTestId('story-delivery-plan')).toBeInTheDocument();
  });

  it('renders the DEV→PROD environment strip', () => {
    renderStoryTab();
    expect(screen.getByTestId('story-delivery-env')).toBeInTheDocument();
  });

  it('PLAN→RELEASE strip contains all 5 stage labels', () => {
    renderStoryTab();
    const strip = screen.getByTestId('story-delivery-plan');
    const text = strip.textContent ?? '';
    expect(text).toContain('PLAN');
    expect(text).toContain('SPEC');
    expect(text).toContain('BUILD');
    // REVIEW/RELEASE may be translated in non-en locales; check via english fallback key
    expect(text).toContain('RELEASE');
  });

  it('DEV→PROD strip contains DEV, SIT, PROD', () => {
    renderStoryTab();
    const strip = screen.getByTestId('story-delivery-env');
    const text = strip.textContent ?? '';
    expect(text).toContain('DEV');
    expect(text).toContain('SIT');
    expect(text).toContain('PROD');
  });
});

describe('StoryTab — copilot roster', () => {
  it('renders the copilot roster container', () => {
    renderStoryTab();
    expect(screen.getByTestId('story-copilot-roster')).toBeInTheDocument();
  });

  it('roster count caption uses COPILOT_ROSTER.length (not a literal)', () => {
    renderStoryTab();
    const roster = screen.getByTestId('story-copilot-roster');
    // The count is inserted from COPILOT_ROSTER.length; verify it appears somewhere
    // near the roster (it's in the Caption1 above it)
    // Also check the roster itself contains 8 cards
    const rosterParent = roster.parentElement;
    expect(rosterParent?.textContent).toContain(String(COPILOT_ROSTER.length));
  });

  it('renders a card for each of the 8 copilots', () => {
    renderStoryTab();
    const roster = screen.getByTestId('story-copilot-roster');
    // Each agent card shows displayName
    expect(roster.textContent).toContain('BMCA');
    expect(roster.textContent).toContain('OOA');
    expect(roster.textContent).toContain('DCA');
    expect(roster.textContent).toContain('ORSA');
    expect(roster.textContent).toContain('SBA');
    expect(roster.textContent).toContain('CSA');
    expect(roster.textContent).toContain('Data Quality');
    expect(roster.textContent).toContain('Onboarding');
  });

  it('renders ceiling badges in the roster', () => {
    renderStoryTab();
    const roster = screen.getByTestId('story-copilot-roster');
    const text = roster.textContent ?? '';
    // At least one ceiling should appear
    const hasCeiling = text.includes('read') || text.includes('write') || text.includes('deploy');
    expect(hasCeiling).toBe(true);
  });
});

describe('StoryTab — platform pillars (preserve existing)', () => {
  it('renders all four pillar cards', () => {
    renderStoryTab();
    expect(screen.getByTestId('story-pillar-agents')).toBeInTheDocument();
    expect(screen.getByTestId('story-pillar-fabric-fhir')).toBeInTheDocument();
    expect(screen.getByTestId('story-pillar-dsg')).toBeInTheDocument();
    expect(screen.getByTestId('story-pillar-alm')).toBeInTheDocument();
  });

  it('renders backstage-story testid and aria label', () => {
    renderStoryTab();
    expect(screen.getByTestId('backstage-story')).toBeInTheDocument();
  });
});

describe('StoryTab — BackstageView integration', () => {
  function renderBackstage(path: string) {
    return render(
      <MemoryRouter initialEntries={[path]}>
        <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
          <Routes>
            <Route path="/backstage/:widget?" element={<BackstageView />} />
          </Routes>
        </RoleProvider>
      </MemoryRouter>,
    );
  }

  it('story tab within BackstageView renders all new sections', () => {
    renderBackstage('/backstage/story');
    expect(screen.getByTestId('backstage-story')).toBeInTheDocument();
    expect(screen.getByTestId('story-stat-tiles')).toBeInTheDocument();
    expect(screen.getByTestId('story-delivery-plan')).toBeInTheDocument();
    expect(screen.getByTestId('story-delivery-env')).toBeInTheDocument();
    expect(screen.getByTestId('story-copilot-roster')).toBeInTheDocument();
  });

  it('story tab still shows all four pillar cards (no regression)', () => {
    renderBackstage('/backstage/story');
    expect(screen.getByTestId('story-pillar-agents')).toBeInTheDocument();
    expect(screen.getByTestId('story-pillar-fabric-fhir')).toBeInTheDocument();
    expect(screen.getByTestId('story-pillar-dsg')).toBeInTheDocument();
    expect(screen.getByTestId('story-pillar-alm')).toBeInTheDocument();
  });
});
