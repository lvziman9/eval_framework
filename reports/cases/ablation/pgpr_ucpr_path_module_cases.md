# PGPR/UCPR Path-Module Qualitative Explanation Cases

Cases compare the frozen Original recommender top-10 against a deterministic ETD path-module reconstruction at alpha=1.

These cases are qualitative illustrations only; they are not a metric proof and are not a full alpha-sweep reproduction.

## LastFM / PGPR / user 12294

- Role: main
- Case type: qualitative explanation case
- Module: ETD path module at alpha=1
- Unique path types: 2 -> 5
- Changed top-10 positions: 3

Original recommender sample:

- rank 1: pid=759, type=belong_to, path=`self_loop user 12294 listened song 43611 belong_to category 4 belong_to song 759`
- rank 2: pid=6711, type=listened, path=`self_loop user 12294 listened song 25681 listened user 8196 listened song 6711`
- rank 3: pid=760, type=belong_to, path=`self_loop user 12294 listened song 16931 belong_to category 4 belong_to song 760`
- rank 4: pid=2845, type=listened, path=`self_loop user 12294 listened song 25681 listened user 11909 listened song 2845`
- rank 5: pid=3971, type=listened, path=`self_loop user 12294 listened song 14726 listened user 2039 listened song 3971`
- rank 6: pid=444, type=listened, path=`self_loop user 12294 listened song 20495 listened user 118 listened song 444`
- rank 7: pid=323, type=listened, path=`self_loop user 12294 listened song 25681 listened user 942 listened song 323`
- rank 8: pid=286, type=listened, path=`self_loop user 12294 listened song 47367 listened user 92 listened song 286`
- rank 9: pid=885, type=listened, path=`self_loop user 12294 listened song 14726 listened user 8865 listened song 885`
- rank 10: pid=2536, type=listened, path=`self_loop user 12294 listened song 20495 listened user 172 listened song 2536`

Path module sample:

- rank 1: pid=759, type=belong_to, score=0.7174, path=`self_loop user 12294 listened song 43611 belong_to category 4 belong_to song 759`
- rank 2: pid=6711, type=listened, score=0.7156, path=`self_loop user 12294 listened song 25681 listened user 8196 listened song 6711`
- rank 3: pid=760, type=belong_to, score=0.7142, path=`self_loop user 12294 listened song 16931 belong_to category 4 belong_to song 760`
- rank 4: pid=2845, type=listened, score=0.7117, path=`self_loop user 12294 listened song 25681 listened user 11909 listened song 2845`
- rank 5: pid=3971, type=listened, score=0.6659, path=`self_loop user 12294 listened song 20495 listened user 5429 listened song 3971`
- rank 6: pid=444, type=listened, score=0.6620, path=`self_loop user 12294 listened song 20495 listened user 118 listened song 444`
- rank 7: pid=323, type=listened, score=0.6579, path=`self_loop user 12294 listened song 25681 listened user 942 listened song 323`
- rank 8: pid=3277, type=related_to, score=0.4102, path=`self_loop user 12294 listened song 15184 related_to related_song 29317 related_to song 3277`
- rank 9: pid=36543, type=mixed_by, score=0.2456, path=`self_loop user 12294 listened song 25681 mixed_by engineer 78 mixed_by song 36543`
- rank 10: pid=25933, type=produced_by_producer, score=0.2414, path=`self_loop user 12294 listened song 25681 produced_by_producer producer 650 produced_by_producer song 25933`

## LastFM / UCPR / user 12294

- Role: auxiliary
- Case type: qualitative explanation case
- Module: ETD path module at alpha=1
- Unique path types: 2 -> 4
- Changed top-10 positions: 2

Original recommender sample:

- rank 1: pid=6711, type=listened, path=`self_loop user 12294 listened song 14726 listened user 2491 listened song 6711`
- rank 2: pid=29971, type=listened, path=`self_loop user 12294 listened song 25681 listened user 17257 listened song 29971`
- rank 3: pid=6801, type=listened, path=`self_loop user 12294 listened song 25681 listened user 8037 listened song 6801`
- rank 4: pid=2269, type=listened, path=`self_loop user 12294 listened song 20495 listened user 5245 listened song 2269`
- rank 5: pid=323, type=listened, path=`self_loop user 12294 listened song 43612 listened user 10263 listened song 323`
- rank 6: pid=28295, type=listened, path=`self_loop user 12294 listened song 14726 listened user 15245 listened song 28295`
- rank 7: pid=16181, type=listened, path=`self_loop user 12294 listened song 43612 listened user 10297 listened song 16181`
- rank 8: pid=13011, type=belong_to, path=`self_loop user 12294 listened song 43611 belong_to category 4 belong_to song 13011`
- rank 9: pid=16222, type=listened, path=`self_loop user 12294 listened song 14726 listened user 10592 listened song 16222`
- rank 10: pid=759, type=listened, path=`self_loop user 12294 listened song 47367 listened user 4363 listened song 759`

Path module sample:

- rank 1: pid=6711, type=listened, score=0.7451, path=`self_loop user 12294 listened song 14726 listened user 2491 listened song 6711`
- rank 2: pid=29971, type=listened, score=0.6984, path=`self_loop user 12294 listened song 25681 listened user 17257 listened song 29971`
- rank 3: pid=6801, type=belong_to, score=0.6803, path=`self_loop user 12294 listened song 25681 belong_to category 4 belong_to song 6801`
- rank 4: pid=2269, type=listened, score=0.6128, path=`self_loop user 12294 listened song 20495 listened user 19598 listened song 2269`
- rank 5: pid=323, type=listened, score=0.6101, path=`self_loop user 12294 listened song 43612 listened user 10263 listened song 323`
- rank 6: pid=28295, type=listened, score=0.6032, path=`self_loop user 12294 listened song 14726 listened user 2554 listened song 28295`
- rank 7: pid=16181, type=listened, score=0.6004, path=`self_loop user 12294 listened song 47367 listened user 6458 listened song 16181`
- rank 8: pid=13011, type=listened, score=0.5740, path=`self_loop user 12294 listened song 13088 listened user 12164 listened song 13011`
- rank 9: pid=32212, type=mixed_by, score=0.3715, path=`self_loop user 12294 listened song 13088 mixed_by engineer 1322 mixed_by song 32212`
- rank 10: pid=25933, type=produced_by_producer, score=0.1510, path=`self_loop user 12294 listened song 25681 produced_by_producer producer 650 produced_by_producer song 25933`

## ML-1M / PGPR / user 0

- Role: main
- Case type: qualitative explanation case
- Module: ETD path module at alpha=1
- Unique path types: 1 -> 6
- Changed top-10 positions: 4

Original recommender sample:

- rank 1: pid=421, type=watched, path=`self_loop user 0 watched movie 968 watched user 66 watched movie 421`
- rank 2: pid=520, type=watched, path=`self_loop user 0 watched movie 608 watched user 1943 watched movie 520`
- rank 3: pid=277, type=watched, path=`self_loop user 0 watched movie 1630 watched user 43 watched movie 277`
- rank 4: pid=1031, type=watched, path=`self_loop user 0 watched movie 1898 watched user 297 watched movie 1031`
- rank 5: pid=957, type=watched, path=`self_loop user 0 watched movie 470 watched user 40 watched movie 957`
- rank 6: pid=31, type=watched, path=`self_loop user 0 watched movie 830 watched user 47 watched movie 31`
- rank 7: pid=466, type=watched, path=`self_loop user 0 watched movie 608 watched user 29 watched movie 466`
- rank 8: pid=312, type=watched, path=`self_loop user 0 watched movie 958 watched user 378 watched movie 312`
- rank 9: pid=517, type=watched, path=`self_loop user 0 watched movie 608 watched user 915 watched movie 517`
- rank 10: pid=748, type=watched, path=`self_loop user 0 watched movie 608 watched user 436 watched movie 748`

Path module sample:

- rank 1: pid=421, type=watched, score=0.8663, path=`self_loop user 0 watched movie 470 watched user 1228 watched movie 421`
- rank 2: pid=520, type=watched, score=0.8525, path=`self_loop user 0 watched movie 608 watched user 1943 watched movie 520`
- rank 3: pid=277, type=watched, score=0.8391, path=`self_loop user 0 watched movie 608 watched user 75 watched movie 277`
- rank 4: pid=1031, type=watched, score=0.8337, path=`self_loop user 0 watched movie 1898 watched user 297 watched movie 1031`
- rank 5: pid=957, type=watched, score=0.8250, path=`self_loop user 0 watched movie 470 watched user 40 watched movie 957`
- rank 6: pid=31, type=belong_to, score=0.8233, path=`self_loop user 0 watched movie 765 belong_to category 481 belong_to movie 31`
- rank 7: pid=2401, type=starring, score=0.7102, path=`self_loop user 0 watched movie 1465 starring actor 422 starring movie 2401`
- rank 8: pid=746, type=produced_by_producer, score=0.6553, path=`self_loop user 0 watched movie 765 produced_by_producer producer 403 produced_by_producer movie 746`
- rank 9: pid=128, type=produced_by_company, score=0.4930, path=`self_loop user 0 watched movie 1465 produced_by_company production_company 5 produced_by_company movie 128`
- rank 10: pid=2541, type=directed_by, score=0.3438, path=`self_loop user 0 watched movie 765 directed_by director 354 directed_by movie 2541`

## ML-1M / UCPR / user 0

- Role: auxiliary
- Case type: qualitative explanation case
- Module: ETD path module at alpha=1
- Unique path types: 2 -> 3
- Changed top-10 positions: 1

Original recommender sample:

- rank 1: pid=2359, type=watched, path=`self_loop user 0 watched movie 1898 watched user 4508 watched movie 2359`
- rank 2: pid=2476, type=watched, path=`self_loop user 0 watched movie 1898 watched user 4658 watched movie 2476`
- rank 3: pid=312, type=watched, path=`self_loop user 0 watched movie 1898 watched user 4571 watched movie 312`
- rank 4: pid=31, type=belong_to, path=`self_loop user 0 watched movie 829 belong_to category 24 belong_to movie 31`
- rank 5: pid=1869, type=belong_to, path=`self_loop user 0 watched movie 1969 belong_to category 18 belong_to movie 1869`
- rank 6: pid=277, type=watched, path=`self_loop user 0 watched movie 747 watched user 1656 watched movie 277`
- rank 7: pid=971, type=watched, path=`self_loop user 0 watched movie 2302 watched user 1849 watched movie 971`
- rank 8: pid=957, type=watched, path=`self_loop user 0 watched movie 1898 watched user 1743 watched movie 957`
- rank 9: pid=2467, type=belong_to, path=`self_loop user 0 watched movie 747 belong_to category 408 belong_to movie 2467`
- rank 10: pid=1015, type=watched, path=`self_loop user 0 watched movie 1898 watched user 3666 watched movie 1015`

Path module sample:

- rank 1: pid=2359, type=watched, score=0.8658, path=`self_loop user 0 watched movie 1898 watched user 4508 watched movie 2359`
- rank 2: pid=2476, type=belong_to, score=0.8221, path=`self_loop user 0 watched movie 1898 belong_to category 11 belong_to movie 2476`
- rank 3: pid=312, type=watched, score=0.7923, path=`self_loop user 0 watched movie 1898 watched user 4571 watched movie 312`
- rank 4: pid=31, type=belong_to, score=0.7890, path=`self_loop user 0 watched movie 829 belong_to category 24 belong_to movie 31`
- rank 5: pid=1869, type=belong_to, score=0.7608, path=`self_loop user 0 watched movie 1969 belong_to category 18 belong_to movie 1869`
- rank 6: pid=277, type=watched, score=0.7607, path=`self_loop user 0 watched movie 1465 watched user 727 watched movie 277`
- rank 7: pid=971, type=watched, score=0.7500, path=`self_loop user 0 watched movie 2302 watched user 1849 watched movie 971`
- rank 8: pid=957, type=watched, score=0.7455, path=`self_loop user 0 watched movie 1898 watched user 1743 watched movie 957`
- rank 9: pid=2467, type=belong_to, score=0.7224, path=`self_loop user 0 watched movie 747 belong_to category 408 belong_to movie 2467`
- rank 10: pid=1375, type=starring, score=0.6564, path=`self_loop user 0 watched movie 2563 starring actor 735 starring movie 1375`

