import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';
import {
  AutoStories,
  ImportContacts,
  Podcasts,
  VideogameAsset,
  YouTube,
} from '@mui/icons-material';

import { ExternalLink } from 'src/components';

const booksToReadAndOfferEn = [
  {
    text: 'Manufacturing Consensus',
    href: 'https://yalebooks.yale.edu/book/9780300251234/manufacturing-consensus/',
    authors: 'Samuel WOOLLEY',
  },
  {
    text: 'Twitter and Tear Gas',
    href: 'https://www.twitterandteargas.org/downloads/twitter-and-tear-gas-by-zeynep-tufekci.pdf',
    authors: 'Zeynep TÜFEKÇI',
  },
  {
    text: 'Weapons of Math Destruction',
    href: 'https://www.penguinrandomhouse.com/books/241363/weapons-of-math-destruction-by-cathy-oneil/',
    authors: "Cathy O'NEIL",
  },
];

const booksToReadAndOfferFr = [
  {
    text: 'Algocratie',
    href: 'https://www.actes-sud.fr/algocratie',
    authors: 'Arthur GRIMONPONT',
  },
  {
    text: 'Algorithmes : la bombe à retardement',
    href: 'https://arenes.fr/livre/algorithmes-la-bombe-a-retardement/',
    authors: "Cathy O'NEIL",
  },
  {
    text: 'Le Fabuleux Chantier',
    href: 'https://laboutique.edpsciences.fr/produit/1107/9782759824304/Le%20fabuleux%20chantier',
    authors: 'Lê Nguyên HOANG, El Mahdi EL MHAMDI',
  },
  {
    text: 'Toxic Data',
    href: 'https://editions.flammarion.com/toxic-data/9782080274946',
    authors: 'David CHAVALARIAS',
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
    text: 'ApresLaBiere',
    href: 'https://tournesol.app/recommendations?language=&uploader=ApresLaBiere',
  },
  {
    text: 'La Fabrique Sociale',
    href: 'https://tournesol.app/recommendations?language=&uploader=La%20Fabrique%20Sociale',
  },
  {
    text: 'Science4All',
    href: 'https://tournesol.app/recommendations?language=&uploader=Science4All',
  },
];

const BooksToReadAndOffer = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Box display="flex" gap={2}>
        <AutoStories />
        <Typography>
          {t('actionsPage.beEducated.readAndOfferMoreBooksLike')}
        </Typography>
      </Box>
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
        <li>
          <Typography>{t('actionsPage.inFrench')}</Typography>
          <ul>
            {booksToReadAndOfferFr.map((book, idx) => (
              <li key={`book_fr_${idx}`}>
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

const VideosToWatchAndShare = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Box display="flex" gap={2}>
        <YouTube />
        <Typography>
          {t('actionsPage.beEducated.watchAndShareVideosFrom')}{' '}
        </Typography>
      </Box>
      <ul>
        <li>
          <Typography>{t('actionsPage.inEnglish')}</Typography>
          <ul>
            {videosToWatchAndShareEn.map((videos, idx) => (
              <li key={`videos_en_${idx}`}>
                <ExternalLink href={videos.href}>{videos.text}</ExternalLink>
              </li>
            ))}
            <li>
              <Typography>{t('actionsPage.beEducated.andMore')}</Typography>
            </li>
          </ul>
        </li>
        <li>
          <Typography>{t('actionsPage.inFrench')}</Typography>
          <ul>
            {videosToWatchAndShareFr.map((videos, idx) => (
              <li key={`videos_fr_${idx}`}>
                <ExternalLink href={videos.href}>{videos.text}</ExternalLink>
              </li>
            ))}
            <li>
              <Typography>{t('actionsPage.beEducated.andMore')}</Typography>
            </li>
          </ul>
        </li>
      </ul>
    </Box>
  );
};

const BeEducated = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="be-educated">
        {t('actionsPage.beEducated.beTrainedAndTrainOthers')}
      </Typography>
      <Box my={2}>
        <Alert severity="info" icon={false}>
          {t('actionsPage.beEducated.why')}
        </Alert>
      </Box>
      <Box display="flex" flexDirection="column" gap={2} mt={2}>
        <Box display="flex" gap={2}>
          <ImportContacts />
          <Typography paragraph>
            {t(
              'actionsPage.beEducated.readAndOfferBooksResultingFromAssociationWorks'
            )}{' '}
            <ExternalLink href="https://www.tallandier.com/livre/la-dictature-des-algorithmes/">
              {'La Dictature des Algorithmes (fr)'}
            </ExternalLink>
            .
          </Typography>
        </Box>
        <BooksToReadAndOffer />
        <VideosToWatchAndShare />
        <Box display="flex" gap={2}>
          <Podcasts />
          <Typography>
            {t('actionsPage.beEducated.listenAndSharePodcastsLike')}{' '}
            <ExternalLink href="https://www.humanetech.com/podcast">
              {'Your Undivided Attention (en)'}
            </ExternalLink>
            .
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <VideogameAsset />
          <Typography>
            <Trans
              t={t}
              i18nKey="actionsPage.beEducated.discoverAndShareEducationalGamesLike"
            >
              Discover and share educational games like{' '}
              <ExternalLink href="https://ncase.me/">
                Nicky Case&apos;s
              </ExternalLink>
              .
            </Trans>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default BeEducated;
