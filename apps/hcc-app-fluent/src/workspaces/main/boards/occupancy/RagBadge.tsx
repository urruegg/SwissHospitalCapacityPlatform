import type { ReactNode } from 'react';
import { Badge } from '@fluentui/react-components';
import { chipBadgeColor, type ChipTone } from '../../../../copilot-rail/reco';
import { ragColors } from '../../../../theme/curavias-theme';

/**
 * Sprint 27 — status/level badge that uses the brand RAG colours (the exact
 * Flag/Trend icon palette) for the primary over/watch/ok tones, so filled
 * badges match the icons. Non-RAG tones keep the Fluent semantic colour.
 * Text colour is fixed per background (white on red; dark on amber/green,
 * honouring the brand "dark text on green/amber" rule) and does not flip with
 * the theme, since the badge background is a fixed brand colour.
 */
const RAG: Partial<Record<ChipTone, { bg: string; fg: string }>> = {
  over: { bg: ragColors.bad, fg: '#F5F7F8' },
  watch: { bg: ragColors.neutral, fg: '#0E0F11' },
  ok: { bg: ragColors.good, fg: '#0E0F11' },
};

interface RagBadgeProps {
  tone: ChipTone;
  children: ReactNode;
}

export function RagBadge({ tone, children }: RagBadgeProps) {
  const rag = RAG[tone];
  if (rag) {
    return (
      <Badge appearance="filled" style={{ backgroundColor: rag.bg, color: rag.fg }}>
        {children}
      </Badge>
    );
  }
  return (
    <Badge appearance="filled" color={chipBadgeColor(tone)}>
      {children}
    </Badge>
  );
}
