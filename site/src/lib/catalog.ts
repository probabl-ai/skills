import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

export interface CatalogSkill {
  id: string;
  title: string;
  summary: string;
  category: string;
}

export interface CatalogWorkflow {
  id: string;
  title: string;
  summary: string;
  includes: string[];
}

interface CatalogFile {
  skills: CatalogSkill[];
  workflows: CatalogWorkflow[];
}

const DEPRECATED_IDS = new Set([
  'organize-ml-workspace',
  'data-science-python-stack',
]);

export const FULL_COMPANION_ID = 'ml-experimentation';

export const SKILL_GROUPS = [
  { category: 'methodology', label: 'Methodology' },
  { category: 'action', label: 'Modeling actions' },
  { category: 'meta', label: 'Session and backlog' },
  { category: 'tooling', label: 'Workspace and tooling' },
] as const;

export function loadCatalog(): CatalogFile {
  const catalogPath = resolve(process.cwd(), '../.catalog.json');
  return JSON.parse(readFileSync(catalogPath, 'utf8')) as CatalogFile;
}

export function activeSkillGroups(catalog: CatalogFile) {
  return SKILL_GROUPS.map((group) => ({
    ...group,
    skills: catalog.skills.filter(
      (skill) => skill.category === group.category && !DEPRECATED_IDS.has(skill.id),
    ),
  })).filter((group) => group.skills.length > 0);
}

export function deprecatedSkills(catalog: CatalogFile): CatalogSkill[] {
  return catalog.skills.filter((skill) => DEPRECATED_IDS.has(skill.id));
}
