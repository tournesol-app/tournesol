import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';
import { getWebExtensionUrl } from 'src/utils/extension';

const booksToReadAndOfferEn = [
  {
    text: 'Feeling Good',
    href: 'https://feelinggood.com/books/',
    authors: 'David D. BURNS',
  },
  {
    text: 'The Righteous Mind',
    href: 'https://www.penguinrandomhouse.com/books/73535/the-righteous-mind-by-jonathan-haidt/',
    authors: 'Jonathan HAIDT',
  },
  {
    text: 'The Scout Mindset',
    href: 'https://www.penguinrandomhouse.com/books/555240/the-scout-mindset-by-julia-galef/',
    authors: 'Julia GALEF',
  },
];

const BooksToReadAndOffer = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography>
        {t('actionsPage.qualityInformation.readAndOfferBooksLike')}
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

const ExposureToQualityInformation = () => {
  const { t } = useTranslation();
  const browserExtensionUrl =
    getWebExtensionUrl() ?? getWebExtensionUrl('firefox');

  return (
    <Box>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="exposure-to-quality-information"
      >
        {t(
          'actionsPage.qualityInformation.increaseYourExposureToQualityInformation'
        )}
      </Typography>
      <ul>
        <li>
          <Typography>
            <Trans
              t={t}
              i18nKey="actionsPage.qualityInformation.installTournesol"
            >
              Install the{' '}
              <ExternalLink href={browserExtensionUrl}>
                Tournesol browser extension
              </ExternalLink>{' '}
              and the{' '}
              <ExternalLink href="https://tournesol.app">
                Tournesol mobile app
              </ExternalLink>{' '}
              (can be installed from your browser on Android).
            </Trans>
          </Typography>
        </li>
      </ul>
      <Typography variant="h6">
        {t('actionsPage.qualityInformation.improveUnderstandingOfPsychology')}
      </Typography>
      <ul>
        <li>
          <Typography>
            <Trans
              t={t}
              i18nKey="actionsPage.qualityInformation.watchShareVideos"
            >
              Watch and share videos on this topic, like{' '}
              <ExternalLink href="https://tournesol.app/entities/yt:WPPPFqsECz0">
                Dissatisfaction
              </ExternalLink>
              .
            </Trans>
          </Typography>
        </li>
        <li>
          <BooksToReadAndOffer />
        </li>
        <li>
          <Typography>
            <Trans
              t={t}
              i18nKey="actionsPage.qualityInformation.readAboutProcrastination"
            >
              Read the blog posts{' '}
              <ExternalLink href="https://waitbutwhy.com/2013/10/why-procrastinators-procrastinate.html">
                Why procrastinators procrastinate?
              </ExternalLink>
              , or watch the author&apos;s{' '}
              <ExternalLink href="https://tournesol.app/entities/yt:arj7oStGLkU">
                TED talk
              </ExternalLink>
              .
            </Trans>
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default ExposureToQualityInformation;
