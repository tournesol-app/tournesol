import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Typography } from '@mui/material';

import LoaderWrapper from 'src/components/LoaderWrapper';
import { TypeEnum } from 'src/services/openapi';
import { ActionList } from 'src/utils/types';
import { idFromUid } from 'src/utils/video';
import { entityCardMainSx } from './style';

/*
 * This component can be returned instead of <EntityCard> when the entity
 * doesn't seem to be available online at its original location.
 */
export const EntityNotAvailable = ({
  uid,
  type,
  actionsIfUnavailable,
}: {
  uid: string;
  type: string;
  actionsIfUnavailable?: ActionList;
}) => {
  const { t } = useTranslation();

  if (type === TypeEnum.VIDEO) {
    return (
      <Box mx={1} my={2}>
        <Grid
          container
          justifyContent="space-between"
          alignItems="center"
          sx={entityCardMainSx}
        >
          <Grid item px={1} py={2}>
            <Typography>{t('video.notAvailableAnymore')}</Typography>
          </Grid>
          <Grid item>
            {actionsIfUnavailable &&
              actionsIfUnavailable.map((Action, index) =>
                typeof Action === 'function' ? (
                  <Action key={index} uid={uid} />
                ) : (
                  Action
                )
              )}
          </Grid>
        </Grid>
      </Box>
    );
  }

  return null;
};

/**
 * Return an <EntityNotAvailable> if the entity doesn't seem to be available
 * online at its original location, return the given children component
 * instead.
 */
const AvailableEntity = ({
  uid,
  type,
  children,
  actionsIfUnavailable,
}: {
  uid: string;
  type: string;
  children: React.ReactNode;
  actionsIfUnavailable?: ActionList;
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAvailable, setIsAvailable] = useState(false);

  /**
   * Check if the entity is available.
   *
   * The behaviour "is available" could be factorized in a custom hook.
   */
  useEffect(() => {
    if (type !== TypeEnum.VIDEO) {
      setIsLoading(false);
      setIsAvailable(true);
    } else {
      const img = new Image();
      img.src = `https://i.ytimg.com/vi/${idFromUid(uid)}/mqdefault.jpg`;
      img.onload = function () {
        setIsLoading(false);
        setIsAvailable(img.width !== 120);
      };
    }
  }, [uid, type]);

  return (
    <LoaderWrapper isLoading={isLoading}>
      {isAvailable ? (
        <>{children}</>
      ) : (
        <EntityNotAvailable
          uid={uid}
          type={type}
          actionsIfUnavailable={actionsIfUnavailable}
        />
      )}
    </LoaderWrapper>
  );
};

export default AvailableEntity;
