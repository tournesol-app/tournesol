from functools import total_ordering


@total_ordering
class Video:
    yt_url = ""
    v1_score = 0
    v2_score = 0
    estimated_information_gains = []
    estimated_related_preferences = []

    def __eq__(self, __o: object) -> bool:
        return __o.__class__ == self.__class__ and __o.yt_url == self.yt_url

    def __gt__(self, obj):
        return self.v2_score > obj.v2_score

    def __le__(self, other):
        return self.v2_score <= other.v2_score

    def __repr__(self) -> str:
        return "Video " + self.yt_url + \
               " with score v1 " + str(self.v1_score) + \
               " and score v2 " + str(self.v2_score)
