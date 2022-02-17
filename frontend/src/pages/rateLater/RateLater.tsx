import React, { useEffect, useCallback } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Card, Box, CardContent, CardActions } from '@mui/material';
import makeStyles from '@mui/styles/makeStyles';
import Typography from '@mui/material/Typography';

import { addToRateLaterList } from 'src/features/rateLater/rateLaterAPI';
import RateLaterAddForm from 'src/features/rateLater/RateLaterAddForm';
import { ApiError, VideoRateLater } from 'src/services/openapi';
import { CompareNowAction, RemoveFromRateLater } from 'src/utils/action';
import { UsersService } from 'src/services/openapi';
import {
  ContentBox,
  ContentHeader,
  LoaderWrapper,
  Pagination,
} from 'src/components';
import VideoList from 'src/features/videos/VideoList';
import { useNotifications } from 'src/hooks';
import { getWebExtensionUrl } from 'src/utils/extension';

const useStyles = makeStyles({
  rateLaterIntro: {
    textAlign: 'center',
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'column',
    fontSize: '14px',
  },
  rateLaterContent: {
    flexDirection: 'column',
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: '20px',
  },
  stickyPagination: {
    position: 'sticky',
    top: 4,
    zIndex: 1,
    padding: '6px',
  },
});

const RateLaterPage = () => {
  const { t } = useTranslation();
  const { displayErrorsFrom, showSuccessAlert } = useNotifications();

  const classes = useStyles();
  const [isLoading, setIsLoading] = React.useState(true);
  const [offset, setOffset] = React.useState(0);
  const [videoCount, setVideoCount] = React.useState<number | null>(null);
  const videoListTopRef = React.useRef<HTMLDivElement>(null);
  const [rateLaterList, setRateLaterList] = React.useState<VideoRateLater[]>(
    []
  );
  const limit = 20;

  const loadList = useCallback(async () => {
    setIsLoading(true);
    let rateLaterResponse;
    try {
      rateLaterResponse = await UsersService.usersMeVideoRateLaterList({
        limit,
        offset,
      });
    } catch (err) {
      console.error('Fetch rater list failed.', err);
      setIsLoading(false);
      return;
    }
    if (rateLaterResponse.count != null) {
      setVideoCount(rateLaterResponse.count);
    }
    if (rateLaterResponse.results != null) {
      setRateLaterList(rateLaterResponse.results);
    }
    setIsLoading(false);
  }, [offset, setVideoCount, setRateLaterList]);

  const addToRateLater = async (video_id: string): Promise<boolean> => {
    const response = await addToRateLaterList({ video_id }).catch(
      (reason: ApiError) => {
        displayErrorsFrom(reason, t('ratelater.errorOccurredCannotAddVideo'), [
          {
            status: 409,
            variant: 'warning',
            msg: t('ratelater.videoAlreadyInList'),
          },
        ]);
      }
    );
    if (response) {
      showSuccessAlert(t('ratelater.videoAdded'));
      await loadList();
      return true;
    }
    return false;
  };

  const onOffsetChange = (newOffset: number) => {
    setOffset(newOffset);
    videoListTopRef.current?.scrollIntoView();
  };

  useEffect(() => {
    loadList();
  }, [loadList]);

  const videos = rateLaterList.map((r) => r.video);

  return (
    <>
      <ContentHeader title={t('myRateLaterListPage.title')} />
      <ContentBox noMinPaddingX maxWidth="md">
        <Card className={classes.rateLaterIntro} elevation={4}>
          <CardContent>
            <Typography variant="h6">
              {t('ratelater.addVideosToRateLaterList')}
            </Typography>
            <Trans t={t} i18nKey="ratelater.rateLaterFormIntroduction">
              Copy-paste the id or the URL of a favorite video of yours.
              <br />
              You can search them in your{' '}
              <a href="https://www.youtube.com/feed/history">
                YouTube history page
              </a>
              , or your{' '}
              <a href="https://www.youtube.com/playlist?list=LL">
                liked video playlist
              </a>
              .<br />
              Our{' '}
              <a href={getWebExtensionUrl() ?? getWebExtensionUrl('chrome')}>
                browser extension
              </a>{' '}
              can also help you import videos effortlessly.
              <br />
              You will then be able to rate the videos you imported.
            </Trans>
          </CardContent>
          <CardActions>
            <RateLaterAddForm addVideo={addToRateLater} />
          </CardActions>
        </Card>

        <div className={classes.rateLaterContent} ref={videoListTopRef}>
          {videoCount !== null && (
            <Typography variant="subtitle1">
              <Trans
                t={t}
                i18nKey="ratelater.listHasNbVideos"
                count={videoCount}
              >
                Your rate-later list now has <strong>{{ videoCount }}</strong>{' '}
                video(s).
              </Trans>
            </Typography>
          )}

          {!!videoCount && (
            <div className={classes.stickyPagination}>
              <Pagination
                offset={offset}
                count={videoCount}
                onOffsetChange={onOffsetChange}
                limit={limit}
              />
            </div>
          )}

          <Box width="100%" textAlign="center">
            <LoaderWrapper isLoading={isLoading}>
              <VideoList
                videos={videos}
                actions={[CompareNowAction, RemoveFromRateLater(loadList)]}
              />
            </LoaderWrapper>
          </Box>
        </div>
      </ContentBox>
    </>
  );
};

export default RateLaterPage;
