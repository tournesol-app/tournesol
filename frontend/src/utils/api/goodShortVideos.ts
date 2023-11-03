import { PollsService } from 'src/services/openapi';
import { Recommendation } from 'src/services/openapi';

const shuffleRecommendations = (array: Recommendation[]) => {
  // https://stackoverflow.com/a/12646864/188760
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
};

export const getGoodShortVideos = async ({
  preferredLanguages,
}: {
  preferredLanguages: string[];
}): Promise<Recommendation[]> => {
  const metadata: Record<string, string | string[]> = {};

  const minutesMax = 5;
  const top = 100;

  metadata['duration:lte:int'] = (60 * minutesMax).toString();
  metadata['language'] = preferredLanguages;

  const videos = await PollsService.pollsRecommendationsList({
    name: 'videos',
    metadata: metadata,
    limit: top,
    excludeComparedEntities: true,
  }).then((data) => data.results ?? []);

  const returnCount = 20;

  shuffleRecommendations(videos);
  videos.splice(returnCount);

  return videos;
};
