import { VideoService } from 'src/services/openapi';
import { allCriterias } from 'src/utils/constants';
import { snakeToCamel } from 'src/utils/string';

export const getRecommendedVideos = async (searchString: string) => {
  const dayInMillisecondes = 1000 * 60 * 60 * 24;
  const conversionTime = new Map();
  const params = new URLSearchParams(searchString);
  conversionTime.set('Any', 1);
  conversionTime.set('Today', dayInMillisecondes);
  conversionTime.set('Week', dayInMillisecondes * 7);
  conversionTime.set('Month', dayInMillisecondes * 31);
  conversionTime.set('Year', dayInMillisecondes * 365);
  const dateNow = Date.now();

  if (params.get('date')) {
    const date = params.get('date');
    params.delete('date');
    if (date != 'Any') {
      // TODO figure out why the 1 month adding is needed here
      const limitPublicationDateMilliseconds =
        dateNow - conversionTime.get(date);
      const param_date = new Date(limitPublicationDateMilliseconds);
      const [d, m, y, H, M, S] = [
        param_date.getDate().toString(),
        (param_date.getMonth() + 1).toString(),
        param_date.getFullYear().toString(),
        param_date.getHours().toString(),
        param_date.getMinutes().toString(),
        param_date.getSeconds().toString(),
      ].map((t) => format(t));
      params.append('date_gte', `${d}-${m}-${y}-${H}-${M}-${S}`);
    }
  }

  function format(str: string) {
    if (str.length == 1) {
      return '0'.concat(str);
    } else if (str.length == 4) {
      return str.slice(2);
    } else {
      return str;
    }
  }

  const getNumberValue = (key: string): number | undefined => {
    const value = params.get(key);
    return value ? Number(value) : undefined;
  };

  try {
    return await VideoService.videoList({
      limit: 20,
      offset: getNumberValue('offset'),
      search: params.get('search') ?? undefined,
      language: params.get('language') ?? undefined,
      uploader: params.get('uploader') ?? undefined,
      dateGte: params.get('date_gte') ?? undefined,
      unsafe: params.get('unsafe') === 'true' ?? undefined,
      ...Object.fromEntries(
        allCriterias.map((c) => [snakeToCamel(c), getNumberValue(c)])
      ),
    });
  } catch (err) {
    console.error(err);
    return {
      results: [],
      count: 0,
    };
  }
};
