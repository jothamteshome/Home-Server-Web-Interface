CREATE TABLE IF NOT EXISTS `shortContentData` (
`content_id`            BIGINT(64)     NOT NULL                     COMMENT 'The id to search for content with',
`content_name`          varbinary(256) NOT NULL         		    COMMENT 'The name of the content',
`content_type`          varbinary(16)  NOT NULL                     COMMENT 'Whether content is image or video',
`content_loc`           varbinary(512) NOT NULL                     COMMENT 'Location of the content',
`search_dir_name`       varbinary(256) NOT NULL                     COMMENT 'Name of outer-most ancestor directory',
`source_dir_name`       varbinary(256) NOT NULL                     COMMENT 'Name of parent directory',
`content_style`         varbinary(128) NOT NULL                     COMMENT 'Finalized Meme, Premade meme, or general shortform content',
`has_caption`           INT(1)         NOT NULL                     COMMENT 'Determines whether caption exists',
`caption_loc`           varbinary(512) NULL                         COMMENT 'Location of caption if it exists',
`prev_content_id`       BIGINT(64)                                  COMMENT 'The id to search for prev content with',
`next_content_id`       BIGINT(64)                                  COMMENT 'The id to search for next content with',
PRIMARY KEY (`content_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains sites shortform content";