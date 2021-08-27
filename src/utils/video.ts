export function extractVideoId(idOrUrl: string) {
  const matchUrl = idOrUrl.match(
    /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu.be\/)([A-Za-z0-9-_]+)/
  );
  if (matchUrl) {
    return matchUrl[1];
  }
  return idOrUrl;
}
