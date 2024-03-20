import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';

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

const booksToReadAndOfferEn = [
  {
    text: 'The Scout Mindset',
    href: 'https://www.penguinrandomhouse.com/books/555240/the-scout-mindset-by-julia-galef/',
  },
  {
    text: 'Against Empathy',
    href: 'https://www.harpercollins.com/products/against-empathy-paul-bloom',
  },
];

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

const BooksToReadAndOffer = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography>
        {t('actionsPage.volition.readAndOfferBooksOnThisDistinction')}
      </Typography>
      <ul>
        <li>
          <Typography>{t('actionsPage.beEducated.inEnglish')}</Typography>
          <ul>
            {booksToReadAndOfferEn.map((book, idx) => (
              <li key={`book_en_${idx}`}>
                <ExternalLink {...book} />
              </li>
            ))}
          </ul>
        </li>
      </ul>
    </Box>
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
      <Box my={2}>
        <Alert severity="info" icon={false}>
          {t('actionsPage.volition.why')}
        </Alert>
      </Box>
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
        <li>
          <BooksToReadAndOffer />
        </li>
      </ul>
    </Box>
  );
};

export default Volition;
