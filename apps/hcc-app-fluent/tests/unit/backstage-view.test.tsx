import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import '../../src/i18n';
import { BackstageView } from '../../src/workspaces/backstage/BackstageView';
import { RoleProvider } from '../../src/context/role-context';

describe('BackstageView', () => {
  it('defaults to the evidence widget', () => {
    render(
      <MemoryRouter initialEntries={['/backstage']}>
        <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
          <Routes>
            <Route path="/backstage/:widget?" element={<BackstageView />} />
          </Routes>
        </RoleProvider>
      </MemoryRouter>,
    );
    expect(screen.getByTestId('widget-evidence')).toBeInTheDocument();
  });

  it('renders the story widget with all four pillars', () => {
    render(
      <MemoryRouter initialEntries={['/backstage/story']}>
        <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
          <Routes>
            <Route path="/backstage/:widget?" element={<BackstageView />} />
          </Routes>
        </RoleProvider>
      </MemoryRouter>,
    );

    expect(screen.getByTestId('widget-story')).toBeInTheDocument();
    expect(screen.getByTestId('backstage-story')).toBeInTheDocument();
    expect(screen.getByTestId('story-pillar-agents')).toBeInTheDocument();
    expect(screen.getByTestId('story-pillar-fabric-fhir')).toBeInTheDocument();
    expect(screen.getByTestId('story-pillar-dsg')).toBeInTheDocument();
    expect(screen.getByTestId('story-pillar-alm')).toBeInTheDocument();
  });

  it('renders backstage sub-navigation with a story link on the default evidence widget', () => {
    render(
      <MemoryRouter initialEntries={['/backstage']}>
        <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
          <Routes>
            <Route path="/backstage/:widget?" element={<BackstageView />} />
          </Routes>
        </RoleProvider>
      </MemoryRouter>,
    );

    expect(screen.getByTestId('widget-evidence')).toBeInTheDocument();
    const storyLink = screen.getByTestId('backstage-nav-story');
    expect(storyLink).toHaveAttribute('href', '/backstage/story');
  });
});
