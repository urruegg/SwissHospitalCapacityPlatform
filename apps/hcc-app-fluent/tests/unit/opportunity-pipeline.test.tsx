import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import '../../src/i18n';
import { OpportunityPipelineView } from '../../src/workspaces/backstage/opportunity/OpportunityPipelineView';
import {
  getStatusCounts,
  getWeightedRoi,
  listOpportunities,
} from '../../src/data/opportunity/opportunity-service';

function renderPipeline() {
  return render(
    <FluentProvider theme={webLightTheme}>
      <OpportunityPipelineView />
    </FluentProvider>,
  );
}

describe('Opportunity pipeline Backstage view', () => {
  it('renders pipeline metrics and an opportunity row from the committed fixture', () => {
    renderPipeline();

    expect(screen.getByTestId('opportunity-status-won')).toHaveTextContent('1');
    expect(screen.getByTestId('opportunity-status-onboarding')).toHaveTextContent('1');
    expect(screen.getByTestId('opportunity-weighted-roi')).toHaveTextContent('35.93%');
    expect(screen.getByRole('cell', { name: 'CuraNova University Hospital' })).toBeInTheDocument();
    expect(screen.getByRole('cell', { name: 'commercial approval recorded' })).toBeInTheDocument();
  });

  it('service exposes deterministic status counts and weighted ROI', () => {
    expect(getStatusCounts()).toEqual({
      new: 1,
      evaluating: 1,
      qualified: 1,
      onboarding: 1,
      won: 1,
      disqualified: 1,
      lost: 1,
    });
    expect(getWeightedRoi()).toBe(35.93);
    expect(listOpportunities()).toHaveLength(7);
  });
});
