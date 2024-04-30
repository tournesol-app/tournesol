export function extractVideoId(
  idOrUrl: string,
  { ignoreVideoId = false } = {}
) {
  const protocol = /(?:https?:\/\/)?/;
  const subdomain = /(?:www\.|m\.)?/;
  const youtubeWatchUrl = /(?:youtube\.com\/(?:watch\?v=|live\/))/;
  const youtubeShortUrl = /(?:youtu\.be\/)/;
  const tournesolEntityUrl = /(?:[.\w]+\/entities\/)/;

  const videoId = /([A-Za-z0-9-_]{11})/;
  const videoIdOrUid = new RegExp(`(?:yt:)?${videoId.source}`);

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
        `${videoIdOrUid.source}`
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

export function idFromUid(uid: string): string {
  if (uid) {
    const uidSplit = uid.split(':');

    if (uidSplit[0] !== '' && uidSplit[1] !== '') {
      return uidSplit.slice(1).join();
    }
  }

  return '';
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
