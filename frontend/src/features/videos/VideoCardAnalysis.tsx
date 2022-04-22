import React from 'react';
import { useTranslation } from 'react-i18next';
import { Grid } from '@mui/material';
import { VideoObject } from 'src/utils/types';
import { videoIdFromEntity } from 'src/utils/video';
import { VideoPlayer } from 'src/components/entity/EntityImagery';
import { VideoMetadata } from 'src/components/entity/EntityMetadata';
import VideoCardScores from './VideoCardScores';
import EntityCardTitle from 'src/components/entity/EntityCardTitle';
import { entityCardMainSx } from 'src/components/entity/style';

function VideoCardAnalysis({
  video,
  compact = false,
  controls = true,
  personalScore,
}: {
  video: VideoObject;
  compact?: boolean;
  controls?: boolean;
  personalScore?: number;
}) {
  const { t } = useTranslation();
  const videoId = videoIdFromEntity(video);

  return (
    <Grid container sx={entityCardMainSx}>
      <Grid item xs={12} sx={{ aspectRatio: '16 / 9' }}>
        <VideoPlayer
          videoId={videoId}
          duration={video.duration}
          controls={controls}
        />
      </Grid>
      <Grid
        item
        xs={12}
        sx={{
          padding: 1,
        }}
        data-testid="video-card-info"
        container
        direction="column"
      >
        <EntityCardTitle title={video.name} compact={compact} />
        <VideoMetadata
          views={video.views}
          publicationDate={video.publication_date}
          uploader={video.uploader}
        />

        <VideoCardScores video={video} />

        {personalScore !== undefined &&
          t('video.personalScore', { score: personalScore.toFixed(0) })}
      </Grid>
    </Grid>
  );
}

export default VideoCardAnalysis;
