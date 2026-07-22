export interface StoryPillar {
  key: string;
  titleKey: string;
  bodyKey: string;
}

export const STORY_PILLARS: StoryPillar[] = [
  { key: 'agents', titleKey: 'backstage.story.agents.title', bodyKey: 'backstage.story.agents.body' },
  { key: 'fabric-fhir', titleKey: 'backstage.story.fabricFhir.title', bodyKey: 'backstage.story.fabricFhir.body' },
  { key: 'dsg', titleKey: 'backstage.story.dsg.title', bodyKey: 'backstage.story.dsg.body' },
  { key: 'alm', titleKey: 'backstage.story.alm.title', bodyKey: 'backstage.story.alm.body' },
];
