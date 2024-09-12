import arrow
from datetime import datetime
from typing import Optional, Union
from invenio_search.engine import dsl, search
from invenio_stats.aggregations import StatAggregator


class StatAggregatorOverridable(StatAggregator):
    """A subclass of StatAggregator that allows for overriding the
    bookmark datetime to re-aggregate earlier stats.

    Primarily needed because of re-aggregation after importing older
    records with existing stats.
    """

    def run(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        update_bookmark: bool = True,
        previous_bookmark: Union[str, None, datetime] = None,
    ):
        """Calculate statistics aggregations."""
        # If no events have been indexed there is nothing to aggregate
        from flask import current_app

        if not dsl.Index(self.event_index, using=self.client).exists():
            return

        previous_bookmark = (
            arrow.get(previous_bookmark).naive
            if previous_bookmark
            else self.bookmark_api.get_bookmark()
        )
        current_app.logger.debug(
            "previous bookmark: %s",
            previous_bookmark.isoformat() if previous_bookmark else None,
        )
        lower_limit = (
            arrow.get(start_date).naive
            or previous_bookmark
            or self._get_oldest_event_timestamp()
        )
        current_app.logger.debug(
            "lower limit: %s", lower_limit.isoformat() if lower_limit else None
        )
        # Stop here if no bookmark could be estimated.
        if lower_limit is None:
            return

        upper_limit = self._upper_limit(end_date)
        current_app.logger.debug(
            "upper limit: %s", self._upper_limit(end_date).isoformat()
        )
        dates = self._split_date_range(lower_limit, upper_limit)
        # Let's get the timestamp before we start the aggregation.
        # This will be used for the next iteration. Some events might
        # be processed twice
        if not end_date:
            end_date = arrow.utcnow().isoformat()

        results = []
        for dt_key, dt in sorted(dates.items()):
            results.append(
                search.helpers.bulk(
                    self.client,
                    self.agg_iter(dt, previous_bookmark),
                    stats_only=True,
                    chunk_size=50,
                )
            )
        # current_app.logger.debug("aggregated %s", results)
        if update_bookmark:
            self.bookmark_api.set_bookmark(end_date)
        # current_app.logger.debug("end_date: %s", end_date)
        return results
