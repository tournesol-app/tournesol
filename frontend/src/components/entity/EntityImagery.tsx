import React, { useState } from 'react';
import ReactPlayer from 'react-player/youtube';

import { Avatar, Box, useTheme } from '@mui/material';

import { InternalLink } from 'src/components';
import { useCurrentPoll } from 'src/hooks';
import { TypeEnum } from 'src/services/openapi';
import { JSONValue, EntityObject } from 'src/utils/types';
import { convertDurationToClockDuration, idFromUid } from 'src/utils/video';

export const DurationWrapper = React.forwardRef(function DurationWrapper(
  {
    duration,
    children,
  }: {
    duration?: number;
    children: React.ReactNode;
  },
  ref
) {
  const theme = useTheme();
  const [isDurationVisible, setIsDurationVisible] = useState(true);
  const formattedDuration: string | null = duration
    ? convertDurationToClockDuration(duration)
    : null;

  return (
    <Box
      position="relative"
      height="100%"
      width="100%"
      onClick={() => setIsDurationVisible(false)}
      ref={ref}
    >
      {isDurationVisible && formattedDuration && (
        <Box
          position="absolute"
          bottom={0}
          right={0}
          color="#fff"
          bgcolor="rgba(0,0,0,0.5)"
          px={1}
          fontFamily="system-ui, arial, sans-serif"
          fontSize="0.8rem"
          fontWeight="bold"
          lineHeight={1.5}
          // Prevent the duration to be hidden by an additional layer
          // displayed on top of it (like the unavailable box).
          zIndex={theme.zIndex.videoCardDuration}
          sx={{ pointerEvents: 'none' }}
        >
          {formattedDuration}
        </Box>
      )}
      {children}
    </Box>
  );
});

export const VideoPlayer = ({
  videoId,
  duration,
  controls = true,
}: {
  videoId: string;
  duration?: number | null;
  controls?: boolean;
}) => {
  return (
    <ReactPlayer
      url={`https://youtube.com/watch?v=${videoId}`}
      playing
      light
      width="100%"
      height="100%"
      wrapper={DurationWrapper}
      duration={duration}
      controls={controls}
    />
  );
};

const EntityImagery = ({
  entity,
  compact = false,
  config = {},
}: {
  entity: EntityObject;
  compact?: boolean;
  config?: { [k in TypeEnum]?: { [k: string]: JSONValue } };
}) => {
  const { baseUrl } = useCurrentPoll();
  const videoConfig = config[TypeEnum.VIDEO] ?? {};

  if (entity.type === TypeEnum.VIDEO) {
    if (videoConfig.displayPlayer ?? true) {
      return (
        <Box
          sx={{
            aspectRatio: '16 / 9',
            width: '100%',
          }}
        >
          <VideoPlayer
            videoId={entity.metadata.video_id}
            duration={entity.metadata.duration}
          />
        </Box>
      );
    }

    const thumbnail = (
      <DurationWrapper duration={entity.metadata.duration}>
        <img
          className="full-width entity-thumbnail"
          src={`https://i.ytimg.com/vi/${idFromUid(entity.uid)}/mqdefault.jpg`}
          alt={entity.metadata.name}
        />
      </DurationWrapper>
    );

    return (
      <Box
        display="flex"
        alignItems="center"
        bgcolor="black"
        width="100%"
        sx={{
          '& img': {
            // prevent the InternalLink to add few extra pixels
            display: 'block',
          },
        }}
      >
        {videoConfig.thumbnailLink ?? true ? (
          <InternalLink
            to={`${baseUrl}/entities/${entity.uid}`}
            sx={{ width: '100%' }}
          >
            {thumbnail}
          </InternalLink>
        ) : (
          thumbnail
        )}
      </Box>
    );
  }
  if (entity.type === TypeEnum.CANDIDATE_FR_2022) {
    return (
      <Box
        display="flex"
        maxHeight="280px"
        justifyContent="center"
        sx={{
          '& > img': {
            flex: 1,
            objectFit: 'contain',
          },
        }}
      >
        {compact ? (
          <img src={entity.metadata.image_url} alt={entity.metadata.name} />
        ) : (
          <InternalLink to={`${baseUrl}/entities/${entity.uid}`}>
            <Avatar
              alt={entity?.metadata?.name || ''}
              src={entity?.metadata?.image_url || ''}
              sx={{
                width: '60px',
                height: '60px',
                m: 2,
              }}
            />
          </InternalLink>
        )}
      </Box>
    );
  }
  return null;
};

export default EntityImagery;
