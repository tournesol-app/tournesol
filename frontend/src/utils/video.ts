import { VideoService, UsersService, TypeEnum } from 'src/services/openapi';
import { YOUTUBE_POLL_NAME } from './constants';
import { RelatedEntityObject, VideoObject } from './types';

export function extractVideoId(idOrUrl: string) {
  const host = process.env.PUBLIC_URL || location.host;
  const escapedCurrentHost = host.replace(/[.\\]/g, '\\$&');

  const matchUrl = idOrUrl.match(
    new RegExp(
      '(?:https?:\\/\\/)?(?:www\\.)?(?:youtube\\.com\\/watch\\?v=|youtu\\.be\\/|' +
        escapedCurrentHost +
        '\\/entities\\/yt:|yt:)([A-Za-z0-9-_]+)'
    )
  );
  const id = matchUrl ? matchUrl[1] : idOrUrl.trim();
  if (isVideoIdValid(id)) {
    return id;
  }
  return null;
}

export function isVideoIdValid(videoId: string) {
  return !!videoId.match(/^[A-Za-z0-9-_]{11}$/);
}

/**
 * Return the video id of an entity.
 *
 * If no field `uid` is found, return the value of the legacy `video_id`
 * field instead.
 *
 * The `uid` is expected to have the form `{namespace}:{id}`. The potential
 * occurrences of the delimiter `:` in the identifier are considered part of it.
 *
 * Example with different `uid`:
 *
 *     yt:videoABCDEF -> videoABCDEF
 *     yt:video:ABCDE -> video:ABCDE
 */
export function videoIdFromEntity(entity: VideoObject): string {
  if (entity.uid) {
    const id = idFromUid(entity.uid);
    if (id) return id;
  }

  return entity.video_id;
}

export function idFromUid(uid: string): string {
  if (uid) {
    const uidSplit = uid.split(':');

    if (uidSplit[0] !== '' && uidSplit[1] !== '') {
      return uidSplit.slice(1).join();
    }
  }

  return '';
}

function pick(arr: string[]): string | null {
  // Returns a random element of an array
  return arr.length > 0 ? arr[Math.floor(Math.random() * arr.length)] : null;
}

async function areAlreadyCompared(videoA: string, videoB: string) {
  // TODO implement this method to avoid giving a video that has already been compared
  return videoA === videoB;
}

async function retryRandomPick(
  numberRetries: number,
  otherVideo: string | null,
  currentVideo: string | null,
  videoList: string[]
): Promise<string | null> {
  if (numberRetries <= 0 || videoList.length == 0) return null;
  if (otherVideo === null) return pick(videoList);
  const newVideoId = pick(videoList);
  const alreadyCompared =
    newVideoId && (await areAlreadyCompared(otherVideo, newVideoId));
  if (!alreadyCompared && newVideoId !== currentVideo) return newVideoId;
  return await retryRandomPick(
    numberRetries - 1,
    otherVideo,
    currentVideo,
    videoList.filter((v) => v !== newVideoId)
  );
}

export async function getVideoFromRateLaterListForComparison(
  otherVideo: string | null,
  currentVideo: string | null
): Promise<string | null> {
  const rateLaterResult = await UsersService.usersMeRateLaterList({
    pollName: YOUTUBE_POLL_NAME,
    limit: 99,
    offset: 0,
  });
  const rateLaterList =
    rateLaterResult?.results?.map((rateL) => rateL.entity.metadata.video_id) ||
    [];

  const rateLaterVideoId = await retryRandomPick(
    5,
    otherVideo,
    currentVideo,
    rateLaterList
  );
  return rateLaterVideoId;
}

export async function getVideoFromPreviousComparisons(
  otherVideo: string | null,
  currentVideo: string | null
): Promise<string | null> {
  const comparisonCount: number =
    (
      await UsersService.usersMeComparisonsList({
        pollName: YOUTUBE_POLL_NAME,
        limit: 0,
        offset: 0,
      })
    )?.count || 0;
  const comparisonVideoResult = await UsersService.usersMeComparisonsList({
    pollName: YOUTUBE_POLL_NAME,
    limit: 99,
    offset: Math.floor(Math.random() * comparisonCount),
  });
  const cl = comparisonVideoResult?.results || [];
  const comparisonVideoList = [
    ...cl.map((v) => v.entity_a.metadata.video_id),
    ...cl.map((v) => v.entity_b.metadata.video_id),
  ];
  const comparisonVideoId = retryRandomPick(
    5,
    otherVideo,
    currentVideo,
    comparisonVideoList
  );
  return comparisonVideoId;
}

export async function getVideoForComparison(
  otherVideo: string | null,
  currentVideo: string | null
): Promise<string | null> {
  // This helper method returns a videoId following the strategy:
  // 1. Uniformily random from rate_later list (75% chance)
  // 2. Uniformily random from already rated videos (20% chance)
  // 3. Uniformily random from Tournesol's top 100 videos (5% chance)
  // If option 1 is selected and fails, option 2 will be tried
  // If option 2 is selected and fails, option 3 will be tried
  const x = Math.random();
  if (x < 0.75) {
    const videoFromRateLaterList = await getVideoFromRateLaterListForComparison(
      otherVideo,
      currentVideo
    );
    if (videoFromRateLaterList) return videoFromRateLaterList;
  }
  if (x < 0.95) {
    const videoFromComparisons = await getVideoFromPreviousComparisons(
      otherVideo,
      currentVideo
    );
    if (videoFromComparisons) return videoFromComparisons;
  }
  const videoResult = await VideoService.videoList({ limit: 100, offset: 0 });
  const videoList = (videoResult?.results || []).map((v) => v.video_id);
  const videoId = await retryRandomPick(5, otherVideo, currentVideo, videoList);
  if (videoId) return videoId;
  return videoList ? pick(videoList) : null;
}

export const convertDurationToClockDuration = (duration: number) => {
  const roundToTwoDigits = (number: number) => {
    return number < 10 ? `0${number}` : `${number}`;
  };
  const hours = Math.floor(duration / 3600);
  const minutes = roundToTwoDigits(Math.floor((duration % 3600) / 60));
  const seconds = roundToTwoDigits(duration % 60);
  return hours > 0 ? `${hours}:${minutes}:${seconds}` : `${minutes}:${seconds}`;
};

export const videoToEntity = (video: VideoObject): RelatedEntityObject => ({
  uid: video.uid,
  type: TypeEnum.VIDEO,
  metadata: {
    name: video.name,
    description: video.description,
    publication_date: video.publication_date,
    uploader: video.uploader,
    language: video.language,
    duration: video.duration,
    video_id: video.video_id,
    views: video.views,
  },
});
