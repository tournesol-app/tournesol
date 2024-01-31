import { UsersService } from 'src/services/openapi';
import { VideoObject } from './types';
import {
  autoSuggestionsRandom,
  fillAutoSuggestions,
  isAutoSuggestionsEmpty,
} from 'src/features/rateLater/autoSuggestions';

export function extractVideoId(idOrUrl: string, ignoreVideoId = false) {
  const protocol = /(?:https?:\/\/)?/;
  const subdomain = /(?:www\.|m\.)?/;
  const youtubeWatchUrl = /(?:youtube\.com\/(?:watch\?v=|live\/))/;
  const youtubeShortUrl = /(?:youtu\.be\/)/;
  const tournesolEntityUrl = /(?:[.\w]+\/entities\/)/;

  const videoId = /([A-Za-z0-9-_]{11})/;
  const youtubeId = /(?:yt:)?([A-Za-z0-9-_]{11})/;

  if (ignoreVideoId) {
    const matchVideoId = idOrUrl.match(new RegExp(`^${videoId.source}`));
    if (matchVideoId != null) {
      return null;
    }
  }

  const matchUrl = idOrUrl.match(
    new RegExp(
      `^${protocol.source}${subdomain.source}` +
        `(?:${youtubeWatchUrl.source}|${youtubeShortUrl.source}|${tournesolEntityUrl.source})?` +
        `${youtubeId.source}`
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

export async function getUidForComparison(
  uid: string | null,
  uidOther: string | null,
  poll: string
): Promise<string | null> {
  const exclude: string[] = [];

  [uid, uidOther].forEach((item) => {
    if (item) {
      exclude.push(item);
    }
  });

  if (isAutoSuggestionsEmpty(poll)) {
    const suggestions = await UsersService.usersMeSuggestionsTocompareList({
      pollName: poll,
    });

    if (suggestions && suggestions.length > 0) {
      fillAutoSuggestions(
        poll,
        suggestions.map((item) => item.entity.uid),
        exclude
      );
    }
  }

  if (isAutoSuggestionsEmpty(poll)) {
    return null;
  }

  return autoSuggestionsRandom(poll, exclude);
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
