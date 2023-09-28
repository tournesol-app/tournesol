import { UsersService, PollsService } from 'src/services/openapi';
import { YOUTUBE_POLL_NAME } from './constants';
import { VideoObject } from './types';

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

function getPseudoRandomInt(max: number) {
  return Math.floor(Math.random() * max);
}

function pick(arr: string[]): string | null {
  // Returns a random element of an array
  return arr.length > 0 ? arr[Math.floor(Math.random() * arr.length)] : null;
}

async function areAlreadyCompared(uidA: string, uidB: string) {
  // TODO implement this method to avoid giving a video that has already been compared
  return uidA === uidB;
}

async function retryRandomPick(
  numberRetries: number,
  uid: string | null,
  uidOther: string | null,
  videoList: string[]
): Promise<string | null> {
  if (numberRetries <= 0 || videoList.length == 0) return null;

  if (uidOther === null) return pick(videoList);

  const newUid = pick(videoList);
  const alreadyCompared =
    newUid && (await areAlreadyCompared(uidOther, newUid));

  if (!alreadyCompared && newUid !== uid) return newUid;

  return await retryRandomPick(
    numberRetries - 1,
    uid,
    uidOther,
    videoList.filter((v) => v !== newUid)
  );
}

export async function getUidFromRateLaterList(
  uid: string | null,
  uidOther: string | null,
  exclude?: string[]
): Promise<string | null> {
  const rateLaters = await UsersService.usersMeRateLaterList({
    pollName: YOUTUBE_POLL_NAME,
    limit: 99,
    offset: 0,
  });

  let newSuggestions =
    rateLaters?.results?.map((rateL) => rateL.entity.uid) || [];

  if (exclude) {
    newSuggestions = newSuggestions.filter((uid) => !exclude.includes(uid));
  }

  const newUid = await retryRandomPick(5, uid, uidOther, newSuggestions);
  return newUid;
}

export async function getUidFromComparedList(
  uid: string | null,
  uidOther: string | null,
  exclude?: string[]
): Promise<string | null> {
  const contributorRatings = await UsersService.usersMeContributorRatingsList({
    pollName: YOUTUBE_POLL_NAME,
    limit: 99,
    offset: 0,
  });

  let newSuggestions =
    contributorRatings.results?.map((rating) => rating.entity.uid) || [];

  if (exclude) {
    newSuggestions = newSuggestions.filter((uid) => !exclude.includes(uid));
  }

  const newUid = retryRandomPick(5, uid, uidOther, newSuggestions);
  return newUid;
}

/**
 * This helper function returns a UID following the strategy:
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
export async function getUidForComparison(
  uid: string | null,
  uidOther: string | null,
  exclude?: string[]
): Promise<string | null> {
  const x = Math.random();

  let newUid;

  if (x < 0.75) {
    newUid = await getUidFromRateLaterList(uid, uidOther, exclude);
    if (newUid) return newUid;
  }

  if (x < 0.95) {
    const newUid = await getUidFromComparedList(uid, uidOther, exclude);
    if (newUid) return newUid;
  }

  const videoResult = await PollsService.pollsRecommendationsList({
    name: 'videos',
    limit: 100,
    // Increase the diversity of recommended videos. Changing the `offset`
    // allows us to not increase the range of suggested videos, without
    // increasing size of the downloaded JSON. We may want to adapt/remove
    // this `offset` the day we will filter the results according to the user
    // preferred languages.
    offset: getPseudoRandomInt(10) * 10,
  });

  let newSuggestions = (videoResult?.results || []).map((v) => v.entity.uid);

  if (exclude) {
    newSuggestions = newSuggestions.filter((uid) => !exclude.includes(uid));
  }

  newUid = await retryRandomPick(5, uid, uidOther, newSuggestions);

  if (newUid) return newUid;
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
