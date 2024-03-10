CREATE TABLE IF NOT EXISTS `uploadSearchDirectories` (
`section_name`              varbinary(64)     NOT NULL     		          COMMENT 'The name of the upload search directory',
`section_directory`         varbinary(512)    NOT NULL                    COMMENT 'The search directory location to upload to',
`section_content_style`     varbinary(128)    NOT NULL                    COMMENT 'Finalized Meme, Premade meme, or general shortform content',
`separate_uploaded_content` INT(1)            NOT NULL                    COMMENT 'Boolean value saying whether uploaded content should be separate from other content',
`separate_image_video`      INT(1)            NOT NULL                    COMMENT 'Boolean value saying whether image and video content should be split',
`search_dir_storage`        INT(1)            NOT NULL                    COMMENT 'Boolean value denoting whether content should be stored directly in search dir',
`caption_required`          INT(1)            NOT NULL                    COMMENT 'Boolean value denoting whether a caption is required for content uploaded to search dir',
PRIMARY KEY (`section_name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains server upload directory information";