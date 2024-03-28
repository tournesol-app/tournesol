import React from 'react';
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
}: {
  views?: number | null;
  publicationDate?: string | null;
  uploader?: string | null;
  withLinks?: boolean;
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
        flexWrap: 'wrap',
        alignContent: 'space-between',
        fontSize: '0.8rem',
        color: 'neutral.main',
        columnGap: '12px',
        marginTop: '4px',
      }}
    >
      {views && (
        <Box component="span">
          <Trans t={t} i18nKey="video.nbViews">
            {{
              nbViews: views.toLocaleString(i18n.resolvedLanguage),
            }}{' '}
            views
          </Trans>
        </Box>
      )}
      {publicationDate && <Box component="span">{displayedDate}</Box>}

      {uploader &&
        (withLinks ? (
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
        ))}
    </Box>
  );
};

const EntityMetadata = ({ entity }: { entity: EntityObject }) => {
  if (entity.type === TypeEnum.VIDEO) {
    return (
      <VideoMetadata
        views={entity.metadata.views}
        publicationDate={entity.metadata.publication_date}
        uploader={entity.metadata.uploader}
      />
    );
  }
  return null;
};

export default EntityMetadata;
