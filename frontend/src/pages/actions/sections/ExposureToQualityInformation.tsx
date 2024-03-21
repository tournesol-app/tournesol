import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Box, Link, Typography } from '@mui/material';
import { getWebExtensionUrl } from 'src/utils/extension';

const ExposureToQualityInformation = () => {
  const { t } = useTranslation();
  const browserExtensionUrl =
    getWebExtensionUrl() ?? getWebExtensionUrl('firefox');

  return (
    <Box
      sx={{
        '& a': { color: 'revert', textDecoration: 'revert' },
      }}
    >
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
              <Link href={browserExtensionUrl} target="_blank" rel="noopener">
                Tournesol browser extension
              </Link>{' '}
              and the{' '}
              <Link href="https://tournesol.app" target="_blank" rel="noopener">
                Tournesol mobile app
              </Link>{' '}
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
              <Link
                href={'https://tournesol.app/entities/yt:WPPPFqsECz0'}
                target="_blank"
                rel="noopener"
              >
                Dissatisfaction
              </Link>
            </Trans>
          </Typography>
        </li>
        <li>
          <Typography>
            <Trans
              t={t}
              i18nKey="actionsPage.qualityInformation.readOfferBooks"
            >
              Read and offer books, like{' '}
              <Link
                href={
                  'https://www.penguinrandomhouse.com/books/73535/the-righteous-mind-by-jonathan-haidt/'
                }
                target="_blank"
                rel="noopener"
              >
                The Righteous Mind
              </Link>
              ,{' '}
              <Link
                href={'https://feelinggood.com/books/'}
                target="_blank"
                rel="noopener"
              >
                Feeling Good
              </Link>
              ,{' '}
              <Link
                href={
                  'https://www.penguinrandomhouse.com/books/555240/the-scout-mindset-by-julia-galef/'
                }
                target="_blank"
                rel="noopener"
              >
                The Scout Mindset
              </Link>
              .
            </Trans>
          </Typography>
        </li>
        <li>
          <Typography>
            <Trans
              t={t}
              i18nKey="actionsPage.qualityInformation.readAboutProcrastination"
            >
              Read blog post{' '}
              <Link
                href={
                  'https://waitbutwhy.com/2013/10/why-procrastinators-procrastinate.html'
                }
                target="_blank"
                rel="noopener"
              >
                Why procrastinators procrastinate?
              </Link>
              , or watch the author&apos;s{' '}
              <Link
                href={'https://tournesol.app/entities/yt:arj7oStGLkU'}
                target="_blank"
                rel="noopener"
              >
                TED talk
              </Link>
              .
            </Trans>
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default ExposureToQualityInformation;
