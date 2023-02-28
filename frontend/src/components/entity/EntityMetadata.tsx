import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Tooltip, Link } from '@mui/material';
import { TypeEnum } from 'src/services/openapi';
import { RelatedEntityObject } from 'src/utils/types';

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
      date.getUTCMonth()
    )}-${toPaddedString(date.getUTCDay())}`;
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexWrap: 'wrap',
        alignContent: 'space-between',
        fontFamily: 'Poppins',
        fontSize: '0.8em',
        color: 'neutral.main',
        columnGap: '12px',
        lineHeight: '1.3',
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
            <Link
              color="inherit"
              component={RouterLink}
              to={`/recommendations?language=&uploader=${encodeURIComponent(
                uploader
              )}`}
            >
              {uploader}
            </Link>
          </Tooltip>
        ) : (
          uploader
        ))}
    </Box>
  );
};

const EntityMetadata = ({ entity }: { entity: RelatedEntityObject }) => {
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
