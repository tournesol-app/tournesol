import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Typography } from '@mui/material';

import LoaderWrapper from 'src/components/LoaderWrapper';
import { ActionList } from 'src/utils/types';
import { entityCardMainSx } from './style';
import useIsAvailable from '../../hooks/useIsAvailable';

/*
 * This component can be returned instead of <EntityCard> when the entity
 * doesn't seem to be available online at its original location.
 */
export const EntityNotAvailable = ({
  uid,
  actionsIfUnavailable,
}: {
  uid: string;
  actionsIfUnavailable?: ActionList;
}) => {
  const { t } = useTranslation();

  if (uid.indexOf('yt:') !== -1) {
    return (
      <Box mx={1} my={2}>
        <Grid
          container
          justifyContent="space-between"
          alignItems="center"
          sx={entityCardMainSx}
        >
          <Grid item pl={1} py={2}>
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
  children,
  actionsIfUnavailable,
}: {
  uid: string;
  children: React.ReactNode;
  actionsIfUnavailable?: ActionList;
}) => {
  const { entityIsChecking, entityIsAvailable } = useIsAvailable(uid);

  return (
    <LoaderWrapper isLoading={entityIsChecking}>
      {entityIsAvailable ? (
        <>{children}</>
      ) : (
        <EntityNotAvailable
          uid={uid}
          actionsIfUnavailable={actionsIfUnavailable}
        />
      )}
    </LoaderWrapper>
  );
};

export default AvailableEntity;
