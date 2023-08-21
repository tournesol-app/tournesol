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
      const id = extractVideoId(videoId);
      expect(id).toEqual(videoId);
    });

    it('handles Tournesol UID', () => {
      const id = extractVideoId(`yt:${videoId}`);
      expect(id).toEqual(videoId);
    });

    it("handles the pattern 'live'", () => {
      const id1 = extractVideoId(ytUrlPatternLive);
      expect(id1).toEqual(videoId);

      const id2 = extractVideoId(ytUrlPatternLive.replace('://www.', '://'));
      expect(id2).toEqual(videoId);
    });

    it("handles the pattern 'mobile'", () => {
      const id = extractVideoId(ytUrlPatternMobile);
      expect(id).toEqual(videoId);
    });

    it("handles the pattern 'watch'", () => {
      const id1 = extractVideoId(ytUrlPatternWatch);
      expect(id1).toEqual(videoId);

      const id2 = extractVideoId(ytUrlPatternWatch.replace('://www.', '://'));
      expect(id2).toEqual(videoId);
    });

    it("handles the pattern 'youtu.be'", () => {
      const id = extractVideoId(ytUrlPatternShort);
      expect(id).toEqual(videoId);
    });
  });
});
