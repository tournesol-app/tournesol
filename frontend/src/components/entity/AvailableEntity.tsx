import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Typography } from '@mui/material';
import { idFromUid } from '../../utils/video';
import { entityCardMainSx } from './style';
import { ActionList } from 'src/utils/types';
import { TypeEnum } from 'src/services/openapi';

/*
 * This component can be returned instead of <EntityCard> when the entity
 * doesn't seem to be available online at its original location.
 */
export const EntityNotAvailable = ({
  uid,
  type,
  unavailableActions,
}: {
  uid: string;
  type: string;
  unavailableActions?: ActionList;
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
            {unavailableActions &&
              unavailableActions.map((Action, index) =>
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
  unavailableActions,
}: {
  uid: string;
  type: string;
  children: React.ReactNode;
  unavailableActions?: ActionList;
}) => {
  const [isAvailable, setIsAvailable] = useState(false);

  /**
   * Check if the entity is available.
   *
   * The behaviour "is available" could be factorized in a custom hook.
   */
  useEffect(() => {
    if (type !== TypeEnum.VIDEO) {
      setIsAvailable(true);
    } else {
      const img = new Image();
      img.src = `https://i.ytimg.com/vi/${idFromUid(uid)}/mqdefault.jpg`;
      img.onload = function () {
        setIsAvailable(img.width !== 120);
      };
    }
  }, [uid, type]);

  return isAvailable ? (
    <>{children}</>
  ) : (
    <EntityNotAvailable
      uid={uid}
      type={type}
      unavailableActions={unavailableActions}
    />
  );
};

export default AvailableEntity;
