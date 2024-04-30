import React from 'react';
import CSS from 'csstype';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Tooltip } from '@mui/material';

import { InternalLink } from 'src/components';
import { TypeEnum } from 'src/services/openapi';
import { EntityObject } from 'src/utils/types';

const toPaddedString = (num: number): string => {
  return num.toString().padStart(2, '0');
};

export const VideoMetadata = ({
  views,
  publicationDate,
  uploader,
  withLinks = true,
  flexWrap = 'wrap',
}: {
  views?: number | null;
  publicationDate?: string | null;
  uploader?: string | null;
  withLinks?: boolean;
  flexWrap?: CSS.Properties['flexWrap'];
}) => {
  const { t, i18n } = useTranslation();

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
        columnGap: '10px',
      }}
    >
      {views && (
        <Box component="span" flexShrink={0}>
          <Trans t={t} i18nKey="video.nbViews">
            {{
              nbViews: views.toLocaleString(i18n.resolvedLanguage),
            }}{' '}
            views
          </Trans>
        </Box>
      )}
      {publicationDate && (
        <Box component="span" flexShrink={0}>
          {displayedDate}
        </Box>
      )}

      {uploader && (
        <Box component="span" flexShrink={0}>
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
    </Box>
  );
};

const EntityMetadata = ({
  entity,
  flexWrap,
}: {
  entity: EntityObject;
  flexWrap?: CSS.Properties['flexWrap'];
}) => {
  if (entity.type === TypeEnum.VIDEO) {
    return (
      <VideoMetadata
        views={entity.metadata.views}
        publicationDate={entity.metadata.publication_date}
        uploader={entity.metadata.uploader}
        flexWrap={flexWrap}
      />
    );
  }
  return null;
};

export default EntityMetadata;
