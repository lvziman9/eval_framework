# PGPR/UCPR Path-Module Qualitative Explanation Cases

Cases compare the frozen Original recommender top-10 against the strict baseline-preserving ETD path module at alpha=1.

The module is constrained to the original top-k item set; alpha=0 preservation is validated in the ablation report.

## LastFM / PGPR / user 34

- Role: main
- Case type: qualitative explanation case
- Module: strict baseline-preserving ETD path module at alpha=1
- Unique path types: 1 -> 2
- Changed top-10 positions: 7

Original recommender sample:

- rank 1: pid=759, type=listened, path=`self_loop user 34 listened song 13939 listened user 2 listened song 759`
- rank 2: pid=760, type=listened, path=`self_loop user 34 listened song 2648 listened user 77 listened song 760`
- rank 3: pid=28847, type=listened, path=`self_loop user 34 listened song 21534 listened user 33 listened song 28847`
- rank 4: pid=2845, type=listened, path=`self_loop user 34 listened song 24372 listened user 12618 listened song 2845`
- rank 5: pid=286, type=listened, path=`self_loop user 34 listened song 21534 listened user 93 listened song 286`
- rank 6: pid=323, type=listened, path=`self_loop user 34 listened song 14726 listened user 252 listened song 323`
- rank 7: pid=3971, type=listened, path=`self_loop user 34 listened song 29971 listened user 167 listened song 3971`
- rank 8: pid=444, type=listened, path=`self_loop user 34 listened song 14332 listened user 190 listened song 444`
- rank 9: pid=2269, type=listened, path=`self_loop user 34 listened song 14726 listened user 21838 listened song 2269`
- rank 10: pid=11647, type=listened, path=`self_loop user 34 listened song 14327 listened user 21263 listened song 11647`

Path module sample:

- rank 1: pid=759, type=listened, score=0.7824, path=`self_loop user 34 listened song 13939 listened user 2 listened song 759`
- rank 2: pid=444, type=belong_to, score=0.7287, path=`self_loop user 34 listened song 33661 belong_to category 4 belong_to song 444`
- rank 3: pid=760, type=listened, score=0.7779, path=`self_loop user 34 listened song 2648 listened user 77 listened song 760`
- rank 4: pid=28847, type=listened, score=0.7763, path=`self_loop user 34 listened song 21534 listened user 33 listened song 28847`
- rank 5: pid=2845, type=listened, score=0.7546, path=`self_loop user 34 listened song 24372 listened user 12618 listened song 2845`
- rank 6: pid=286, type=listened, score=0.7544, path=`self_loop user 34 listened song 21534 listened user 93 listened song 286`
- rank 7: pid=323, type=listened, score=0.7459, path=`self_loop user 34 listened song 14726 listened user 252 listened song 323`
- rank 8: pid=3971, type=listened, score=0.7323, path=`self_loop user 34 listened song 29971 listened user 167 listened song 3971`
- rank 9: pid=2269, type=listened, score=0.7249, path=`self_loop user 34 listened song 14726 listened user 21838 listened song 2269`
- rank 10: pid=11647, type=listened, score=0.7201, path=`self_loop user 34 listened song 14327 listened user 21263 listened song 11647`

## LastFM / UCPR / user 2086

- Role: auxiliary
- Case type: qualitative explanation case
- Module: strict baseline-preserving ETD path module at alpha=1
- Unique path types: 1 -> 2
- Changed top-10 positions: 2

Original recommender sample:

- rank 1: pid=6711, type=listened, path=`self_loop user 2086 listened song 6712 listened user 5874 listened song 6711`
- rank 2: pid=3972, type=listened, path=`self_loop user 2086 listened song 40663 listened user 15172 listened song 3972`
- rank 3: pid=16222, type=listened, path=`self_loop user 2086 listened song 19822 listened user 15856 listened song 16222`
- rank 4: pid=29971, type=listened, path=`self_loop user 2086 listened song 40663 listened user 13879 listened song 29971`
- rank 5: pid=6801, type=listened, path=`self_loop user 2086 listened song 19751 listened user 30 listened song 6801`
- rank 6: pid=13011, type=listened, path=`self_loop user 2086 listened song 19206 listened user 19538 listened song 13011`
- rank 7: pid=24938, type=listened, path=`self_loop user 2086 listened song 40663 listened user 3257 listened song 24938`
- rank 8: pid=16181, type=listened, path=`self_loop user 2086 listened song 19206 listened user 3638 listened song 16181`
- rank 9: pid=15334, type=listened, path=`self_loop user 2086 listened song 5208 listened user 21961 listened song 15334`
- rank 10: pid=12436, type=listened, path=`self_loop user 2086 listened song 12453 listened user 6301 listened song 12436`

Path module sample:

- rank 1: pid=6711, type=listened, score=0.7984, path=`self_loop user 2086 listened song 6712 listened user 5874 listened song 6711`
- rank 2: pid=16222, type=belong_to, score=0.7330, path=`self_loop user 2086 listened song 6712 belong_to category 4 belong_to song 16222`
- rank 3: pid=3972, type=listened, score=0.7453, path=`self_loop user 2086 listened song 40663 listened user 15172 listened song 3972`
- rank 4: pid=29971, type=listened, score=0.7228, path=`self_loop user 2086 listened song 40663 listened user 13879 listened song 29971`
- rank 5: pid=6801, type=listened, score=0.7124, path=`self_loop user 2086 listened song 19751 listened user 30 listened song 6801`
- rank 6: pid=13011, type=listened, score=0.7079, path=`self_loop user 2086 listened song 19206 listened user 19538 listened song 13011`
- rank 7: pid=24938, type=listened, score=0.7056, path=`self_loop user 2086 listened song 40663 listened user 3257 listened song 24938`
- rank 8: pid=16181, type=listened, score=0.7042, path=`self_loop user 2086 listened song 19206 listened user 3638 listened song 16181`
- rank 9: pid=15334, type=listened, score=0.6870, path=`self_loop user 2086 listened song 5208 listened user 21961 listened song 15334`
- rank 10: pid=12436, type=listened, score=0.6697, path=`self_loop user 2086 listened song 12453 listened user 6301 listened song 12436`

## ML-1M / PGPR / user 0

- Role: main
- Case type: qualitative explanation case
- Module: strict baseline-preserving ETD path module at alpha=1
- Unique path types: 1 -> 2
- Changed top-10 positions: 5

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

- rank 1: pid=421, type=watched, score=0.8663, path=`self_loop user 0 watched movie 968 watched user 66 watched movie 421`
- rank 2: pid=31, type=belong_to, score=0.8233, path=`self_loop user 0 watched movie 1630 belong_to category 481 belong_to movie 31`
- rank 3: pid=520, type=watched, score=0.8525, path=`self_loop user 0 watched movie 608 watched user 1943 watched movie 520`
- rank 4: pid=277, type=watched, score=0.8391, path=`self_loop user 0 watched movie 1630 watched user 43 watched movie 277`
- rank 5: pid=1031, type=watched, score=0.8337, path=`self_loop user 0 watched movie 1898 watched user 297 watched movie 1031`
- rank 6: pid=957, type=watched, score=0.8250, path=`self_loop user 0 watched movie 470 watched user 40 watched movie 957`
- rank 7: pid=466, type=watched, score=0.8221, path=`self_loop user 0 watched movie 608 watched user 29 watched movie 466`
- rank 8: pid=312, type=watched, score=0.8134, path=`self_loop user 0 watched movie 958 watched user 378 watched movie 312`
- rank 9: pid=517, type=watched, score=0.8103, path=`self_loop user 0 watched movie 608 watched user 915 watched movie 517`
- rank 10: pid=748, type=watched, score=0.8029, path=`self_loop user 0 watched movie 608 watched user 436 watched movie 748`

## ML-1M / UCPR / user 36

- Role: auxiliary
- Case type: qualitative explanation case
- Module: strict baseline-preserving ETD path module at alpha=1
- Unique path types: 1 -> 2
- Changed top-10 positions: 3

Original recommender sample:

- rank 1: pid=2359, type=watched, path=`self_loop user 36 watched movie 559 watched user 1065 watched movie 2359`
- rank 2: pid=520, type=watched, path=`self_loop user 36 watched movie 312 watched user 1759 watched movie 520`
- rank 3: pid=957, type=watched, path=`self_loop user 36 watched movie 748 watched user 629 watched movie 957`
- rank 4: pid=2476, type=watched, path=`self_loop user 36 watched movie 1000 watched user 4431 watched movie 2476`
- rank 5: pid=228, type=watched, path=`self_loop user 36 watched movie 748 watched user 4076 watched movie 228`
- rank 6: pid=1268, type=watched, path=`self_loop user 36 watched movie 559 watched user 924 watched movie 1268`
- rank 7: pid=277, type=watched, path=`self_loop user 36 watched movie 312 watched user 3576 watched movie 277`
- rank 8: pid=2190, type=watched, path=`self_loop user 36 watched movie 730 watched user 3485 watched movie 2190`
- rank 9: pid=747, type=watched, path=`self_loop user 36 watched movie 741 watched user 3485 watched movie 747`
- rank 10: pid=2128, type=watched, path=`self_loop user 36 watched movie 559 watched user 723 watched movie 2128`

Path module sample:

- rank 1: pid=2359, type=watched, score=0.7420, path=`self_loop user 36 watched movie 559 watched user 1065 watched movie 2359`
- rank 2: pid=2476, type=belong_to, score=0.7118, path=`self_loop user 36 watched movie 1708 belong_to category 11 belong_to movie 2476`
- rank 3: pid=520, type=watched, score=0.7283, path=`self_loop user 36 watched movie 312 watched user 1759 watched movie 520`
- rank 4: pid=957, type=watched, score=0.7262, path=`self_loop user 36 watched movie 748 watched user 629 watched movie 957`
- rank 5: pid=228, type=watched, score=0.6994, path=`self_loop user 36 watched movie 748 watched user 4076 watched movie 228`
- rank 6: pid=1268, type=watched, score=0.6782, path=`self_loop user 36 watched movie 559 watched user 924 watched movie 1268`
- rank 7: pid=277, type=watched, score=0.6552, path=`self_loop user 36 watched movie 312 watched user 3576 watched movie 277`
- rank 8: pid=2190, type=watched, score=0.6502, path=`self_loop user 36 watched movie 730 watched user 3485 watched movie 2190`
- rank 9: pid=747, type=watched, score=0.6247, path=`self_loop user 36 watched movie 741 watched user 3485 watched movie 747`
- rank 10: pid=2128, type=watched, score=0.6125, path=`self_loop user 36 watched movie 559 watched user 723 watched movie 2128`

