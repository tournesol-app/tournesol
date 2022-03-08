import React, { useState } from 'react';
import ReactPlayer from 'react-player/youtube';
import { Box } from '@mui/material';
import { TypeEnum } from 'src/services/openapi';
import { convertDurationToClockDuration } from 'src/utils/video';
import { RelatedEntityObject } from 'src/utils/types';

export const PlayerWrapper = React.forwardRef(function PlayerWrapper(
  {
    duration,
    children,
  }: {
    duration?: string;
    children: React.ReactNode;
  },
  ref
) {
  const [isDurationVisible, setIsDurationVisible] = useState(true);
  return (
    <Box
      position="relative"
      height="100%"
      onClick={() => setIsDurationVisible(false)}
      ref={ref}
    >
      {isDurationVisible && duration && (
        <Box
          position="absolute"
          bottom={0}
          right={0}
          bgcolor="rgba(0,0,0,0.5)"
          color="#fff"
          px={1}
          fontFamily="system-ui, arial, sans-serif"
          fontSize="0.8em"
          fontWeight="bold"
          sx={{ pointerEvents: 'none' }}
        >
          {duration}
        </Box>
      )}
      {children}
    </Box>
  );
});

const EntityImagery = ({ entity }: { entity: RelatedEntityObject }) => {
  if (entity.type === TypeEnum.VIDEO) {
    const duration = entity.metadata.duration;
    return (
      <ReactPlayer
        url={`https://youtube.com/watch?v=${entity.metadata.video_id}`}
        playing
        light
        width="100%"
        height="100%"
        wrapper={PlayerWrapper}
        duration={!!duration && convertDurationToClockDuration(duration)}
      />
    );
  }
  if (entity.type === TypeEnum.CANDIDATE_FR_2022) {
    return (
      <Box
        display="flex"
        maxHeight="280px"
        justifyContent="center"
        sx={{
          '& img': {
            flex: 1,
            objectFit: 'contain',
          },
        }}
      >
        <img src={entity.metadata.image_url} />
      </Box>
    );
  }
  return null;
};

export default EntityImagery;
