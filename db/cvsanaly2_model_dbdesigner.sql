-- ------------------------------------------------------------
-- Path where is localizate the application
-- ------------------------------------------------------------

CREATE TABLE repositories (
  id INTEGER(11) NOT NULL,
  uri VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(30) NOT NULL,
  PRIMARY KEY(id)
);

-- ------------------------------------------------------------
-- General information about the tools
-- ------------------------------------------------------------

CREATE TABLE tool_info (
  project VARCHAR(255) NOT NULL,
  tool VARCHAR(255) NOT NULL,
  tool_version VARCHAR(255) NOT NULL,
  datasource VARCHAR(255) NOT NULL,
  datasource_info TEXT NOT NULL,
  creation_date DATETIME NOT NULL,
  last_modification DATETIME NOT NULL,
  PRIMARY KEY(project)
);

-- ------------------------------------------------------------
-- List of the files has been commited
-- ------------------------------------------------------------

CREATE TABLE tree (
  id INTEGER(11) NOT NULL,
  parent INTEGER(11) NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  deleted TINYINT(1) UNSIGNED NOT NULL,
  PRIMARY KEY(id)
);

-- ------------------------------------------------------------
-- List of files path
-- ------------------------------------------------------------

CREATE TABLE file_paths (
  id INTEGER(11) NOT NULL,
  file_id INTEGER(11) NOT NULL,
  path MEDIUMTEXT NOT NULL,
  PRIMARY KEY(id),
  INDEX file_id(file_id),
  FOREIGN KEY(file_id)
    REFERENCES tree(id)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
);

-- ------------------------------------------------------------
-- General information about the commits
-- ------------------------------------------------------------

CREATE TABLE scmlog (
  id INTEGER(11) NOT NULL,
  rev MEDIUMTEXT NOT NULL,
  committer VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  date DATETIME NOT NULL,
  lines_added INTEGER(11) NOT NULL,
  lines_removed INTEGER(11) NOT NULL,
  message TEXT NOT NULL,
  composed_rev TINYINT(1) NOT NULL,
  repository_id INTEGER(11) NOT NULL,
  PRIMARY KEY(id),
  INDEX repository_id(repository_id),
  FOREIGN KEY(repository_id)
    REFERENCES repositories(id)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
);

-- ------------------------------------------------------------
-- Action doing in the commited file 
-- ------------------------------------------------------------

CREATE TABLE actions (
  id INTEGER(11) NOT NULL,
  file_id INTEGER(11) NOT NULL,
  type VARCHAR(1) NOT NULL,
  PRIMARY KEY(id),
  FOREIGN KEY(id)
    REFERENCES scmlog(id)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION,
  FOREIGN KEY(file_id)
    REFERENCES tree(id)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
);

-- ------------------------------------------------------------
-- Indicators for file
-- ------------------------------------------------------------

CREATE TABLE metrics (
  id INTEGER(11) NOT NULL,
  file_id INTEGER(11) NOT NULL,
  commit_id INTEGER(11) NOT NULL,
  lang TINYTEXT NOT NULL,
  sloc INTEGER(11) NOT NULL,
  loc INTEGER(11) NOT NULL,
  ncomment INTEGER(11) NOT NULL,
  lcomment INTEGER(11) NOT NULL,
  lblank INTEGER(11) NOT NULL,
  nfunctions INTEGER(11) NOT NULL,
  mccabe_min INTEGER(11) NOT NULL,
  mccabe_max INTEGER(11) NOT NULL,
  mccabe_sum INTEGER(11) NOT NULL,
  mccabe_mean INTEGER(11) NOT NULL,
  mccabe_median INTEGER(11) NOT NULL,
  halstead_length INTEGER(11) NOT NULL,
  halstead_vol INTEGER(11) NOT NULL,
  halstead_level DOUBLE NOT NULL,
  halstead_md INTEGER(11) NOT NULL,
  PRIMARY KEY(id),
  INDEX file_id(file_id),
  INDEX commit_id(commit_id),
  FOREIGN KEY(file_id)
    REFERENCES tree(id)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION,
  FOREIGN KEY(commit_id)
    REFERENCES scmlog(id)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
);


