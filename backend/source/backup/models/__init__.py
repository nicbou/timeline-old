from django.db import models


class BaseSource(models.Model):
    class Meta:
        abstract = True

    @property
    def source_name(self) -> str:
        return type(self).__name__

    @property
    def entry_source(self) -> str:
        """
        A "source" value shared by all entries created by this Source instance.

        For example "twitter/katyperry" or "rsync/macbook"
        """
        return f"{self.source_name}/{self.id}"
