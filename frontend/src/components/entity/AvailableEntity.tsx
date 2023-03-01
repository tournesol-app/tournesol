import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Typography } from '@mui/material';
import { idFromUid } from '../../utils/video';
import { entityCardMainSx } from './style';
import { ActionList } from 'src/utils/types';
import { TypeEnum } from 'src/services/openapi';

/*
 * return a different error element related to the type of the entity and actions
 */
export const EntityNotAvailable = ({
  type,
  unavailableActions,
  uid,
}: {
  type: string;
  unavailableActions?: ActionList;
  uid: string;
}) => {
  const { t } = useTranslation();

  if (type == TypeEnum.VIDEO) {
    return (
      <Box mx={1} my={2}>
        <Grid
          mx={1}
          my={2}
          container
          sx={entityCardMainSx}
          justifyContent="space-between"
          alignItems="center"
        >
          <Grid ml={1} my={2}>
            <Typography>{t('video.notAvailableAnymore')}</Typography>
          </Grid>
          <Grid>
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

/*
 * Check if an entity is available
 * It returns children if it is available either it returns an error element
 */
const AvailableEntity = ({
  children,
  uid,
  type,
  unavailableActions,
}: {
  children: React.ReactNode;
  uid: string;
  type: string;
  unavailableActions?: ActionList;
}) => {
  const [isAvailable, setIsAvailable] = useState(false);

  useEffect(() => {
    if (type != 'video') {
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
      type={type}
      unavailableActions={unavailableActions}
      uid={uid}
    />
  );
};

export default AvailableEntity;
