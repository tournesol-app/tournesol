import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Tooltip } from '@mui/material';

import { InternalLink } from 'src/components';
import { TypeEnum } from 'src/services/openapi';
import { EntityObject } from 'src/utils/types';

export type EntityMetadataVariant = 'uploaderOnly' | 'wrap';

const toPaddedString = (num: number): string => {
  return num.toString().padStart(2, '0');
};

export const VideoMetadata = ({
  views,
  publicationDate,
  uploader,
  withLinks = true,
  variant = 'wrap',
}: {
  views?: number | null;
  publicationDate?: string | null;
  uploader?: string | null;
  withLinks?: boolean;
  variant?: EntityMetadataVariant;
}) => {
  const { t, i18n } = useTranslation();

  const flexWrap = variant === 'wrap' ? 'wrap' : 'nowrap';
  const flexShrink = variant === 'wrap' ? 1 : 0;

  let displayedDate;
  // Instead of displaying the date in the same format for every user, we
  // could choose to display date.toLocaleDateString(i18n.resolvedLanguage)
  // instead. See:
  //
  //    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toLocaleDateString
  if (publicationDate) {
    const date = new Date(publicationDate);
    displayedDate = `${date.getUTCFullYear()}-${toPaddedString(
      date.getUTCMonth() + 1
    )}-${toPaddedString(date.getUTCDate())}`;
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexWrap: flexWrap,
        alignContent: 'space-between',
        fontSize: '0.8rem',
        color: 'neutral.main',
        columnGap: '12px',
      }}
    >
      {uploader && (
        <Box component="span" flexShrink={flexShrink}>
          {withLinks ? (
            <Tooltip
              title={`${t('video.seeRecommendedVideosSameUploader')}`}
              placement="bottom"
            >
              <InternalLink
                to={`/recommendations?language=&uploader=${encodeURIComponent(
                  uploader
                )}`}
                color="inherit"
                underline="always"
                sx={{
                  fontWeight: 600,
                }}
              >
                {uploader}
              </InternalLink>
            </Tooltip>
          ) : (
            uploader
          )}
        </Box>
      )}
      {variant === 'wrap' && publicationDate && (
        <Box component="span" flexShrink={flexShrink}>
          {displayedDate}
        </Box>
      )}
      {variant === 'wrap' && views && (
        <Box component="span" flexShrink={flexShrink}>
          <Trans t={t} i18nKey="video.nbViews">
            {{
              nbViews: Intl.NumberFormat(i18n.resolvedLanguage, {
                notation: 'compact',
              }).format(views),
            }}{' '}
            views
          </Trans>
        </Box>
      )}
    </Box>
  );
};

const EntityMetadata = ({
  entity,
  variant = 'wrap',
}: {
  entity: EntityObject;
  variant?: EntityMetadataVariant;
}) => {
  if (entity.type === TypeEnum.VIDEO) {
    return (
      <VideoMetadata
        views={entity.metadata.views}
        publicationDate={entity.metadata.publication_date}
        uploader={entity.metadata.uploader}
        variant={variant}
      />
    );
  }
  return null;
};

export default EntityMetadata;
