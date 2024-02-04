CREATE TABLE IF NOT EXISTS `showData` (
`show_id`          BIGINT(64)     NOT NULL                   COMMENT 'The id to search episode with',
`show_episode`     varbinary(256) NOT NULL UNIQUE    		 COMMENT 'The name of the episode',
`show_name`        varbinary(128) NOT NULL                   COMMENT 'The name of the show series',
`show_ep_num`      varbinary(128) NOT NULL                   COMMENT 'The season-episode data',
`show_search_dir`  varbinary(256) NOT NULL                   COMMENT 'The base directory this show came from',
`show_thumb`       varbinary(512) NOT NULL                   COMMENT 'The source of the thumbnail',
`show_loc`         varbinary(512) NOT NULL                   COMMENT 'The source location',
PRIMARY KEY (`show_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site show data";