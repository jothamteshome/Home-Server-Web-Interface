CREATE TABLE IF NOT EXISTS `comicData` (
`comic_id`          BIGINT(64)     NOT NULL                   COMMENT 'The search for a comic with',
`comic_name`        varbinary(256) NOT NULL UNIQUE    		  COMMENT 'The name of the comic',
`comic_genre`       varbinary(64)  NOT NULL                   COMMENT 'Name of outer-most ancestor directory',
`comic_franchise`   varbinary(128) NOT NULL                   COMMENT 'The name of the franchise comic belongs to',
`has_chapters`      INT(1)         NOT NULL                   COMMENT 'Boolean value saying whether this has multiple parts',
`comic_series`      varbinary(256) NULL                       COMMENT 'Name of series if it exists',
`comic_author`      varbinary(128) NOT NULL                   COMMENT 'The author of this comic',
`comic_loc`         varbinary(512) NOT NULL                   COMMENT 'The source location',
PRIMARY KEY (`comic_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site comic data";