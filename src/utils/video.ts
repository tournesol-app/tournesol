import { VideoService } from 'src/services/openapi';
// import { OpenAPI, VideoService, UsersService } from 'src/services/openapi';

export function extractVideoId(idOrUrl: string) {
  const matchUrl = idOrUrl.match(
    /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu.be\/)([A-Za-z0-9-_]+)/
  );
  if (matchUrl) {
    return matchUrl[1];
  }
  return idOrUrl;
}

export async function ensureVideoExistOrCreate(video_id: string) {
  // FIXME: should the video be created automatically?
  // And if so, shouldn't the backend be responsible for it?
  // It's currently impractical to check if the API error
  // is blocking or not.
  try {
    await VideoService.videoCreate({ video_id });
  } catch (err) {
    if (
      err.status === 400 &&
      err.body?.video_id?.[0]?.includes('already exists')
    ) {
      console.debug(
        'Video already exists in the database: API error can be ignored'
      );
    } else {
      throw err;
    }
  }
}

// // TODO: improve this method to not return a video if it has already been compared with the target other video
// export async function getVideoForComparison(
//   token: string | undefined,
//   username: string | undefined
// ) {
//   // This helper method returns a videoId following the strategy:
//   // 1. Uniformily random from rate_later list (75% chance)
//   // 2. Uniformily random from already rated videos (20% chance)
//   // 3. Uniformily random from Tournesol's top 100 videos (5% chance)
//   // If option 1 is selected and fails, option 2 will be tried
//   // If option 2 is selected and fails, option 3 will be tried
//   if (!token || !username) return;
//   OpenAPI.TOKEN = token;

//   const x = Math.random();
//   if (x < 0.75) {
//     const rate_later_empty_result = await UsersService.usersVideoRateLaterList(
//       username,
//       0,
//       0
//     );
//     if (rate_later_empty_result && rate_later_empty_result.count) {
//       const rate_later_offset = Math.floor(
//         rate_later_empty_result.count * Math.random()
//       );
//       const rate_later_result = await UsersService.usersVideoRateLaterList(
//         username,
//         1,
//         rate_later_offset
//       );
//       if (rate_later_result && rate_later_result.results)
//         return rate_later_result.results[0].video.video_id;
//     }
//   }
//   if (x < 0.95) {
//     const comparison_empty_result = await UsersService.usersVideoRateLaterList(
//       username,
//       0,
//       0
//     );
//     if (comparison_empty_result && comparison_empty_result.count) {
//       const comparison_offset = Math.floor(
//         comparison_empty_result.count * Math.random()
//       );
//       const comparison_result = await UsersService.usersMeComparisonsList(
//         1,
//         comparison_offset
//       );
//       if (comparison_result?.results) {
//         const aOrB = Math.random() > 0.5 ? 'video_a' : 'video_b';
//         return comparison_result.results[0][aOrB].video_id;
//       }
//     }
//   }
//   const video_offset = Math.floor(100 * Math.random());
//   const video_result = await VideoService.videoList(1, video_offset);
//   if (video_result?.results) return video_result.results[0].video_id;
// }
