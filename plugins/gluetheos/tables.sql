create table sourcefiles (
	filename	varchar(255) not null,
	revision	varchar(16) not null,
	rev_date	date not null,
	rev_time 	time not null,
	content		BLOB,
	sha1		char(40) not null,
	nilsimsa	char(64) not null,
	primary key (filename, revision)
);