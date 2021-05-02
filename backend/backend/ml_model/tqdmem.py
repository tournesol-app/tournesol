from tqdm.auto import tqdm
import os
import psutil


def get_rss_bytes(process="current"):
    """Get rss for a process."""
    assert isinstance(process, int) or (
        isinstance(process, str) and process == "current"
    ), process

    process = psutil.Process(os.getpid())
    mem_bytes = process.memory_info().rss
    return mem_bytes


def print_memory(stage=None):
    """Print the memory used by the current process."""
    mem_bytes = get_rss_bytes(process="current")
    print("Memory used (%s): %.1f MB" % (str(stage), mem_bytes / 1024.0 / 1024.0))


class tqdmem(tqdm):
    """[ ####     24/100it, mem=+2 MB]

    Inspired by https://github.com/tqdm/tqdm/issues/374
    """

    def __init__(self, *args, relative=True, **kwargs):
        self.rss_start_mb = tqdmem.get_memory_mb()
        self.relative = relative
        self.last_postfix = {}
        super(tqdmem, self).__init__(*args, **kwargs)

    def with_mem_postfix(self, key="mem"):
        """Add memory usage postfix entry."""
        postfix_total = dict(self.last_postfix)
        postfix_total[key] = self.format_mem()
        super(tqdmem, self).set_postfix(**postfix_total)

    def set_postfix(self, **kwargs):
        self.last_postfix = kwargs
        super(tqdmem, self).set_postfix(**kwargs)

    def update(self, *args, **kwargs):
        self.with_mem_postfix()
        return super(tqdmem, self).update(*args, **kwargs)

    def __iter__(self):
        self.with_mem_postfix()
        return super(tqdmem, self).__iter__()

    @staticmethod
    def get_memory_mb():
        # get the memory usage in mb
        return get_rss_bytes(process="current") / (1024 * 1024)

    def format_mem(self, postfix="mb"):
        rss_now_mb = tqdmem.get_memory_mb()

        def format_total(total):
            return "%.2f" % total

        def format_delta(delta):
            return "+%.2f" % delta

        if self.relative:
            return format_delta(rss_now_mb - self.rss_start_mb) + postfix
        else:
            return format_total(rss_now_mb) + postfix
