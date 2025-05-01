# Stats and Analytics

## References

https://github.com/inveniosoftware/invenio-stats/blob/master/invenio_stats/utils.py#L94
https://github.com/inveniosoftware/invenio-app-rdm/blob/master/invenio_app_rdm/config.py#L1186
https://github.com/inveniosoftware/react-invenio-app-ils/blob/c55054d59f2a033a5ffffc59b67f4fa1819d2913/src/lib/api/stats/stats.js#L5

## Stats indices

Usage stats are stored only in the search index, not in the db. This makes it imperative that the stats indices are regularly backed up, because the stats cannot be recovered from the db.

### Individual events

Indices are created to store the individual usage events
- `kcworks-events-stats-record-view-YYYY-MM`
- `kcworks-events-stats-file-download-YYYY-MM`

These are collectively aliased to
- `kcworks-events-stats-record-view`
- `kcworks-events-stats-file-download`

### Aggregations

In addition, aggregate indices are created for each month with the naming patterns
- `kcworks-stats-file-download-YYYY-MM`
- `kcworks-stats-record-view-YYYY-MM`
These are collectively aliased to
- `kcworks-stats-file-download`
- `kcworks-stats-record-view`

A bookmarks index tracks the creation of the aggregate indices:
- `kcworks-stats-bookmarks`

The aggregate records each count a single record's events (views or downloads) during the month for the index. They include both the recid and the parent recid, allowing the aggregations to be collected either for an individual version or for all versions of a work (i.e., parent).

- bucket aggregations create a bucket for each unique term in a field
    - "aggregations.xxx.buckets" is an array of objects with "key" and "doc_count" values

#### Aggregation requests

in agg_iter:

```python
dsl.Search(using=self.client, index=self.event_index).filter(
    # Filter for the specific interval (hour, day, month)
    "term",
    timestamp=rounded_dt,
)
for p in range(num_partitions)
    terms = agg_query.aggs.bucket(
    "terms",
    "terms",
    field=unique_id,
    include={"partition": p, "num_partitions": num_partitions},
    size=self.max_bucket_size,
    )

    terms.metric(

    "top_hit", "top_hits", size=1, sort={"timestamp": "desc"}

    )

    for dst, (metric, src, opts) in self.metric_fields.items():

    terms.metric(dst, metric, field=src, **opts)


{
 "aggs": {
   "???": {
     "terms": {
       "terms": {
         "field": "unique_session_id",
         "partition": n,
         "num_partitions": x,
         "size": y
       }
     }
     "cardinality": {
       "field": "unique_session_id",
       "precision_threshold": 1000,
     }
   }
 }
}
```

query result basis for aggregation records, from a terms bucket aggregation with only stats returned:
- organized in buckets by "ui" + record id (or "unique_id")
    - "doc_count" lists number of hits (events) for a given *day* (the set interval)

```python
{
'_shards': {'failed': 0, 'skipped': 0, 'successful': 69, 'total': 69},
'aggregations': {
    'terms': {
        'buckets': [
        ...
            {
                'doc_count': 1,
                'key': 'ui_yv6k0-srr25',
                'last_update': {
                    'value': 1726598317179.0,
                    'value_as_string': '2024-09-17T18:38:37.179Z'
                },
                'top_hit': {
                    'hits': {
                        'hits': [
                            {
                            '_id': '2024-04-17T12:19:30-'
                                   'd719203049c7b7ffa7bad3dfc97de87225549cf7',
                            '_index': 'events-stats-record-view-2024-04',
                            '_score': None,
                            '_source': {
                                'country': 'imported',
                                'is_robot': False,
                                'parent_recid': 'q4wph-4hk75',
                                'recid': 'yv6k0-srr25',
                                'timestamp': '2024-04-17T11:19:33',
                                'unique_id': 'ui_yv6k0-srr25',
                                'unique_session_id':
                                    'a6f9fcc160c3360209'
                                    'd163fb95983caee3273e3fb1a4ba549765f75c',
                                'updated_timestamp': '2024-09-i'
                                                     '17T18:38:37.179332',
                                'via_api': False,
                                'visitor_id':
                                    'a6f9fcc160c3360209d163fb959'
                                    '83caee3273e3fb1a4ba549765f75c'
                                },
                            'sort': [1713352773000]
                            }
                        ],
                        'max_score': None,
                        'total': {
                            'relation': 'eq',
                            'value': 1
                        }
                    }
                },
                'unique_count': {
                    'value': 1
                }
            }
        ],
    'doc_count_error_upper_bound': 0,
    'sum_other_doc_count': 0
    }
},
'hits': {
    'hits': [],
    'max_score': None,
    'total': {'relation': 'eq', 'value': 174}},
    'timed_out': False,
    'took': 10
}
```
### Index record schemas

#### kcworks-events-stats-record-view

```json
{
"_index": "kcworks-events-stats-record-view-2019-01",
"_id": "2019-01-01T00:00:00-8e31b4cd058701ecf5ce0dbdc057f3cc775d94ce",
"_score": 1.0,
"_source": {
    "timestamp": "2019-01-01T00:00:00",
    "recid": "jnhz6-e2n32",
    "parent_recid": "pbwf2-yty55",
    "unique_id": "ui_jnhz6-e2n32",
    "is_robot": false,
    "country": "imported",
    "via_api": false,
    "visitor_id": "4c2caf11d9698e896a9b5990c43f60949578cc66deb98d2e31eddabd",
    "unique_session_id": "4c2caf11d9698e896a9b5990c43f60949578cc66deb98d2e31eddabd",
    "updated_timestamp": "2024-07-16T22:58:10.107933"
    }
}
```

#### kcworks-events-stats-file-download

```json
{
  "_index": "kcworks-events-stats-file-download-2019-01",
  "_id": "2019-01-01T00:00:00-0f6eaae908805134818089196c2855f8804781de",
  "_score": 1.0,
  "_source": {
    "timestamp": "2019-01-01T00:00:00",
    "bucket_id": "019b4cd0-31f3-413c-bbc4-95047d1fde34",
    "file_id": "da479344-5585-4bf9-9c6d-23cadf51e7ee",
    "file_key": "lrvol2019iss13fulltext.pdf",
    "size": 742774,
    "recid": "k59an-48c77",
    "parent_recid": "19xa6-enq55",
    "is_robot": false,
    "country": "imported",
    "unique_id": "019b4cd0-31f3-413c-bbc4-95047d1fde34_da479344-5585-4bf9-9c6d-23cadf51e7ee",
    "via_api": false,
    "visitor_id": "4c2caf11d9698e896a9b5990c43f60949578cc66deb98d2e31eddabd",
    "unique_session_id": "4c2caf11d9698e896a9b5990c43f60949578cc66deb98d2e31eddabd",
    "updated_timestamp": "2024-07-17T18:34:13.204519"
  }
}
```

#### kcworks-stats-bookmarks

```json
{
  "_index": "kcworks-stats-bookmarks",
  "_id": "9GFKe5ABGzTNItjdhxgL",
  "_score": 1.0,
  "_source": {
    "date": "2024-07-04T01:10:00.181946",
    "aggregation_type": "stats_reindex"
  }
}
```

#### kcworks-stats-record-view (aggregates)

```json
{
  "_index": "kcworks-stats-record-view-2019-01",
  "_id": "ui_3bn84-vwr29-2019-01-01",
  "_score": 1.0,
  "_source": {
    "timestamp": "2019-01-01T00:00:00",
    "unique_id": "ui_3bn84-vwr29",
    "count": 2,
    "updated_timestamp": "2024-09-04T21:05:28.568054",
    "unique_count": 2,
    "recid": "3bn84-vwr29",
    "parent_recid": "v51aw-69a63",
    "via_api": false
  }
}
```

#### kcworks-stats-file-download (aggregates)

```json
{
  "_index": "kcworks-stats-file-download-2019-01",
  "_id": "1770b96d-04a2-42ff-8bd5-4369f4fceb3c_78785ea0-70a1-49cf-b082-960bf6deae9c-2019-01-01",
  "_score": 1.0,
  "_source": {
    "timestamp": "2019-01-01T00:00:00",
    "unique_id": "1770b96d-04a2-42ff-8bd5-4369f4fceb3c_78785ea0-70a1-49cf-b082-960bf6deae9c",
    "count": 2,
    "updated_timestamp": "2024-09-04T20:56:41.105763",
    "unique_count": 2,
    "volume": 53651620.0,
    "file_id": "78785ea0-70a1-49cf-b082-960bf6deae9c",
    "file_key": "fair-use-in-the-visual-arts-lesson-plans-for-librarians.pdf",
    "bucket_id": "1770b96d-04a2-42ff-8bd5-4369f4fceb3c",
    "recid": "c2gjs-86225",
    "parent_recid": "cqazz-qzj09"
  }
}
```

## Retrieving stats

### Useful OpenSearch queries

To retrieve the cumulative file download stats for all records from a specific date, use the following query:

```bash
GET kcworks-events-stats-file-download/_search?scroll=1m
```

```json
{
  "size": 10,
  "query": {
    "bool": {
      "must": [
        {"term": {"is_robot": false}},
        {"range": {"timestamp": {"gte": "2024-11-15T00:00:00"}}}
      ]
    }
  },
  "aggs": {
    "unique_sessions": {
      "cardinality": {"field": "unique_session_id"}
    }
  }
}
```

This query deduplicates the events by `unique_session_id`.

To retrieve the record view stats, you can use the same query but replace the `kcworks-events-stats-file-download` index with `kcworks-events-stats-record-view`.




## Recording events

### invenio_records

- signals before and after...
    - record create
    - record update
    - recort delete
    - record revert

Stats event recording is triggered by the record insertion signals from invenio_records, which are subscribed to like this:

```python
from invenio_records.signals import (before_record_insert, \
                                      after_record_insert)
listener = before_record_insert.connect(do_something)
listener = after_record_insert.connect(do_something_else)
```

### invenio_rdm_records

The `invenio_rdm_records` app subscribes to the record signals and triggers the stats event recording.

## Stats collection configuration

docs at https://invenio-stats.readthedocs.io/en/latest/configuration.html

The configuration objects are shaped like this:

`STATS_EVENTS`

```python
{
    "file-download": {
        "templates": "invenio_rdm_records.records.stats.templates.events.file_download",
        "event_builders": [
            "invenio_rdm_records.resources.stats.file_download_event_builder",
            "invenio_rdm_records.resources.stats.check_if_via_api",
        ],
    "cls": EventsIndexer,
    "params": {
        "preprocessors": [flag_robots, anonymize_user, build_file_unique_id]
    },
},
```

`STATS_AGGREGATIONS`

```python
    "file-download-agg": {
        "templates": "invenio_rdm_records.records.stats.templates.aggregations.aggr_file_download",
        "cls": StatAggregator,
        "params": {
            "event": "file-download",
            "field": "unique_id",
            "interval": "day",
            "index_interval": "month",
            "copy_fields": {
                "file_id": "file_id",
                "file_key": "file_key",
                "bucket_id": "bucket_id",
                "recid": "recid",
                "parent_recid": "parent_recid",
            },
            "metric_fields": {
                "unique_count": (
                    "cardinality",
                    "unique_session_id",
                    {"precision_threshold": 1000},
                ),
                "volume": ("sum", "size", {}),
            },
        },
    },
```

## Stat calculation for records

calculated in invenio_rdm_records.records.stats.api.Statistics.get_record_stats()

## Stats task scheduling

```python
CELERY_BEAT_SCHEDULE = {
    # indexing of statistics events & aggregations
    "stats-process-events": {
        StatsEventTask,
        "schedule": crontab(minute="25,55"),  # Every hour at minute 25 and 55
    },
    "stats-aggregate-events": {
        StatsAggregationTask,
        "schedule": crontab(minute=0),  # Every hour at minute 0
    },
    "reindex-stats": StatsRDMReindexTask,  # Every hour at minute 10
}
```

## API query configuration

STATS_QUERIES config variable defines allowed queries, params, permissions like this:

```python
STATS_QUERIES = {
    "record-view": {
        "cls": TermsQuery,
        "permission_factory": None,
        "params": {
            "index": "stats-record-view",
            "doc_type": "record-view-day-aggregation",
            "copy_fields": {
                "recid": "recid",
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "recid": "recid",
            },
            "metric_fields": {
                "views": ("sum", "count", {}),
                "unique_views": ("sum", "unique_count", {}),
            },
        },
    }
```



## API endpoint permissions

`STATS_PERMISSION_FACTORY = permissions_policy_lookup_factory`


## Other kinds of stats

### Language of records

To retrieve the counts of records with each language code from OpenSearch, use the following query:

```bash
GET kcworks-rdmrecords-records/_search?scroll=1m
```

```json
{
  "size": 1,
  "aggs": {
    "languages": {
      "terms": {"field": "metadata.languages.id", "size": 1000}
    }
  }
}
```