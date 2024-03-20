import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Link, Typography } from '@mui/material';

const projectsToUse = [
  {
    text: 'Wikipedia',
    href: 'https://www.wikipedia.org',
  },
  {
    text: 'Community Notes',
    href: 'https://twitter.com/i/birdwatch',
  },
  {
    text: 'Polis',
    href: 'https://pol.is/home',
  },
  {
    text: 'Captain Fact',
    href: 'https://captainfact.io',
  },
  {
    text: 'Tournesol',
    href: 'https://tournesol.app',
  },
];

// XXX duplciated code with BeEducated.tsx
const ExternalLink = ({ text, href }: { text: string; href: string }) => {
  return (
    <Link
      href={href}
      target="_blank"
      rel="noopener"
      sx={{
        color: 'revert',
        textDecoration: 'revert',
      }}
    >
      {text}
    </Link>
  );
};

const ProjectsToUse = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography>
        {t('actionsPage.volition.useAndParticipateInPlatforms')}
      </Typography>
      <ul>
        {projectsToUse.map((project, idx) => (
          <li key={`projects_to_promote_${idx}`}>
            <ExternalLink {...project} />
          </li>
        ))}
      </ul>
    </>
  );
};

const Volition = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="volition">
        {t(
          'actionsPage.volition.favourThoughtfulVolitionsToInstinctivePreferences'
        )}
      </Typography>
      <ul>
        <li>
          <Typography>
            {t('actionsPage.volition.preventYourselfFromCompulsivePosting')}
          </Typography>
        </li>
        <li>
          <ProjectsToUse />
        </li>
        <li>
          <Typography>
            {t('actionsPage.volition.watchAndShareVideosOnThisDistinctionLike')}{' '}
            <ExternalLink
              text="This Video Will Make You Angry"
              href="https://tournesol.app/entities/yt:rE3j_RHkqJc"
            />
            .
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default Volition;
