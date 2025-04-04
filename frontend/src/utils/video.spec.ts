import { extractVideoId } from './video';

describe('video module', () => {
  describe('function - extractVideoId', () => {
    const videoId = 'lYXQvHhfKuM';

    const validUrls = [
      'https://www.youtube.com/watch?v=lYXQvHhfKuM',
      'https://youtube.com/watch?v=lYXQvHhfKuM',
      'https://www.youtube.com/live/lYXQvHhfKuM?feature=share',
      'https://youtube.com/live/lYXQvHhfKuM?feature=share',
      'https://m.youtube.com/watch?v=lYXQvHhfKuM',
      'https://youtu.be/lYXQvHhfKuM',
      'https://www.youtube.com/v/lYXQvHhfKuM',
      'https://www.youtube.com/shorts/lYXQvHhfKuM',
    ];

    it('handles video id', () => {
      const id1 = extractVideoId(videoId);
      expect(id1).toEqual(videoId);

      // When ignoreVideoId is true, raw video id should not be extracted.
      const id2 = extractVideoId(videoId, { ignoreVideoId: true });
      expect(id2).toEqual(null);
    });

    it('handles Tournesol UID', () => {
      const id1 = extractVideoId(`yt:${videoId}`);
      expect(id1).toEqual(videoId);

      const id2 = extractVideoId(`yt:${videoId}`, { ignoreVideoId: true });
      expect(id2).toEqual(videoId);
    });

    test.each(validUrls)('handles URL %s', (validUrl) => {
      const extractedVideoId = extractVideoId(validUrl);
      expect(extractedVideoId).toEqual(videoId);

      const extractedVideoId2 = extractVideoId(validUrl, {
        ignoreVideoId: true,
      });
      expect(extractedVideoId2).toEqual(videoId);
    });
  });
});
