import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';

const projectsToPromote = [
  {
    text: 'Algorithmic Personalization Project',
    href: 'https://personalization.csail.mit.edu',
  },
  {
    text: 'Horus',
    href: 'https://iscpif.fr/horus-methodologie/',
  },
  {
    text: 'Politoscope',
    href: 'https://politoscope.org',
  },
  {
    text: 'TheirTube',
    href: 'https://www.their.tube',
  },
  {
    text: 'Tournesol',
    href: 'https://tournesol.app',
  },
];

const ProjectsToPromote = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography>
        {t('actionsPage.helpResearch.promoteAndTakePartInResearchProjectsLike')}
      </Typography>
      <ul>
        {projectsToPromote.map((project, idx) => (
          <li key={`projects_to_promote_${idx}`}>
            <ExternalLink href={project.href}>{project.text}</ExternalLink>
          </li>
        ))}
      </ul>
    </>
  );
};

const HelpResearch = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="help-research"
      >
        {t(
          'actionsPage.helpResearch.helpScientificResearchThatServesPublicInterest'
        )}
      </Typography>
      <ul>
        <li>
          <ProjectsToPromote />
        </li>
        <li>
          <Trans t={t} i18nKey="actionsPage.helpResearch.attendTournesolTalks">
            Attend to{' '}
            <ExternalLink href="https://tournesol.app/talks">
              Tournesol Talks
            </ExternalLink>
            , or{' '}
            <ExternalLink href="mailto:talks@tournesol.app">
              ask to intervene
            </ExternalLink>
            .
          </Trans>
        </li>
      </ul>
    </Box>
  );
};

export default HelpResearch;
