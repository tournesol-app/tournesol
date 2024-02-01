import { extractVideoId } from './video';

describe('video module', () => {
  describe('function - extractVideoId', () => {
    const videoId = 'lYXQvHhfKuM';

    const ytUrlPatternLive =
      'https://www.youtube.com/live/lYXQvHhfKuM?feature=share';
    const ytUrlPatternMobile = 'https://m.youtube.com/watch?v=lYXQvHhfKuM';
    const ytUrlPatternShort = 'https://youtu.be/lYXQvHhfKuM';
    const ytUrlPatternWatch = 'https://www.youtube.com/watch?v=lYXQvHhfKuM';

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

    it("handles the pattern 'live'", () => {
      const id1 = extractVideoId(ytUrlPatternLive);
      expect(id1).toEqual(videoId);

      const id2 = extractVideoId(ytUrlPatternLive.replace('://www.', '://'));
      expect(id2).toEqual(videoId);

      const id3 = extractVideoId(ytUrlPatternLive, { ignoreVideoId: true });
      expect(id3).toEqual(videoId);
    });

    it("handles the pattern 'mobile'", () => {
      const id = extractVideoId(ytUrlPatternMobile);
      expect(id).toEqual(videoId);

      const id2 = extractVideoId(ytUrlPatternMobile, { ignoreVideoId: true });
      expect(id2).toEqual(videoId);
    });

    it("handles the pattern 'watch'", () => {
      const id1 = extractVideoId(ytUrlPatternWatch);
      expect(id1).toEqual(videoId);

      const id2 = extractVideoId(ytUrlPatternWatch.replace('://www.', '://'));
      expect(id2).toEqual(videoId);

      const id3 = extractVideoId(ytUrlPatternWatch, { ignoreVideoId: true });
      expect(id3).toEqual(videoId);
    });

    it("handles the pattern 'youtu.be'", () => {
      const id = extractVideoId(ytUrlPatternShort);
      expect(id).toEqual(videoId);

      const id2 = extractVideoId(ytUrlPatternShort, { ignoreVideoId: true });
      expect(id2).toEqual(videoId);
    });
  });
});
