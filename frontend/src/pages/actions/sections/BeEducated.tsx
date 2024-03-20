import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, Box, Link, Typography } from '@mui/material';

const booksToReadAndOfferEn = [
  {
    text: 'Manufacturing Consensus',
    href: 'https://yalebooks.yale.edu/book/9780300251234/manufacturing-consensus/',
  },
  {
    text: 'Twitter and Tear Gas',
    href: 'https://www.twitterandteargas.org/downloads/twitter-and-tear-gas-by-zeynep-tufekci.pdf',
  },
];

const booksToReadAndOfferFr = [
  {
    text: 'Algocratie',
    href: 'https://www.actes-sud.fr/algocratie',
  },
  {
    text: 'Le Fabuleux Chantier',
    href: 'https://laboutique.edpsciences.fr/produit/1107/9782759824304/Le%20fabuleux%20chantier',
  },
  {
    text: 'Toxic Data',
    href: 'https://editions.flammarion.com/toxic-data/9782080274946',
  },
];

const videosToWatchAndShareEn = [
  {
    text: 'Science4All (english)',
    href: 'https://tournesol.app/recommendations?language=&uploader=Science4All+%28english%29',
  },
];

const videosToWatchAndShareFr = [
  {
    text: 'Science4All',
    href: 'https://tournesol.app/recommendations?language=&uploader=Science4All',
  },
  {
    text: 'ApresLaBiere',
    href: 'https://tournesol.app/recommendations?language=&uploader=ApresLaBiere',
  },
  {
    text: 'La Fabrique Sociale',
    href: 'https://tournesol.app/recommendations?language=&uploader=La%20Fabrique%20Sociale',
  },
];

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

const BooksToReadAndOffer = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography>
        {t('actionsPage.beEducated.readAndOfferMoreBooksLike')}
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
        <li>
          <Typography>{t('actionsPage.beEducated.inFrench')}</Typography>
          <ul>
            {booksToReadAndOfferFr.map((book, idx) => (
              <li key={`book_fr_${idx}`}>
                <ExternalLink {...book} />
              </li>
            ))}
          </ul>
        </li>
      </ul>
    </>
  );
};

const VideosToWatchAndShare = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography>
        {t('actionsPage.beEducated.watchAndShareVideosFrom')}{' '}
      </Typography>
      <ul>
        <li>
          <Typography>{t('actionsPage.beEducated.inEnglish')}</Typography>
          <ul>
            {videosToWatchAndShareEn.map((videos, idx) => (
              <li key={`videos_en_${idx}`}>
                <ExternalLink {...videos} />
              </li>
            ))}
            <li>
              <Typography>{t('actionsPage.beEducated.andMore')}</Typography>
            </li>
          </ul>
        </li>
        <li>
          <Typography>{t('actionsPage.beEducated.inFrench')}</Typography>
          <ul>
            {videosToWatchAndShareFr.map((videos, idx) => (
              <li key={`videos_fr_${idx}`}>
                <ExternalLink {...videos} />
              </li>
            ))}
            <li>
              <Typography>{t('actionsPage.beEducated.andMore')}</Typography>
            </li>
          </ul>
        </li>
      </ul>
    </>
  );
};

const BeEducated = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="be-educated">
        {t('actionsPage.beEducated.beTrainedAndTrainOthers')}
      </Typography>
      <Box my={2}>
        <Alert severity="info" icon={false}>
          {t('actionsPage.beEducated.why')}
        </Alert>
      </Box>
      <ul>
        <li>
          <Typography>
            {t(
              'actionsPage.beEducated.readAndOfferBooksResultingFromAssociationWorks'
            )}{' '}
            <ExternalLink
              text="La Dictature des Algorithmes (fr)"
              href="https://www.tallandier.com/livre/la-dictature-des-algorithmes/"
            />
          </Typography>
        </li>
        <li>
          <BooksToReadAndOffer />
        </li>
        <li>
          <VideosToWatchAndShare />
        </li>
        <li>
          <Typography>
            {t('actionsPage.beEducated.listenAndSharePodcastsLike')}{' '}
            <ExternalLink
              text="Your Undivided Attention (en)"
              href="https://www.humanetech.com/podcast"
            />
          </Typography>
        </li>
        <li>
          <Typography>
            <Trans
              t={t}
              i18nKey="actionsPage.beEducated.discoverPlayAndShareEducationalGamesLike"
            >
              Discover, play and share educational games like{' '}
              <Link
                href="https://ncase.me/"
                target="_blank"
                rel="noopener"
                sx={{
                  color: 'revert',
                  textDecoration: 'revert',
                }}
              >
                Nicky Case&apos;s
              </Link>
              .
            </Trans>
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default BeEducated;
