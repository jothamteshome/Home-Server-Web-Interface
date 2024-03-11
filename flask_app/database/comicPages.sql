CREATE TABLE IF NOT EXISTS `comicPages` (
`comic_page_id`     INT(11)        NOT NULL AUTO_INCREMENT    COMMENT 'The id for a specific comic page',
`comic_id`          BIGINT(64)     NOT NULL                   COMMENT 'The id of a comic',
`comic_page_name`   varbinary(128) NOT NULL         		  COMMENT 'The name of a comic page',
PRIMARY KEY (`comic_page_id`),
FOREIGN KEY (comic_id) REFERENCES comicData(comic_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site comic page data";