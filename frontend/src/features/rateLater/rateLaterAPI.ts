import { UsersService } from 'src/services/openapi';
import { Video } from 'src/services/openapi';

export const addToRateLaterList = async ({
  video_id,
}: {
  video_id: string;
}) => {
  return UsersService.usersMeVideoRateLaterCreate({
    requestBody: {
      video: { video_id } as Video,
    },
  });
};
