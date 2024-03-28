import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';

const projectsToUse = [
  {
    text: 'CaptainFact',
    href: 'https://captainfact.io',
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
    text: 'Tournesol',
    href: 'https://tournesol.app',
  },
  {
    text: 'Wikipedia',
    href: 'https://www.wikipedia.org',
  },
];

const booksToReadAndOfferEn = [
  {
    text: 'Against Empathy',
    href: 'https://www.harpercollins.com/products/against-empathy-paul-bloom',
    authors: 'Paul BLOOM',
  },
  {
    text: 'The Scout Mindset',
    href: 'https://www.penguinrandomhouse.com/books/555240/the-scout-mindset-by-julia-galef/',
    authors: 'Julia GALEF',
  },
];

const ProjectsToUse = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography>{t('actionsPage.volition.useToolsAndPlatforms')}</Typography>
      <ul>
        {projectsToUse.map((project, idx) => (
          <li key={`projects_to_promote_${idx}`}>
            <ExternalLink href={project.href}>{project.text}</ExternalLink>
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
          <Typography>{t('actionsPage.inEnglish')}</Typography>
          <ul>
            {booksToReadAndOfferEn.map((book, idx) => (
              <li key={`book_en_${idx}`}>
                <Box display="flex" flexWrap="wrap" columnGap={1}>
                  <ExternalLink href={book.href}>{book.text}</ExternalLink>
                  <Typography variant="body2">- {book.authors}</Typography>
                </Box>
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
    <Box>
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
            <ExternalLink href="https://tournesol.app/entities/yt:rE3j_RHkqJc">
              {'This Video Will Make You Angry'}
            </ExternalLink>
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
