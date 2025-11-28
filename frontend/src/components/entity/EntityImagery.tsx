import React, { useEffect, useState } from 'react';
import ReactPlayer from 'react-player/youtube';

import { Avatar, Box, useTheme } from '@mui/material';

import { InternalLink } from 'src/components';
import { useCurrentPoll, useLoginState } from 'src/hooks';
import { TypeEnum } from 'src/services/openapi';
import { absolutePollBasePath } from 'src/utils/navigation';
import { JSONValue, EntityObject } from 'src/utils/types';
import { convertDurationToClockDuration, idFromUid } from 'src/utils/video';
import { updateContributorRatingEntitySeen } from 'src/utils/api/contributorRatings';
import { UID_YT_NAMESPACE } from 'src/utils/constants';

// Check if the video can be considered watched after each tick (in ms).
const PROGRESS_TICK_MS = 1000;
// A video is considered watched if more than this fraction of time has
// passed.
const WATCHED_FRACTION = 0.6;

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
      onClick={() => setIsDurationVisible(false)}
      ref={ref}
      sx={{
        position: 'relative',
        height: '100%',
        width: '100%',
      }}
    >
      {isDurationVisible && formattedDuration && (
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            right: 0,
            color: '#fff',
            bgcolor: 'rgba(0,0,0,0.5)',
            px: 1,
            fontFamily: 'system-ui, arial, sans-serif',
            fontSize: '0.8rem',
            fontWeight: 'bold',
            lineHeight: 1.5,
            zIndex: theme.zIndex.videoCardDuration,
            pointerEvents: 'none',
          }}
        >
          {formattedDuration}
        </Box>
      )}
      {children}
    </Box>
  );
});

export const YoutubeVideoPlayer = ({
  videoId,
  duration,
  controls = true,
}: {
  videoId: string;
  duration?: number | null;
  controls?: boolean;
}) => {
  const { name: pollName, options } = useCurrentPoll();
  const { isLoggedIn } = useLoginState();

  const [playRate, setPlayRate] = useState(1);
  const [secondsPlayed, setSecondsPlayed] = useState(0);
  const [watched, setWatched] = useState(false);

  useEffect(() => {
    if (!isLoggedIn || !duration || watched) {
      return;
    }

    const markAsWatched = async () => {
      setWatched(true);

      try {
        await updateContributorRatingEntitySeen(
          pollName,
          `${UID_YT_NAMESPACE}${videoId}`,
          true,
          options?.comparisonsCanBePublic === true
        );
      } catch {
        {
          console.error('Failed to update the contributor rating.');
        }
      }
    };

    if (secondsPlayed > duration * WATCHED_FRACTION) {
      markAsWatched();
    }
  }, [
    duration,
    isLoggedIn,
    options?.comparisonsCanBePublic,
    pollName,
    secondsPlayed,
    videoId,
    watched,
  ]);

  return (
    <ReactPlayer
      url={`https://youtube.com/watch?v=${videoId}`}
      playing
      light={`https://i.ytimg.com/vi/${videoId}/sddefault.jpg`}
      width="100%"
      height="100%"
      wrapper={DurationWrapper}
      duration={duration}
      controls={controls}
      progressInterval={PROGRESS_TICK_MS}
      onProgress={() =>
        setSecondsPlayed(
          (current) => current + (playRate * PROGRESS_TICK_MS) / 1000
        )
      }
      playbackRate={playRate}
      onPlaybackRateChange={(rate: number) => setPlayRate(rate)}
      config={{
        playerVars: {
          /*
          Setting `playsinline=0` is intended to make the video start in fullscreen on iOS.
          However, this doesn't always work as expected. When a user clicks the "light"
          player thumbnail, the player attempts to autoplay the video. In some cases,
          Safari might block this autoplay (if the player loads too slowly?), as the video
          playback might not be recognized as a direct result of the user's click.
          */
          playsinline: 0,
        },
      }}
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
          <YoutubeVideoPlayer
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
        sx={{
          display: 'flex',
          alignItems: 'center',
          bgcolor: 'black',
          width: '100%',
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
        sx={{
          display: 'flex',
          maxHeight: '280px',
          justifyContent: 'center',
          '& > img': {
            flex: 1,
            objectFit: 'contain',
          },
        }}
      >
        {compact ? (
          <img src={entity.metadata.image_url} alt={entity.metadata.name} />
        ) : (
          <InternalLink
            to={`${absolutePollBasePath(baseUrl)}/entities/${entity.uid}`}
          >
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
