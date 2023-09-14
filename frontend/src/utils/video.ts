import { UsersService, TypeEnum, PollsService } from 'src/services/openapi';
import { YOUTUBE_POLL_NAME } from './constants';
import { RelatedEntityObject, VideoObject } from './types';

export function extractVideoId(idOrUrl: string) {
  const host = process.env.PUBLIC_URL || location.host;
  const escapedCurrentHost = host.replace(/[.\\]/g, '\\$&');

  const matchUrl = idOrUrl.match(
    new RegExp(
      '(?:https?:\\/\\/)?(?:www\\.|m\\.)?' +
        '(?:youtube\\.com\\/watch\\?v=|youtube\\.com\\/live\\/|youtu\\.be\\/|' +
        escapedCurrentHost +
        '\\/entities\\/yt:|yt:)([A-Za-z0-9-_]{11})'
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

function getPeudoRandomInt(max: number) {
  return Math.floor(Math.random() * max);
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
  currentVideo: string | null,
  exclude?: string[]
): Promise<string | null> {
  const rateLaterResult = await UsersService.usersMeRateLaterList({
    pollName: YOUTUBE_POLL_NAME,
    limit: 99,
    offset: 0,
  });

  let newSuggestions =
    rateLaterResult?.results?.map((rateL) => rateL.entity.metadata.video_id) ||
    [];

  if (exclude) {
    newSuggestions = newSuggestions.filter(
      (videoId) => !exclude.includes(`yt:${videoId}`)
    );
  }

  const rateLaterVideoId = await retryRandomPick(
    5,
    otherVideo,
    currentVideo,
    newSuggestions
  );

  return rateLaterVideoId;
}

export async function getVideoFromPreviousComparisons(
  otherVideo: string | null,
  currentVideo: string | null,
  exclude?: string[]
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

  let newSuggestions = comparisonVideoList.filter(
    (videoId, index) => comparisonVideoList.indexOf(videoId) === index
  );
  if (exclude) {
    newSuggestions = newSuggestions.filter(
      (videoId) => !exclude.includes(`yt:${videoId}`)
    );
  }

  const comparisonVideoId = retryRandomPick(
    5,
    otherVideo,
    currentVideo,
    newSuggestions
  );
  return comparisonVideoId;
}

/**
 * This helper function returns a video id following the strategy:
 *
 *  1. Uniformily random from rate_later list (75% chance)
 *  2. Uniformily random from already rated videos (20% chance)
 *  3. Uniformily random from Tournesol's top 100 videos (5% chance)
 *  If option 1 is selected and fails, option 2 will be tried
 *  If option 2 is selected and fails, option 3 will be tried
 *
 * The exlude parameter allows to exclude a list of UIDs before the random
 * selection.
 */
export async function getVideoForComparison(
  otherVideo: string | null,
  currentVideo: string | null,
  exclude?: string[]
): Promise<string | null> {
  const x = Math.random();
  if (x < 0.75) {
    const videoFromRateLaterList = await getVideoFromRateLaterListForComparison(
      otherVideo,
      currentVideo,
      exclude
    );
    if (videoFromRateLaterList) return videoFromRateLaterList;
  }
  if (x < 0.95) {
    const videoFromComparisons = await getVideoFromPreviousComparisons(
      otherVideo,
      currentVideo,
      exclude
    );
    if (videoFromComparisons) return videoFromComparisons;
  }
  const videoResult = await PollsService.pollsRecommendationsList({
    name: 'videos',
    limit: 100,
    // Increase the diversity of recommended videos. Changing the `offset`
    // allows us to not increase the `limit`, and this way limits the size of
    // the JSON downloaded. We may want to adapt/remove this `offset` the day
    // we will filter the results according to the user preferred languages.
    offset: getPeudoRandomInt(10) * 10,
  });

  let newSuggestions = (videoResult?.results || []).map((v) =>
    idFromUid(v.uid)
  );

  if (exclude) {
    newSuggestions = newSuggestions.filter(
      (videoId) => !exclude.includes(`yt:${videoId}`)
    );
  }

  const videoId = await retryRandomPick(
    5,
    otherVideo,
    currentVideo,
    newSuggestions
  );
  if (videoId) return videoId;

  return newSuggestions ? pick(newSuggestions) : null;
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
