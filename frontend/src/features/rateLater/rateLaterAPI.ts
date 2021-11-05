import { ensureVideoExistsOrCreate } from 'src/utils/video';
import { UsersService } from 'src/services/openapi';
import { Video } from 'src/services/openapi';

export const addToRateLaterList = async ({
  video_id,
}: {
  video_id: string;
}) => {
  await ensureVideoExistsOrCreate(video_id);
  return UsersService.usersMeVideoRateLaterCreate({
    video: { video_id } as Video,
  });
};
