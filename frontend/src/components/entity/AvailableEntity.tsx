import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid } from '@mui/material';
import { idFromUid } from '../../utils/video';
import { entityCardMainSx } from './style';

export const EntityNotAvailable = ({ type }: { type: string }) => {
  const { t } = useTranslation();

  if (type == 'video') {
    return (
      <Box mx={1} my={2}>
        <Grid container sx={entityCardMainSx}>
          <Box mx={1} my={2}>
            {t('video.notAvailableAnymore')}
          </Box>
        </Grid>
      </Box>
    );
  }

  return null;
};

const AvailableEntity = ({
  children,
  uid,
  type,
}: {
  children: React.ReactNode;
  uid: string;
  type: string;
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

  return isAvailable ? <>{children}</> : <EntityNotAvailable type={type} />;
};

export default AvailableEntity;
