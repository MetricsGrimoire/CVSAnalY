# Useful queries for CVSAnalY2 database

## Commits

1) Total number of commits

```mysql
SELECT COUNT(id) FROM scmlog;
```

2) Number of commits per unit of time

```mysql
SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(s.id)
FROM scmlog s 
GROUP BY DATE_FORMAT(s.date, '%Y%m');
```

3) Aggregated number of commits up to time

```mysql
SELECT g.myyear, g.mymonth, g.numcommits, (@sumacu:=@sumacu+g.numcommits) aggregated_numcommits
FROM 
  (SELECT @sumacu:=0) r,
  (
    SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(s.id) numcommits
    FROM scmlog s
    GROUP BY DATE_FORMAT(s.date, '%Y%m')
  ) g;
```

4) Maximum and minimum number of commits per unit of time

```mysql
SELECT MAX(g.numcommits), MIN(g.numcommits)
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(s.id) numcommits
  FROM scmlog s
  GROUP BY DATE_FORMAT(s.date, '%Y%m') 
) g;
```

5) Mean and median of commits per unit of time

```mysql
SELECT AVG(g.numcommits)
FROM ( 
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(s.id) numcommits
  FROM scmlog s
  GROUP BY DATE_FORMAT(s.date, '%Y%m') 
) g;
```

## Actions

6) Total number of actions

```mysql
SELECT COUNT(a.id)
FROM actions a;
```

7) Total number of actions per type

```mysql
SELECT type, COUNT(a.id)
FROM actions a
GROUP BY type
```

8) Number of actions per unit of time

```mysql
SELECT MIN(g.numactions), MAX(g.numactions)
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, a.type, COUNT(a.id) numactions
  FROM scmlog s, actions a
  WHERE s.id = a.commit_id
  GROUP BY DATE_FORMAT(s.date, '%Y%m'), a.type
) g;
```

9) Aggregated number of actions up to time

```mysql
SELECT g.myyear, g.mymonth, g.numactions, (@sumacu:=@sumacu+g.numactions) aggregated_numactions
FROM 
  (SELECT @sumacu:=0) r,
  (
    SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
    FROM scmlog s, actions a where s.id = a.commit_id
    GROUP BY DATE_FORMAT(s.date, '%Y%m')
  ) g;
```

10) Maximum and minimum number of actions per unit of time

```mysql
SELECT MAX(g.numactions), MIN(g.numactions)
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
  FROM scmlog s, actions a
  WHERE s.id = a.commit_id
  GROUP BY DATE_FORMAT(s.date, '%Y%m')
) g;
```

11) Mean and median of actions per unit of time

```mysql
SELECT AVG(g.numactions)
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
  FROM scmlog s, actions a 
  WHERE s.id = a.commit_id 
  GROUP BY DATE_FORMAT(s.date, '%Y%m')
) g;
```

12) Number of actions per unit of time and per type

```mysql
SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, a.type, COUNT(a.id)
FROM scmlog s, actions a
WHERE s.id = a.commit_id
GROUP BY DATE_FORMAT(s.date, '%Y%m'), a.type;
```

13) Aggregated number of actions per type and up to time

```mysql
SELECT g.type, g.myyear, g.mymonth, g.numactions, IF(myyear IS NULL, @sumacu:=0, @sumacu:=@sumacu+g.numactions) aggregated_numactions
FROM 
  (SELECT @sumacu:=0) r,
  (
    SELECT type, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
    FROM scmlog s, actions a
    WHERE s.id = a.commit_id
    GROUP BY type, DATE_FORMAT(s.date, '%Y'), DATE_FORMAT(s.date, '%m') WITH ROLLUP
  ) g
WHERE (g.myyear IS NULL OR g.mymonth IS NOT NULL) AND g.type IS NOT NULL;
```

14) Maximum and minimum number of actions per unit of time and per type

```mysql
SELECT MIN(g.numactions), MAX(g.numactions)
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, a.type, COUNT(a.id) numactions
  FROM scmlog s, actions a
  WHERE s.id = a.commit_id
  GROUP BY DATE_FORMAT(s.date, '%Y%m'), a.type
) g;
```

15) Mean and median of actions per unit of type and per type

```mysql
SELECT AVG(g.numactions)
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, a.type, COUNT(a.id) numactions
  FROM scmlog s, actions a
  WHERE s.id = a.commit_id
  GROUP BY DATE_FORMAT(s.date, '%Y%m'), a.type
) g;
```

## Files

16) Total number of files in the whole history of the project

```mysql
SELECT COUNT(DISTINCT a.file_id)
FROM actions a;
```

17) Number of files per unit of time

```mysql
SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(DISTINCT a.file_id)
FROM scmlog s, actions a
WHERE s.id = a.commit_id
GROUP BY DATE_FORMAT(s.date, '%Y%m');
```

18) Aggregated number of files up to time

```mysql
SELECT g.myyear, g.mymonth, g.numfiles, IF(myyear IS NULL, @sumacu:=0, @sumacu:=@sumacu+g.numfiles) aggregated_numfiles
FROM 
  (SELECT @sumacu:=0) r,
  (
    SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(DISTINCT a.file_id) numfiles
    FROM scmlog s, actions a
    WHERE s.id = a.commit_id
    GROUP BY DATE_FORMAT(s.date, '%Y%m')
  ) g;
```

19) Maximum and minimum number of active (not deleted) files

```mysql
SELECT MAX(g.numfiles), MIN(g.numfiles)
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(DISTINCT a.file_id) numfiles
  FROM scmlog s, actions a
  WHERE 
    s.id = a.commit_id
    AND a.file_id NOT IN (SELECT DISTINCT file_id FROM actions WHERE type = 'D')
  GROUP BY DATE_FORMAT(s.date, '%Y%m')
) g;
```

20) Mean and median of active (not deleted) files per unit of time

```mysql
SELECT AVG(g.numfiles)
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(DISTINCT a.file_id) numfiles
  FROM scmlog s, actions a
  WHERE 
    s.id = a.commit_id
    AND a.file_id NOT IN (SELECT DISTINCT file_id FROM actions WHERE type = 'D')
  GROUP BY DATE_FORMAT(s.date, '%Y%m')
) g;
```

21) Total number of files per type in the whole history of the project

```mysql
SELECT a.type, COUNT(DISTINCT a.file_id) numfiles
FROM actions a
GROUP BY a.type;
```

22) Number of files per type and per unit of time

```mysql
SELECT a.type, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(DISTINCT a.file_id) numfiles
FROM scmlog s, actions a
WHERE s.id = a.commit_id
GROUP BY a.type, DATE_FORMAT(s.date, '%Y%m');
```

23) Aggregated number of files per type up to time

```mysql
SELECT g.type, g.myyear, g.mymonth, g.numfiles, IF(myyear IS NULL, @sumacu:=0, @sumacu:=@sumacu+g.numfiles) aggregated_numfiles
FROM 
  (SELECT @sumacu:=0) r,
  (
    SELECT type, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(DISTINCT a.file_id) numfiles
    FROM scmlog s, actions a
    WHERE s.id = a.commit_id
    GROUP BY type, DATE_FORMAT(s.date, '%Y'), DATE_FORMAT(s.date, '%m') WITH ROLLUP
  ) g
WHERE (g.myyear IS NULL OR g.mymonth IS NOT NULL) AND g.type IS NOT NULL;
```

24) Maximum and minimum number of active (not deleted) files per type

```mysql
SELECT g.type, MAX(g.numfiles), MIN(g.numfiles)
FROM (
  SELECT a.type, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(DISTINCT a.file_id) numfiles
  FROM scmlog s, actions a
  WHERE 
    s.id = a.commit_id
    AND a.file_id NOT IN (SELECT DISTINCT file_id FROM actions WHERE type = 'D')
  GROUP BY a.type, DATE_FORMAT(s.date, '%Y%m')
)g
GROUP BY g.type;
```

25) Mean and median of active (not deleted) files per type

```mysql
SELECT g.type, AVG(g.numfiles)
FROM (
  SELECT a.type, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(DISTINCT a.file_id) numfiles
  FROM scmlog s, actions a
  WHERE 
    s.id = a.commit_id
    AND a.file_id NOT IN (SELECT DISTINCT file_id FROM actions WHERE type = 'D')
    GROUP BY a.type, DATE_FORMAT(s.date, '%Y%m')
) g
GROUP BY g.type;
```

26) Number of files per language (extension `Metrics` needed)

```mysql
SELECT m.lang, COUNT(DISTINCT m.file_id) numfiles
FROM metrics m
GROUP BY m.lang;
```

27) Accumulated number of files per language (extension `Metrics` needed)

```mysql
SELECT g.lang, g.numfiles, (@sumacu:=@sumacu+g.numfiles) aggregated_numfiles
FROM 
  (SELECT @sumacu:=0) r,
  (
    SELECT m.lang, COUNT(DISTINCT m.file_id) numfiles
    FROM metrics m
    GROUP BY m.lang
  ) g;
```

## Commits - Files

28) Total number of commits per file

```mysql
SELECT f.id, COUNT(s.id)
FROM scmlog s, actions a, files f
WHERE 
  s.id = a.commit_id
  AND a.file_id = f.id
GROUP BY f.id;
```

29) Number of commits per file and per unit of time

```mysql
SELECT f.id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(s.id)
FROM scmlog s, actions a, files f
WHERE 
  s.id = a.commit_id
  AND a.file_id = f.id
GROUP BY f.id, DATE_FORMAT(s.date, '%Y%m');
```

30) Accumulated number of commits per file up to time

```mysql
SELECT g.id, g.myyear, g.mymonth, g.numcommits, IF(myyear IS NULL, @sumacu:=0, @sumacu:=@sumacu+g.numcommits) aggregated_numfiles
FROM 
  (SELECT @sumacu:=0) r,
  (
    SELECT f.id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(s.id) numcommits
    FROM scmlog s, actions a, files f
    WHERE 
      s.id = a.commit_id
      AND a.file_id = f.id
    GROUP BY f.id, DATE_FORMAT(s.date, '%Y'), DATE_FORMAT(s.date, '%m') WITH ROLLUP
  ) g
WHERE (g.myyear IS NULL OR g.mymonth IS NOT NULL) AND g.id IS NOT NULL;
```

31) Maximum and minimum number of commits over files per unit of time

```mysql
SELECT g.id, MAX(numcommits), MIN(numcommits)
FROM (
  SELECT f.id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(s.id) numcommits
  FROM scmlog s, actions a, files f
  WHERE 
    s.id = a.commit_id
    AND a.file_id = f.id
  GROUP BY f.id, DATE_FORMAT(s.date, '%Y%m')
) g 
GROUP BY g.id;
```

32) Mean and median of commits over files per unit of time

```mysql
SELECT g.id, AVG(numcommits)
FROM (
  SELECT f.id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(s.id) numcommits
  FROM scmlog s, actions a, files f
  WHERE s.id = a.commit_id AND a.file_id = f.id
  GROUP BY f.id, DATE_FORMAT(s.date, '%Y%m')
) g
GROUP BY g.id;
```

## Actions - Files

33) Total number of actions per file

```mysql
SELECT f.id, COUNT(a.id) numactions
FROM scmlog s, actions a, files f
WHERE s.id = a.commit_id AND a.file_id = f.id
GROUP BY f.id;
```

34) Number of actions per file and per unit of time

```mysql
SELECT f.id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
FROM scmlog s, actions a, files f
WHERE 
  s.id = a.commit_id
  AND a.file_id = f.id
GROUP BY f.id, DATE_FORMAT(s.date, '%Y%m');
```

35) Accumulated number of actions per file up to time

```mysql
SELECT g.id, g.myyear, g.mymonth, g.numactions, IF(myyear IS NULL, @sumacu:=0, @sumacu:=@sumacu+g.numactions) aggregated_numfiles
FROM 
  (SELECT @sumacu:=0) r,
  (
    SELECT f.id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
    FROM scmlog s, actions a, files f
    WHERE 
      s.id = a.commit_id
      AND a.file_id = f.id 
    GROUP BY f.id, DATE_FORMAT(s.date, '%Y'), DATE_FORMAT(s.date, '%m') WITH ROLLUP
  ) g
WHERE (g.myyear IS NULL OR g.mymonth IS NOT NULL) AND g.id IS NOT NULL;
```

36) Maximum and minimum number of actions over files per unit of time

```mysql
SELECT g.id, MAX(numactions), MIN(numactions)
FROM (
  SELECT f.id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
  FROM scmlog s, actions a, files f
  WHERE 
    s.id = a.commit_id
    AND a.file_id = f.id
  GROUP BY f.id, DATE_FORMAT(s.date, '%Y%m')
) g
GROUP BY g.id;
```

37) Mean and median of actions over files per unit of time

```mysql
SELECT g.id, AVG(numactions)
FROM (
  SELECT f.id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
  FROM scmlog s, actions a, files f
  WHERE 
    s.id = a.commit_id 
    AND a.file_id = f.id
  GROUP BY f.id, DATE_FORMAT(s.date, '%Y%m')
) g
GROUP BY g.id;
```

38) Total number of actions per type and per file

```mysql
SELECT f.id, a.type, COUNT(a.id) numactions
FROM scmlog s, actions a, files f
WHERE s.id = a.commit_id AND a.file_id = f.id
GROUP BY f.id, a.type;
```

39) Number of actions per type, file and unit of time

```mysql
SELECT f.id, a.type, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
FROM scmlog s, actions a, files f
WHERE s.id = a.commit_id AND a.file_id = f.id
GROUP BY f.id, a.type, DATE_FORMAT(s.date, '%Y%m');
```

40) Accumulated number of actions per type, file up to time

```mysql
SELECT g.id, g.type, g.myyear, g.mymonth, g.numactions, IF(myyear IS NULL, @sumacu:=0, @sumacu:=@sumacu+g.numactions) aggregated_numfiles
FROM 
  (SELECT @sumacu:=0) r,
  (
    SELECT f.id, a.type, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
    FROM scmlog s, actions a, files f
    WHERE s.id = a.commit_id AND a.file_id = f.id
    GROUP BY f.id, a.type, DATE_FORMAT(s.date, '%Y'), DATE_FORMAT(s.date, '%m') WITH ROLLUP
  ) g
WHERE (g.type IS NULL OR g.myyear IS NULL OR g.mymonth IS NOT NULL) AND g.id IS NOT NULL;
```

41) Maximum and minimum number of actions over files per type and per unit of time

```mysql
SELECT g.id, g.type, MAX(numactions), MIN(numactions)
FROM (
  SELECT f.id, a.type, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
  FROM scmlog s, actions a, files f
  WHERE s.id = a.commit_id AND a.file_id = f.id
  GROUP BY f.id, a.type, DATE_FORMAT(s.date, '%Y%m')
) g
GROUP BY g.id;
```

42) Mean and median of actions over files per type and per unit of time

```mysql
SELECT g.id, g.type, AVG(numactions)
FROM (
  SELECT f.id, a.type, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, COUNT(a.id) numactions
  FROM scmlog s, actions a, files f
  WHERE 
    s.id = a.commit_id
    AND a.file_id = f.id
  GROUP BY f.id, a.type, DATE_FORMAT(s.date, '%Y%m')
) g
GROUP BY g.id;
```

## Size variables (extension `Metrics` needed)

43) Total LOC/SLOC of the project in the whole history of the project

```mysql
SELECT SUM(m.loc) FROM metrics m;
```

```mysql
SELECT SUM(m.sloc) FROM metrics m;
```

44) Project size in LOC / SLOC per unit of time

```mysql
SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, SUM(m.loc) result
FROM metrics m, scmlog s 
WHERE s.id = m.commit_id
GROUP BY DATE_FORMAT(s.date, '%Y%m');
```

```mysql
SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, SUM(m.sloc) result
FROM metrics m, scmlog s 
WHERE s.id = m.commit_id
GROUP BY DATE_FORMAT(s.date, '%Y%m');
```

45) Maximum and minimum size in LOC / SLOC per unit of time

```mysql
SELECT MAX(g.loc), MIN(g.loc) 
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, SUM(m.loc) loc
  FROM metrics m, scmlog s 
  WHERE s.id = m.commit_id
  GROUP BY DATE_FORMAT(s.date, '%Y%m')
) g;
```

```mysql
SELECT MAX(g.sloc), MIN(g.sloc) 
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, SUM(m.sloc) sloc
  FROM metrics m, scmlog s 
  WHERE s.id = m.commit_id
  GROUP BY DATE_FORMAT(s.date, '%Y%m')
) g;
```

46) Mean and median of size in LOC / SLOC per unit of time

```mysql
SELECT AVG(g.loc) 
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, SUM(m.loc) loc
  FROM metrics m, scmlog s 
  WHERE s.id = m.commit_id
  GROUP BY DATE_FORMAT(s.date, '%Y%m')
) g;
```

```mysql
SELECT AVG(g.sloc) 
FROM (
  SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, SUM(m.sloc) sloc
  FROM metrics m, scmlog s 
  WHERE s.id = m.commit_id
  GROUP BY DATE_FORMAT(s.date, '%Y%m')
) g;
```

## Files - Size variables (extension `Metrics` needed)

47) Maximum and minimum size in LOC / SLOC per file

```mysql
SELECT SUM(min_loc), SUM(max_loc) 
FROM (
  SELECT m.file_id, MIN(m.loc) min_loc, MAX(m.loc) max_loc
  FROM metrics m, scmlog s 
  WHERE s.id = m.commit_id
  GROUP BY m.file_id
) g;
```

```mysql
SELECT SUM(min_sloc), SUM(max_sloc) 
FROM (
  SELECT m.file_id, MIN(m.sloc) min_sloc, MAX(m.sloc) max_sloc
  FROM metrics m, scmlog s 
  WHERE s.id = m.commit_id
  GROUP BY m.file_id
) g;
```

48) Mean and median of size in LOC / SLOC per file

```mysql
SELECT SUM(avg_loc) 
FROM (
  SELECT m.file_id, AVG(m.loc) avg_loc 
  FROM metrics m, scmlog s
  WHERE s.id = m.commit_id 
  GROUP BY m.file_id
) g;
```

```mysql
SELECT SUM(avg_sloc) 
FROM (
  SELECT m.file_id, AVG(m.sloc) avg_sloc 
  FROM metrics m, scmlog s
  WHERE s.id = m.commit_id 
  GROUP BY m.file_id
) g;
```

49) Maximum and minimum file sizes in LOC / SLOC per unit of time

```mysql
SELECT g.file_id, SUM(g.max_loc), SUM(g.min_loc) 
FROM (
  SELECT m.file_id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, MIN(m.loc) min_loc, MAX(m.loc) max_loc
  FROM metrics m, scmlog s 
  WHERE s.id = m.commit_id 
  GROUP BY m.file_id, DATE_FORMAT(s.date, '%Y%m')
) g 
GROUP BY g.file_id;
```

```mysql
SELECT g.file_id, SUM(g.max_sloc), SUM(g.min_sloc) 
FROM (
  SELECT m.file_id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, MIN(m.sloc) min_sloc, MAX(m.sloc) max_sloc
  FROM metrics m, scmlog s 
  WHERE s.id = m.commit_id
  GROUP BY m.file_id, DATE_FORMAT(s.date, '%Y%m')
) g 
GROUP BY g.file_id;
```

50) Mean and median of file sizes in LOC / SLOC per unit of time

```mysql
SELECT g.file_id, SUM(g.avg_loc) 
FROM (
  SELECT m.file_id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, AVG(m.loc) avg_loc 
  FROM metrics m, scmlog s 
  WHERE s.id = m.commit_id
  GROUP BY m.file_id, DATE_FORMAT(s.date, '%Y%m')
) g 
GROUP BY g.file_id;
```

```mysql
SELECT g.file_id, SUM(g.avg_sloc) 
FROM (
  SELECT m.file_id, DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, AVG(m.sloc) avg_sloc 
  FROM metrics m, scmlog s 
  WHERE s.id = m.commit_id
  GROUP BY m.file_id, DATE_FORMAT(s.date, '%Y%m')
) g 
GROUP BY g.file_id;
```

## Committers - Authors

51) Total number of committers / authors

```mysql
SELECT IF(COUNT(DISTINCT s.author_id) = 0, 0, COUNT(DISTINCT s.committer_id) / COUNT(DISTINCT s.author_id))
FROM scmlog s;
```

52) Number of distinct committers / authors per unit of time

```mysql
SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, IF(COUNT(DISTINCT s.author_id) = 0, 0, COUNT(DISTINCT s.committer_id) / COUNT(DISTINCT s.author_id)) committer_author
FROM scmlog s
GROUP BY DATE_FORMAT(s.date, '%Y%m');
```

53) Aggregated number of distinct committers / authors up to time

```mysql
SELECT g.myyear, g.mymonth, g.committer_author, IF(myyear IS NULL, @sumacu:=0, @sumacu:=@sumacu+g.committer_author ) aggregated_committer_author
FROM 
  (SELECT @sumacu:=0) r,
  (
    SELECT DATE_FORMAT(s.date, '%Y') myyear, DATE_FORMAT(s.date, '%m') mymonth, IF(COUNT(DISTINCT s.author_id) = 0, 0, COUNT(DISTINCT s.committer_id) / COUNT(DISTINCT s.author_id)) committer_author
    FROM scmlog s
    GROUP BY DATE_FORMAT(s.date, '%Y%m')
  ) g;
```
